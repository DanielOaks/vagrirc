#/usr/bin/env sh
# Ruby Setup
# Mostly taken from the wonderful PuPHPet project, used under the MIT license

# CentOS release we're using
OS=centos
RELEASE=6


# Start of PuPHPet Ruby Setup <<<
/usr/local/rvm/bin/rvm cleanup all
gem update --system >/dev/null
echo 'y' | rvm rvmrc warning ignore all.rvmrcs

echo 'Finished installing RVM and Ruby 1.9.3'
# >>> End of PuPHPet Ruby Setup
