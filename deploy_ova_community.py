#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,too-few-public-methods

import atexit
import binascii
import io
import json
import logging
import os
import re
import shlex
import signal
import ssl
import subprocess
import sys
import tarfile
from argparse import ArgumentParser
from distutils import spawn
from getpass import getpass
from threading import Thread
from time import sleep, time
from traceback import print_exc
from urlparse import urlparse

import psutil
import requests
from pyVim import connect
from pyVmomi import vim, vmodl  # pylint: disable=no-name-in-module
from requests.packages.urllib3.exceptions import InsecureRequestWarning

__title__ = 'OVA deployer'
__version__ = '1.6.1'
__author__ = 'Brian Ma'

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# MIN_PYTHON = (2, 7, 9)
# ssl._create_unverified_context appears at 2.7.9
# if sys.version_info < MIN_PYTHON or sys.version_info[0] != 2:
#     sys.exit("Python 2 ONLY! And minimal require is %s.%s.%s." % MIN_PYTHON)
# ssl._create_default_https_context = ssl._create_unverified_context  # pylint: disable=protected-access

sig_triggered = False  # pylint: disable=invalid-name


def set_sig_flag():
    global sig_triggered  # pylint: disable=global-statement,invalid-name
    sig_triggered = True


def sig_handler(signo, dummy_stack_frame):
    set_sig_flag()
    sig_dict = {
        getattr(signal, n): n
        for n in dir(signal) if n.startswith('SIG')
    }
    print ''
    _LOGGER.info('Process recieved signal: %s', sig_dict[signo])
    this_proc = psutil.Process(os.getpid())
    for child in this_proc.children(True):
        child.kill()
    raise KeyboardInterrupt()


signal.signal(signal.SIGTERM, sig_handler)
signal.signal(signal.SIGHUP, sig_handler)

_LOGGER = logging.getLogger('')
_LOGGER_HANDLER = logging.StreamHandler()
_LOGGER.addHandler(_LOGGER_HANDLER)
_LOGGER_HANDLER.setFormatter(logging.Formatter('[%(levelname)s]: %(message)s'))
_LOGGER.setLevel(logging.INFO)

GZIP_BIN = 'pigz'
if not spawn.find_executable(GZIP_BIN):
    GZIP_BIN = 'gzip'

vcenter_consts = None


class VCenterConstants(object):

    def __init__(self, site, pwd):
        self.PORT = 443

        self.HOST = '10.200.208.5'
        self.USER_PREFIX = 'APP\\'
        self.DATA_CENTER = 'Appliance Solutions'
        self.DATA_STORE = 'SC8K_LUN03_ALL_WanTw'
        self.CLUSTER = 'AS_NBVA_6.0'
        self.RES_POOL = 'AS_Saipu_6.0'
        self.VM_FOLDER_PARENT = 'AS_Saipu_6.0'

        self.SEC_C = 71
        self.NETMASK = '255.255.252.0'
        self.GATEWAY = '10.200.68.1'

        self.SEARCH_DOMAIN = 'cdc.veritas.com'
        self.DNS = '172.16.8.32'
        self.AD_POOL_PREFIX = 'dp_adv_'
        self.AD_STU_PREFIX = 'stu_adv_'
        self.MSDP_POOL_PREFIX = 'dp_disk_'
        self.MSDP_STU_PREFIX = 'stu_disk_'

        # name: (ip start, ip end, vm folder),
        self.TEAM_INFO = {
            "zhongxiu_li": (66, 75, "zhongxiu"),
            "allen_hou": (76, 85, "allenh"),
            "huide_huang": (86, 95, "Richard Huang"),
            "brian_ma": (97, 104, "brian_ma"),
            "jing_li": (106, 115, "JingLi"),
            "jeff_cai": (116, 125, "Jeff Cai"),
            "yiqun_yue": (126, 135, "Yiqun"),
            "xi_wang": (136, 145, "WangXi"),
            "hao_zhang": (146, 155, "Zhang Hao"),
            "bingo_xing": (156, 165, "Bingo"),
            "chao_geng": (166, 175, "Chao Geng"),
            "eric_sun": (176, 185, "EricSun"),
            "tong_jiang": (186, 195, "Tong Jiang")
        }

        if site == 'vc65':
            self.HOST = 'vc65.cdc.veritas.com'
            self.PORT = 443
            self.USER_PREFIX = 'community\\'
            self.DATA_CENTER = 'BJG'
            self.DATA_STORE = 'NBVA'
            self.CLUSTER = 'AS'
            self.RES_POOL = 'NBVA'
            self.VM_FOLDER_PARENT = 'NBVA'
            self.SEC_C = 213
            self.NETMASK = '255.255.240.0'
            self.GATEWAY = '10.200.208.1'
            self.TEAM_INFO['brian.ma'] = (97, 104, "brian.ma")
        self.user_pwd = pwd
        self.IP_PREFIX = '10.200.%d.' % self.SEC_C
        self.HOSTNAME_PREFIX = 'n%d-h' % self.SEC_C


