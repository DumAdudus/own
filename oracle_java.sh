#!/bin/bash

UPDATE=191
BUILD=12
UUID=2787e4a523244c269598db4e85c51e0c


jdk=jdk-8u${UPDATE}-linux-x64.rpm
format='https://download.oracle.com/otn-pub/java/jdk/8u%i-b%i/%s/%s'
uri=$(printf $format $UPDATE $BUILD $UUID $jdk)
echo "$uri"
wget --continue --no-verbose -O $jdk --header "Cookie: oraclelicense=a" "$uri" && yum install -y $jdk
