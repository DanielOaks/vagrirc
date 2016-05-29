#/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive
CACHE_FOLDER=/environment/cache/packages


echo 'Installing RVM'
apt-add-repository -y ppa:rael-gc/rvm >/dev/null
apt-get update
apt-get install -y rvm
echo 'Finished installing RVM'