def roundup(integer, stride):
    return integer if integer % stride == 0 else integer + stride - integer % stride


class _OvaArtifact(object):
    _JENKINS_URL = 'http://jenkins-appliance.engba.veritas.com/job/nba_main_createova/lastStableBuild/injectedEnvVars/api/json'
    _OVA_URL_PATTERN = 'http://artifactory-appliance.engba.veritas.com/artifactory/release/nba/main/%s/nba-%s.ova'
    _NBA_TAG = 'NBA_BUILDTAG'
    _NBVA_TAG = 'BUILDTAG'

    def __init__(self, ova_uri, edition='robo'):
        self.nba_tag = 'custom'
        self.nbva_tag = self.nba_tag
        self.ova_uri = ''

        if ova_uri == 'LATEST':
            self._get_latest(edition)
        else:
            self.ova_uri = ova_uri
        self.checker = _OvaChecker(self.ova_uri)

    def _get_latest(self, edition):
        resp = requests.get(self._JENKINS_URL)
        build_env = json.loads(resp.content)['envMap']
        self.nba_tag = build_env[self._NBA_TAG]
        self.nbva_tag = build_env[self._NBVA_TAG]
        self.ova_uri = self._OVA_URL_PATTERN % (self.nba_tag, self.nbva_tag)
        if edition == 'no_w':
            self.ova_uri = self.ova_uri.replace('.ova', '-nowizard.ova')
        elif edition == 'gsi':
            self.ova_uri = self.ova_uri.replace('.ova', '-gsp.ova')
        _LOGGER.info('NBVA build tag: %s', self.nbva_tag)
        _LOGGER.debug(vars(self))


class _OvaChecker(object):

    def __init__(self, ova_uri):
        self.http = False
        self.local = False

        pieces = urlparse(ova_uri)
        if all([pieces.scheme, pieces.netloc]):  # ova on web
            resp = requests.head(ova_uri)
            _LOGGER.debug(vars(resp))
            if resp.status_code != 200:
                log_err_n_exit('Remote file not found: %s', ova_uri)
            if 'Accept-Ranges' in resp.headers and \
               resp.headers['Accept-Ranges'] == 'bytes':
                self.http = True
            else:
                log_err_n_exit('Range fetch not supported on: %s',
                               pieces.netloc)
        else:
            if not os.path.exists(ova_uri):
                log_err_n_exit('Local file not found: %s', ova_uri)
            self.local = True


class _FileInTar(object):
    NAME_BYTES = 100
    SIZE_OFFSET = 124
    SIZE_BYTES = 12
    HEX_FLAG = 0x80

    def __init__(self):
        self.start = 0L
        self.name = ''
        self.size = 0L  # payload size


