#/usr/bin/env sh
# Puppet Setup
# Mostly taken from the wonderful PuPHPet project

# CentOS release we're using
OS=centos
RELEASE=6


# Start of PuPHPet Puppet Setup <<<
rm -rf /usr/bin/puppet

if [ "${OS}" == 'debian' ] || [ "${OS}" == 'ubuntu' ]; then
    apt-get -y install augeas-tools libaugeas-dev
elif [[ "${OS}" == 'centos' ]]; then
    yum -y install augeas-devel
fi

echo 'Installing Puppet requirements'
gem install haml hiera facter json ruby-augeas --no-ri --no-rdoc
echo 'Finished installing Puppet requirements'

echo 'Installing Puppet 3.7.4'
gem install puppet --version 3.7.4 --no-ri --no-rdoc
echo 'Finished installing Puppet 3.7.4'

cat >/usr/bin/puppet << 'EOL'
#!/bin/bash

rvm ruby-1.9.3-p551 do puppet "$@"
EOL

chmod +x /usr/bin/puppet
# >>> End of PuPHPet Puppet Setup
