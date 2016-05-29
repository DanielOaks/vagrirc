#/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive
CACHE_FOLDER=/environment/cache/packages


echo 'Installing Ruby'
source /usr/share/rvm/scripts/rvm
rvm install 1.9.3 >/dev/null
rvm --default use 1.9.3
echo 'Finished installing Ruby'