class OvaOnFly(object):
    OVA_BLOCKSIZE = 512
    FETCH_HEAD_SIZE = 205000

    def __init__(self, ova_url):
        self.ova_url = ova_url
        self.ova_partial = None
        self.ovf = None
        self.menifest = None
        self.vmdk = None
        self.vmdk_stream = None
        self.requests_session = requests.session()
        self.requests_session.verify = False

    def parse(self):
        headers = {'Range': 'bytes=0-%d' % self.FETCH_HEAD_SIZE}
        response = self.requests_session.get(self.ova_url, headers=headers)
        self.ova_partial = io.BytesIO(response.content)
        self.ovf = self._next()
        second = self._next()
        if second.name.endswith('.mf'):
            self.menifest = second
            self.vmdk = self._next()
        else:
            self.vmdk = second

    def _next(self):
        file_in_tar = _FileInTar()
        file_in_tar.start = self.ova_partial.tell()
        block_data = self.ova_partial.read(self.OVA_BLOCKSIZE)
        file_in_tar.name = str(
            block_data[:_FileInTar.NAME_BYTES]).rstrip('\x00')
        # highest bit indicate hex/octal
        size_bytes = bytearray(
            block_data[_FileInTar.SIZE_OFFSET:
                       _FileInTar.SIZE_OFFSET + _FileInTar.SIZE_BYTES])
        _LOGGER.debug(
            'Size bytes: %s',
            ' '.join(re.findall('.{1,4}', binascii.hexlify(size_bytes))))
        if size_bytes[0] & _FileInTar.HEX_FLAG:
            # size in hex mode, remove the indicate flag from size bytes
            size_bytes[0] = size_bytes[0] & ~_FileInTar.HEX_FLAG
            size_str = str(size_bytes).strip('\x00')
            file_in_tar.size = long(size_str.encode('hex'), 16)
        else:
            size_str = str(size_bytes).strip('\x00')
            file_in_tar.size = long(size_str, 8)

        _LOGGER.debug(vars(file_in_tar))
        # align at 512 bytes block boundary
        aligned_boundary = roundup(file_in_tar.size, self.OVA_BLOCKSIZE)
        if self.ova_partial.tell() + aligned_boundary < len(
                self.ova_partial.getvalue()):
            self.ova_partial.seek(aligned_boundary, os.SEEK_CUR)
        return file_in_tar

    def _get_file_content(self, file_in_tar):
        if self.ova_partial:
            self.ova_partial.seek(file_in_tar.start + OvaOnFly.OVA_BLOCKSIZE,
                                  os.SEEK_SET)
            return self.ova_partial.read(file_in_tar.size)
        else:
            return None

    def get_ovf_content(self):
        return self._get_file_content(self.ovf)

    def getmembers(self):
        return [self.ovf, self.menifest, self.vmdk]

    def close(self):
        if self.ova_partial:
            self.ova_partial.close()
        self.requests_session.close()

    def get_vmdk_data(self):
        start_pos = self.vmdk.start + self.OVA_BLOCKSIZE
        headers = {
            'Range': 'bytes=%d-%d' % (start_pos, start_pos + self.vmdk.size - 1)
        }
        _LOGGER.debug(headers)
        resp = self.requests_session.get(
            self.ova_url, headers=headers, stream=True)
        # download_iter = DownloadInChunks(resp)
        # self.vmdk_stream = IterableToFileAdapter(download_iter)
        self.vmdk_stream = resp.raw
        return self.vmdk_stream


