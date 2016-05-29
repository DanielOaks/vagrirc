#/usr/bin/env sh

export DEBIAN_FRONTEND=noninteractive
CACHE_FOLDER=/environment/cache/packages


echo 'Installing Puppet'
gem update rdoc
gem install puppet
echo 'Finished installing Puppet'
