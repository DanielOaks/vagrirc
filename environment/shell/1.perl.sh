#/usr/bin/env sh
# Perl Setup
# Mostly taken from the wonderful PuPHPet project, used under the MIT license

# CentOS release we're using
OS=centos
RELEASE=6


# Software
echo 'Installing perl'
yum -y install perl >/dev/null
echo 'Finished installing perl'