class OvaFile(object):  # pylint: disable=too-many-instance-attributes
    """A class to manipulate ova file."""

    def __init__(self, ova_uri, edition):
        ova_arti = _OvaArtifact(ova_uri, edition)
        self.ova_uri = ova_arti.ova_uri
        self.ova_file = None
        self.ova_on_fly = False

        if ova_arti.checker.http:  # ova on web
            self.ova_file = OvaOnFly(self.ova_uri)
            self.ova_file.parse()
            self.ova_on_fly = True
        else:
            self.ova_file = tarfile.open(self.ova_uri)

        ova_members = self.ova_file.getmembers()
        # 0: ovf; 1: mf; 2: disk1.vmdk.gz
        self.ovf_file = ova_members[0]
        self.vmdk1_info = ova_members[2]
        self.is_vmdk_gzipped = self.vmdk1_info.name.endswith('.gz')
        self.gzip_proc = None
        self.vmdk1_fobj = None
        self.tmp_fifo = 'fifo_%d' % os.getpid()

    def get_ovf_content(self):
        if self.ova_on_fly:
            return self.ova_file.get_ovf_content()
        else:
            return self.ova_file.extractfile(self.ovf_file).read()

    def get_vmdk1_obj(self):
        if not self.vmdk1_fobj:
            if self.ova_on_fly:
                self.vmdk1_fobj = self.ova_file.get_vmdk_data()
            else:
                vmdk1 = self.ova_file.extractfile(self.vmdk1_info)
                self.vmdk1_fobj = vmdk1
                if self.is_vmdk_gzipped:
                    os.mkfifo(self.tmp_fifo)
                    cmd = 'tar --extract --to-stdout -f %s %s | %s --stdout -d > %s' % \
                          (self.ova_uri, self.get_vmdk1_name(), GZIP_BIN, self.tmp_fifo)
                    _LOGGER.info(cmd)
                    self.gzip_proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, shell=True)
                    self.vmdk1_fobj = io.open(self.tmp_fifo, 'rb')
                else:
                    self.vmdk1_fobj = vmdk1
        return self.vmdk1_fobj

    def get_vmdk1_name(self):
        return self.vmdk1_info.name

    def get_vmdk1_size(self):
        return self.vmdk1_info.size

    def close(self):
        if self.gzip_proc and not self.gzip_proc.returncode:
            self.gzip_proc.terminate()
            self.gzip_proc = None
        if self.vmdk1_fobj:
            self.vmdk1_fobj.close()
            self.vmdk1_fobj = None
            # os.remove(self.tmp_fifo)
        if self.ova_file:
            self.ova_file.close()
            self.ova_file = None


class UploadInChunks(object):

    def __init__(self, fileobj, filesize, chunksize=1 << 20):
        self.fileobj = fileobj
        self.chunksize = chunksize
        self.totalsize = filesize
        self.readsofar = 0

    def __iter__(self):
        while True:
            data = self.fileobj.read(self.chunksize)
            if not data:
                sys.stderr.write("\n")
                break
            self.readsofar += len(data)
            self._show_progress()
            yield data

    def __len__(self):
        return self.totalsize

    def _show_progress(self):
        progress = int(round(self.readsofar * 100 / self.totalsize, ndigits=2))

        completed = "#" * int(progress)
        spaces = " " * (100 - progress)
        # the pretty progress [####     ] 34%
        sys.stderr.write(
            "\r[{0:s}{1:s}] {2:3d}%".format(completed, spaces, progress))

    def set_lease_progress(self, lease):
        progress = int(round(self.readsofar * 100 / self.totalsize, ndigits=2))
        lease.HttpNfcLeaseProgress(progress)


class IterableToFileAdapter(object):

    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, dummy_size=-1):
        # TBD: add buffer for `len(data) > size` case
        return next(self.iterator, b'')

    def __len__(self):
        return self.length

    def close(self):
        self.iterator = None
        self.length = 0


class DownloadInChunks(object):

    def __init__(self, resp):
        self.resp = resp
        _LOGGER.debug(vars(resp))
        self.totalsize = len(resp.content)
        _LOGGER.debug(self.totalsize)

    def __iter__(self):
        for chunk in self.resp.iter_content(1 << 20):
            if chunk:
                yield chunk

    def __str__(self):
        for chunk in self.resp.iter_content(1 << 20):
            if chunk:
                yield chunk

    def __len__(self):
        return self.totalsize


def log_err_n_exit(msg, *args):
    _LOGGER.error(msg if not args else msg % args)
    sys.exit(1)


