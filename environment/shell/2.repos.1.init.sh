#/usr/bin/env sh
# Repos Setup
# Mostly taken from the wonderful PuPHPet project

CACHE_FOLDER=/environment/cache/repos

# CentOS release we're using
OS=centos
RELEASE=6


# Start of PuPHPet Initial Setup <<<
echo 'Adding repos: elrepo, epel, scl'
perl -p -i -e 's@enabled=1@enabled=0@gi' /etc/yum/pluginconf.d/fastestmirror.conf
perl -p -i -e 's@#baseurl=http://mirror.centos.org/centos/\$releasever/os/\$basearch/@baseurl=http://mirror.rackspace.com/CentOS//\$releasever/os/\$basearch/\nenabled=1@gi' /etc/yum.repos.d/CentOS-Base.repo
perl -p -i -e 's@#baseurl=http://mirror.centos.org/centos/\$releasever/updates/\$basearch/@baseurl=http://mirror.rackspace.com/CentOS//\$releasever/updates/\$basearch/\nenabled=1@gi' /etc/yum.repos.d/CentOS-Base.repo
perl -p -i -e 's@#baseurl=http://mirror.centos.org/centos/\$releasever/extras/\$basearch/@baseurl=http://mirror.rackspace.com/CentOS//\$releasever/extras/\$basearch/\nenabled=1@gi' /etc/yum.repos.d/CentOS-Base.repo

if [ "${RELEASE}" == 6 ]; then
    EL_REPO='http://www.elrepo.org/elrepo-release-6-6.el6.elrepo.noarch.rpm'
    EPEL='https://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm'
else
    EL_REPO='http://www.elrepo.org/elrepo-release-7.0-2.el7.elrepo.noarch.rpm'
    EPEL='https://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm'
fi

# caching
EL_REPO_CACHE="${CACHE_FOLDER}/$(echo ${EL_REPO} | awk -F/ '{print $NF}')"
EPEL_CACHE="${CACHE_FOLDER}/$(echo ${EPEL} | awk -F/ '{print $NF}')"

mkdir -p "$CACHE_FOLDER"
if [ ! -e "${EL_REPO_CACHE}" ]; then
    wget "${EL_REPO}" -O "${EL_REPO_CACHE}"
fi
if [ ! -e "${EPEL_CACHE}" ]; then
    wget "${EPEL}" -O "${EPEL_CACHE}"
fi

yum -y --nogpgcheck install "${EL_REPO_CACHE}" >/dev/null
yum -y --nogpgcheck install "${EPEL_CACHE}" >/dev/null
yum -y install centos-release-SCL >/dev/null
# Unfinished End of PuPHPet Initial Setup <<<
