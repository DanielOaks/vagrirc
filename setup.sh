#!/usr/bin/env sh
# Sets up the required plugins / etc we need

# to cache packages
vagrant plugin install vagrant-cachier

# to run vagrirc
pip3 install -r requirements.txt