def get_args():
    parser = ArgumentParser(description='A script for deploying OVA to vCenter')

    parser.add_argument(
        '-V', '--version', action='version', version='%(prog)s v' + __version__)

    parser.add_argument(
        '-u', '--user', required=True, action='store', help='Username to use.')

    parser.add_argument(
        '-i',
        '--vmIp',
        required=True,
        action='store',
        help='last section of the vm IP address.')

    parser.add_argument(
        '-f',
        '--ova_uri',
        required=True,
        action='store',
        help='URI of the OVA file to be deployed, \
              could be a local path or an HTTP url. \
              If LATEST is given, will use latest stable build in artifactory.')

    parser.add_argument(
        '-d',
        '--vmFolder',
        nargs='?',
        action='store',
        help='vmFolder the vm belongs to.')

    parser.add_argument(
        '--nopoweron',
        action='store_true',
        help='Do not power on the vm after ova\'s deployment.')

    parser.add_argument(
        '--debug', action='store_true', help='Set log level, default INFO.')

    parser.add_argument(
        '--site',
        nargs='?',
        default='vc60',
        choices=['vc60', 'vc65'],
        action='store',
        help='Choose site running vcenter. (default: %(default)s)')

    parser.add_argument(
        '--edition',
        nargs='?',
        default='robo',
        choices=['robo', 'no_w', 'gsi'],
        action='store',
        help='Choose NBVA edition to deploy. (default: %(default)s)')

    args = parser.parse_args()
    if args.vmIp != 'ANY':
        if int(args.vmIp) not in range(2, 255):
            log_err_n_exit('Not valid IP address, set vmIp in range [2, 254]')

    if args.site == 'vc65':
        args.password = getpass(prompt='Enter password: ')
    else:
        args.password = 'Pas@symc'

    return args


def get_obj_in_list(obj_name, obj_list):
    """Get an object out of a list (obj_list) whos name matches obj_name."""
    for obj in obj_list:
        if obj.name == obj_name:
            return obj
    raise Exception("Unable to find object by the name of %s in list: %s" %
                    (obj_name, [x.name for x in obj_list]))


def get_objects(service_instance, args):
    # Get datacenter object.
    datacenter_list = service_instance.content.rootFolder.childEntity
    datacenter_obj = get_obj_in_list(vcenter_consts.DATA_CENTER,
                                     datacenter_list)

    # Get datastore object.
    datastore_list = datacenter_obj.datastoreFolder.childEntity
    datastore_obj = get_obj_in_list(vcenter_consts.DATA_STORE, datastore_list)

    # Get cluster object.
    cluster_list = datacenter_obj.hostFolder.childEntity
    cluster_obj = get_obj_in_list(vcenter_consts.CLUSTER, cluster_list)

    # Get resource pool.
    res_pool_list = cluster_obj.resourcePool.resourcePool
    res_pool_obj = get_obj_in_list(vcenter_consts.RES_POOL, res_pool_list)

    # Get vmFolder
    vmfolder_list = get_obj_in_list(
        vcenter_consts.VM_FOLDER_PARENT,
        datacenter_obj.vmFolder.childEntity).childEntity
    folder_name = ''
    if args.vmFolder:
        if args.vmFolder == "ANY":
            if args.user not in vcenter_consts.TEAM_INFO:
                log_err_n_exit('Not a known user, DO NOT set vmFolder to ANY')
            folder_name = vcenter_consts.TEAM_INFO[args.user][2]
            _LOGGER.debug('vm folder ANY: ' + folder_name)
        else:
            folder_name = args.vmFolder
    else:
        folder_name = args.user
    vmfolder = get_obj_in_list(folder_name, vmfolder_list)
    """
    print 'Datacenters: \t\t%s' % [o.name for o in datacenter_list]
    print 'Datastores: \t\t%s' % [o.name for o in datastore_list]
    print 'Clusters: \t\t%s' % [o.name for o in cluster_list]
    print 'Resource Pools: \t%s' % [o.name for o in resource_pool_list]
    print 'VM Folders: \t\t%s' % [o.name for o in vmfolder_list]
    """

    return datastore_obj, res_pool_obj, vmfolder


def get_valid_slot(user, vm_folder):
    occupied = []
    _LOGGER.debug('Get an IP address from [%d - %d]',
                  *vcenter_consts.TEAM_INFO[user][0:2])
    for vm in vm_folder.childEntity:  # pylint: disable=invalid-name
        match = re.match(r'^%s_%s(\d+)$' %
                         (user, vcenter_consts.HOSTNAME_PREFIX), vm.name)
        if match:
            secd = int(match.group(1))
            occupied.append(secd)

    ip_range = range(vcenter_consts.TEAM_INFO[user][0],
                     vcenter_consts.TEAM_INFO[user][1] + 1)
    ip_avail = set(ip_range).difference(occupied)
    _LOGGER.debug('Occupied IPs: %s', [o for o in occupied])
    if len(ip_avail) == 0:
        log_err_n_exit('IP pool of %s is empty, please remove some vm', user)

    return list(ip_avail)[0]


