#/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive
CACHE_FOLDER=/environment/cache/packages


echo 'Installing git'
apt-get install -y git >/dev/null
echo 'Finished installing git'

echo 'Installing Development Tools'
apt-get install -y build-essential >/dev/null
echo 'Finished installing Development Tools'

echo 'Installing Puppet'
apt-get install -y puppet >/dev/null
echo 'Finished installing Puppet'
