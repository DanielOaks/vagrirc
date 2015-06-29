#/usr/bin/env sh
# Ruby Setup
# Mostly taken from the wonderful PuPHPet project, used under the MIT license

CACHE_FOLDER=/environment/cache/repos

# CentOS release we're using
OS=centos
RELEASE=6


# Start of PuPHPet Ruby Setup <<<
rm -rf /usr/bin/ruby /usr/bin/gem /usr/bin/rvm /usr/local/rvm

echo 'Installing RVM and Ruby 1.9.3'

if [ "${OS}" == 'debian' ] || [ "${OS}" == 'ubuntu' ]; then
    gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys D39DC0E3
elif [[ "${OS}" == 'centos' ]]; then
    gpg2 --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys D39DC0E3
fi

curl -sSL https://get.rvm.io | bash -s stable --quiet-curl --ruby=ruby-1.9.3-p551

source /usr/local/rvm/scripts/rvm

if [[ -f '/root/.bashrc' ]] && ! grep -q 'source /usr/local/rvm/scripts/rvm' /root/.bashrc; then
    echo 'source /usr/local/rvm/scripts/rvm' >> /root/.bashrc
fi

if [[ -f '/etc/profile' ]] && ! grep -q 'source /usr/local/rvm/scripts/rvm' /etc/profile; then
    echo 'source /usr/local/rvm/scripts/rvm' >> /etc/profile
fi
# Unfinished end of PuPHPet Ruby Setup