def keep_lease_alive(lease, chunk_reader):
    while not sig_triggered:
        sleep(2)
        try:
            if chunk_reader:
                chunk_reader.set_lease_progress(lease)
            else:
                lease.HttpNfcLeaseProgress(50)
            if lease.state == vim.HttpNfcLease.State.done or \
               lease.state == vim.HttpNfcLease.State.error:
                break
        except vim.fault.Timedout:
            _LOGGER.error('Lease timeout')
            break
        except:  # pylint: disable=bare-except
            break


def abort_lease(lease, reason):
    set_sig_flag()

    _LOGGER.error('Lease abort: %s', reason)
    fault = vmodl.MethodFault()
    # _LOGGER.debug(vars(fault))
    msg = vmodl.LocalizableMessage()
    msg.message = reason
    fault.faultMessage = [msg]
    fault.msg = reason
    lease.HttpNfcLeaseAbort(fault)


def power_on_vm(vm):  # pylint: disable=invalid-name
    if vm:
        vm.PowerOn()


def create_vim_keyvalue(key, value):
    key_value = vim.KeyValue()
    key_value.key = key
    key_value.value = value
    return key_value


class NbvaProps(object):  # pylint: disable=too-many-instance-attributes

    def __init__(self):
        self.hostname = ''
        self.vm_ip = ''
        self.fqdn = ''
        self.ad_pool = ''
        self.ad_stu = ''
        self.msdp_pool = ''
        self.msdp_stu = ''

        self.dns = vcenter_consts.DNS
        self.search = vcenter_consts.SEARCH_DOMAIN
        self.netmask = vcenter_consts.NETMASK
        self.gateway = vcenter_consts.GATEWAY

    def setup(self, sec_d):
        self._set_ip(sec_d)
        self._set_hostname(sec_d)
        self._set_nbu_config()

    def _set_ip(self, sec_d):
        self.vm_ip = vcenter_consts.IP_PREFIX + sec_d

    def _set_hostname(self, sec_d):
        self.hostname = vcenter_consts.HOSTNAME_PREFIX + sec_d
        self.fqdn = '%s.%s' % (self.hostname, self.search)

    def _set_nbu_config(self):
        self.ad_pool = vcenter_consts.AD_POOL_PREFIX + self.hostname
        self.ad_stu = vcenter_consts.AD_STU_PREFIX + self.hostname
        self.msdp_pool = vcenter_consts.MSDP_POOL_PREFIX + self.hostname
        self.msdp_stu = vcenter_consts.MSDP_STU_PREFIX + self.hostname

    def vimkv_fqdn(self):
        return create_vim_keyvalue('va.hostname', self.fqdn)

    def vimkv_search(self):
        return create_vim_keyvalue('va.dnsDomain', self.search)

    def vimkv_ip(self):
        return create_vim_keyvalue('va.ip', self.vm_ip)

    def vimkv_netmask(self):
        return create_vim_keyvalue('va.netmask', self.netmask)

    def vimkv_gateway(self):
        return create_vim_keyvalue('va.gateway', self.gateway)

    def vimkv_dns(self):
        return create_vim_keyvalue('va.dns1', self.dns)

    def vimkv_ad_pool(self):
        return create_vim_keyvalue('va.adPoolName', self.ad_pool)

    def vimkv_ad_stu(self):
        return create_vim_keyvalue('va.adStuName', self.ad_stu)

    def vimkv_msdp_pool(self):
        return create_vim_keyvalue('va.msdpPoolName', self.msdp_pool)

    def vimkv_msdp_stu(self):
        return create_vim_keyvalue('va.msdpStuName', self.msdp_stu)


