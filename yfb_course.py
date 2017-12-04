#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import logging
import os
import re
import subprocess
import sys
import time
from HTMLParser import HTMLParser
from urlparse import parse_qs, urlparse

import requests
from lxml import etree
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

disable_warnings(InsecureRequestWarning)

__title__ = 'yfb course downloader'
__version__ = '1.1'
__author__ = 'DumAs'

LOGGER = logging.getLogger('')
LOGGER_HANDLER = logging.StreamHandler()
LOGGER.addHandler(LOGGER_HANDLER)
LOGGER_HANDLER.setFormatter(
    logging.Formatter(
        "[%(asctime)s] [%(levelname)5s] --- %(message)s (%(filename)s:%(lineno)s)",
        "%Y-%m-%d %H:%M:%S"))
LOGGER.setLevel(logging.DEBUG)

YFB_COOKIE = 'yfb_cookie.txt'
LESSON_LIST = 'http://edu.yanfabu.com/lessonplugin/lesson/list?courseId=%d'
LESSON_URI_FMT = 'http://edu.yanfabu.com/course/%d/lesson/%d'
AES_KEY_REGEX = r'http://edu.yanfabu.com/hls/[0-9]*/clef/[^"]*'
LOG_FILE = 'yfb.log'

KEY_MEDIA_URI = 'mediaUri'
KEY_MEDIA_HLS = 'mediaHLSUri'
KEY_LESSON_TITLE = 'title'
KEY_FILE_ID = 'file_id'
KEY_APP_ID = 'app_id'

SWF_PLAYLIST = 'http://play.video.qcloud.com/index.php?_t={timestamp:d}&file_id={fileid:d}&interface=Vod_Api_GetPlayInfo&app_id={appid:d}&refer=edu.yanfabu.com'
# CMD_FFMPEG = 'ffmpeg -hide_banner -v info -i "%s" -bsf:a aac_adtstoasc -c copy "%s.ts"'
CMD_FFMPEG = 'ffmpeg -hide_banner -v info -i "%s" -c copy "%s.ts"'


def log_err_n_exit(msg, *args):
    LOGGER.error(msg if not args else msg % args)
    sys.exit(1)


def check_response(resp, msg=None):
    if resp.status_code != 200:
        LOGGER.debug(resp.headers)
        LOGGER.debug(resp.content)
        if msg:
            log_err_n_exit(msg)
        else:
            log_err_n_exit('Failed to request %s', resp.url)


def chwd(path):
    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)


def write2file(filename, content):
    with open(filename, 'w') as f:
        f.write(content)


def transform_filename(filename):
    LOGGER.debug(filename)
    # first unescape
    parser = HTMLParser()
    unescaped = parser.unescape(filename)
    # replace '/' with unicode U+2215 '∕'
    new_name = unescaped.replace('/', u'\u2215')
    return new_name