def generate_nbva_props(ip_sec_d):
    nbva_props = NbvaProps()
    nbva_props.setup(ip_sec_d)
    return nbva_props


def create_import_spec(service_inst, ovfd, datastore, res_pool, spec_params):  # pylint: disable=too-many-arguments
    manager = service_inst.content.ovfManager
    return manager.CreateImportSpec(ovfd, res_pool, datastore, spec_params)


def create_import_params(secd, author):
    spec_params = vim.OvfManager.CreateImportSpecParams()

    nbva_props = generate_nbva_props(str(secd))
    spec_params.diskProvisioning = 'thin'
    spec_params.entityName = '%s_%s' % (author, nbva_props.hostname)

    spec_params.propertyMapping += [
        nbva_props.vimkv_fqdn(),
        nbva_props.vimkv_search(),
        nbva_props.vimkv_ip(),
        nbva_props.vimkv_netmask(),
        nbva_props.vimkv_gateway(),
        nbva_props.vimkv_dns(),
        nbva_props.vimkv_ad_pool(),
        nbva_props.vimkv_ad_stu(),
        nbva_props.vimkv_msdp_pool(),
        nbva_props.vimkv_msdp_stu()
    ]
    return spec_params


def pprint_elapsed(elapsed):
    if elapsed < 60:
        _LOGGER.info('elapsed %.2f seconds.', float(elapsed))
    else:
        _LOGGER.info('elapsed %d minutes %.2f seconds.', *divmod(elapsed, 60))


def count_method(method, *args):
    start_time = time()
    method(*args)
    elapsed = time() - start_time
    pprint_elapsed(elapsed)


def upload_vmdk(lease, ova, url):
    # Spawn a dawmon thread to keep the lease active while POSTing VMDK.
    keepalive_thread = Thread(target=keep_lease_alive, args=(lease, None,))
    # keepalive_thread = Thread(target=keep_lease_alive, args=(lease, chunk_reader,))
    keepalive_thread.start()
    fifo = 'fifo_%d' % os.getpid()

    try:
        _LOGGER.info('Upload file %s to url %s', ova.get_vmdk1_name(), url)
        """
        headers = {'Content-Type': 'application/x-vnd.vmware-streamVmdk',
                   'Content-Length': str(ova.get_vmdk1_size())}
        response = requests.post(url, data=IterableToFileAdapter(chunk_reader),
                   headers=headers, verify=False, stream=True)
        """

        os.mkfifo(fifo)
        atexit.register(os.unlink, fifo)
        gzip_cmd = " | %s -d --stdout " % GZIP_BIN if ova.is_vmdk_gzipped else ''
        if not ova.ova_on_fly:
            fifo_cmd = ("tar --extract --to-stdout -f %s %s" + gzip_cmd + "> %s"
                       ) % (ova.ova_uri, ova.get_vmdk1_name(), fifo)
        else:
            start_pos = ova.vmdk1_info.start + OvaOnFly.OVA_BLOCKSIZE
            partial_headers = "'Range: bytes=%d-%d'" % \
                              (start_pos, start_pos + ova.vmdk1_info.size - 1)
            _LOGGER.debug(partial_headers)
            fifo_cmd = ("curl -Ss -H %s %s" + gzip_cmd + "> %s") % (
                partial_headers, ova.ova_file.ova_url, fifo)

        curl_headers = "-H 'Content-Type: application/x-vnd.vmware-streamVmdk'"
        curl_output = "'\\nResp: %{http_code}\\nUploaded: %{size_upload}\\n'"
        curl_cmd = ("curl -X POST --insecure --write-out %s " +
                    "--output /dev/null -T %s %s %s") % (curl_output, fifo,
                                                         curl_headers, url)
        _LOGGER.info(fifo_cmd)
        _LOGGER.info(curl_cmd)

        # All python in memory tempt fail, it needs to load all data in mem.
        # With NBVA's case, it's >13GB and it's op pattern is 1 hit 1 go,
        # i.e. download first and then upload
        # Using external command would make it a stream process and much more efficient
        # proc_fifo = subprocess.Popen(fifo_cmd, shell=True, stdin=subprocess.PIPE)
        proc_fifo = subprocess.Popen(fifo_cmd, shell=True)
        _LOGGER.info('Uploading...')
        proc_curl = subprocess.Popen(shlex.split(curl_cmd))
        """
        if not ova.ova_on_fly:
            proc_fifo.communicate()
        else:
            proc_fifo.communicate(ova.get_vmdk1_obj().read())
        """

        proc_curl.wait()
        proc_fifo.wait()
        if proc_curl.returncode != 0:
            raise Exception('curl command failed')
        elif proc_fifo.returncode != 0:
            raise Exception('fifo command failed')
        """
        print '%d\t%s' % (response.status_code, response.returncode)
        """

        lease.HttpNfcLeaseProgress(100)
        lease.HttpNfcLeaseComplete()
    except Exception as exc:  # pylint: disable=broad-except
        _LOGGER.error(exc)
        print_exc()
        abort_lease(lease, 'Fail to upload vmdk')
    except KeyboardInterrupt:
        print ''
        abort_lease(lease, 'User aborted')

    keepalive_thread.join()


def import_ova(import_spec, ova, res_pool, vm_folder, no_poweron):
    lease = res_pool.ImportVApp(import_spec.importSpec, vm_folder)
    while True:
        if lease.state == vim.HttpNfcLease.State.ready:
            break
        elif lease.state == vim.HttpNfcLease.State.error:
            log_err_n_exit("Lease error: " + lease.error.msg)
        sleep(0.25)

    # NBVA's ova has only one vmdk
    vmdk1 = lease.info.deviceUrl[0]
    url = vmdk1.url

    upload_vmdk(lease, ova, url)
    if lease.state == vim.HttpNfcLease.State.done and not no_poweron:
        power_on_vm(lease.info.entity)


def main():
    args = get_args()
    if args.debug:
        _LOGGER_HANDLER.setFormatter(
            logging.Formatter('[%(levelname)s] <%(module)s>: %(message)s'))
        _LOGGER.setLevel(logging.DEBUG)

    global vcenter_consts
    vcenter_consts = VCenterConstants(args.site, args.password)

    try:
        _LOGGER.info("Connecting to vCenter %s", vcenter_consts.HOST)
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_NONE
        service_instance = connect.SmartConnect(
            host=vcenter_consts.HOST,
            user=vcenter_consts.USER_PREFIX + args.user,
            pwd=vcenter_consts.user_pwd,
            port=vcenter_consts.PORT,
            sslContext=context)
        atexit.register(connect.Disconnect, service_instance)
    except Exception as exc:  # pylint: disable=bare-except
        _LOGGER.error(exc.msg)
        log_err_n_exit("Unable to connect to vCenter %s", vcenter_consts.HOST)

    datastore, res_pool, vm_folder = get_objects(service_instance, args)
    if args.vmIp != 'ANY':
        secd = args.vmIp
    else:
        secd = get_valid_slot(args.user, vm_folder)
    author = args.user
    ova_uri = args.ova_uri

    _LOGGER.info('Reading ova file %s.', ova_uri)
    ova = OvaFile(ova_uri, args.edition)
    atexit.register(OvaFile.close, ova)
    ovfd = ova.get_ovf_content()

    spec_params = create_import_params(secd, author)
    import_spec = create_import_spec(service_instance, ovfd, datastore,
                                     res_pool, spec_params)
    # print str(import_spec).decode()
    """
    fobj = ova.get_vmdk1_obj()
    _LOGGER.debug(vars(fobj))
    exit(1)
    """
    """
    print 'Prepare vmdk file.'
    vmdkf = ova.get_vmdk1_obj()
    chunk_reader = UploadInChunks(vmdkf, ova.get_vmdk1_size(), chunksize=1024*1024*32)
    """

    _LOGGER.info('Creating vm %s, vmdk size %d.',
                 import_spec.importSpec.configSpec.name, ova.get_vmdk1_size())
    count_method(import_ova, import_spec, ova, res_pool, vm_folder,
                 args.nopoweron)


if __name__ == "__main__":
    main()