class YfbCourse(object):

    def __init__(self, course_id):
        self._course_id = course_id
        self._lessons = []
        cookies = cookielib.MozillaCookieJar('yfb_cookie.txt')
        cookies.load(ignore_expires=True)
        for cookie in cookies:
            # set cookie expire date to two weeks from today
            cookie.expires = time.time() + 14 * 24 * 3600
        self.req = requests.Session()
        self.req.cookies = cookies

    def get_course_id(self):
        return self._course_id

    def get_lesson_count(self):
        return len(self._lessons)

    def get_course(self):
        lessons = self._get_lessons()
        LOGGER.debug(lessons)
        course_dir = './yfb_course_%d' % self._course_id
        chwd(course_dir)
        # for lesson in lessons:
        for lesson in lessons[lessons.index(6208):]:
            self._get_lesson(lesson)

    def _get_lessons(self):
        if not self._lessons:
            resp = self.req.get(LESSON_LIST % self._course_id)
            check_response(resp)
            tree = etree.HTML(resp.content)
            self._lessons = map(int, tree.xpath('//li/@data-id'))
        return self._lessons

    def _get_lesson(self, lesson_id):
        lesson_url = LESSON_URI_FMT % (self._course_id, lesson_id)

        resp = self.req.get(lesson_url)
        check_response(resp, 'Failed to get lesson info,')
        lesson_info = resp.json()
        LOGGER.debug(lesson_info)
        if KEY_MEDIA_URI in lesson_info and \
           'video_player.swf' in lesson_info[KEY_MEDIA_URI]:
            self._dl_swf_src(lesson_info)
        elif KEY_MEDIA_HLS in lesson_info:
            self._dl_hls_src(lesson_info)
        else:
            log_err_n_exit(str(lesson_info) + '\nUnrecognized lesson info,')

    def _dl_swf_src(self, lesson_info):
        LOGGER.info('%s <-> %s', lesson_info[KEY_LESSON_TITLE],
                    lesson_info['endTimeFormat'])
        uri_parse = urlparse(lesson_info[KEY_MEDIA_URI])
        queries = parse_qs(uri_parse.query)
        LOGGER.debug(queries)
        if set((KEY_FILE_ID, KEY_APP_ID)) <= queries.keys():
            log_err_n_exit('Unrecognized swf url: %s',
                           lesson_info[KEY_MEDIA_URI])
        videos_url = SWF_PLAYLIST.format(
            timestamp=int(time.time()),
            fileid=int(queries[KEY_FILE_ID][0]),
            appid=int(queries[KEY_APP_ID][0]))
        resp = self.req.get(videos_url)
        check_response(resp)
        video_info = resp.json()['data']['file_info']
        video_size = int(video_info['size'])
        LOGGER.debug('Video size: %d B', video_size)
        video_url = None
        video_list = video_info['image_video']['videoUrls']
        if video_size == 0:
            video_url = video_list[0]['url']
        else:
            for video in video_list:
                if video['fileSize'] == video_size:
                    video_url = video['url']
                    LOGGER.debug(video_url)
                    break
        if not video_url:
            log_err_n_exit('Failed to get video url, info content: %s',
                           video_info)
        self._dlfile(video_url, '%s.ts' % lesson_info[KEY_LESSON_TITLE])

    def _dl_hls_src(self, lesson_info):
        LOGGER.info('%s <-> %s', lesson_info[KEY_LESSON_TITLE],
                    lesson_info['endTimeFormat'])
        resp = self.req.get(lesson_info[KEY_MEDIA_HLS])
        check_response(resp)
        LOGGER.debug(resp.content)
        hd_hls_url = resp.content.splitlines()[-1]  # [sd, md, hd]
        local_hls = '%s.m3u8' % lesson_info[KEY_LESSON_TITLE]
        aes_key = '%s.key' % lesson_info['mediaId']
        hls_content = self.req.get(hd_hls_url).content
        # LOGGER.debug(hd_hls_content)
        s = re.search(AES_KEY_REGEX, hls_content)
        if not s:
            log_err_n_exit('Failed to search the pattern')
        # aes key url: "http://edu.yanfabu.com/hls/1334/clef/lMl7x53UqIkza9RXX3I0edSIDutxmHA5"
        aes_key_url = s.group(0)
        hls_content = hls_content.replace(aes_key_url, aes_key)
        write2file(local_hls, hls_content)
        self._dlfile(aes_key_url, aes_key)
        ffmpeg_cmd = CMD_FFMPEG % (local_hls, lesson_info[KEY_LESSON_TITLE])
        LOGGER.debug(ffmpeg_cmd)
        proc = subprocess.Popen(ffmpeg_cmd, shell=True)
        proc.wait()
        if proc.returncode != 0:
            log_err_n_exit('Failed to convert stream, exit code: %d',
                           proc.returncode)

    def _dlfile(self, url, filename):
        r = self.req.get(url)
        if not r.ok:
            log_err_n_exit('Failed to download %s', url)
        with open(transform_filename(filename), 'wb') as f:
            for chunk in r.iter_content(1024 * 1024 * 4):  # 4MB chunk
                f.write(chunk)


def main():
    yfb = YfbCourse(1165)
    yfb.get_course()


if __name__ == "__main__":
    main()
