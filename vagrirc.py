#!/usr/bin/env python3
# VagrIRC Manager
"""VagrIRC - IRC development network provisioning made easy!

Maps out an IRC network, and creates all the config and shell files.

Basically, this is designed to be used before booting up a virtual machine
using Vagrant. This tool maps out a network, and then creates all the required
configuration files and shell scripts for the virtual machine to provision it
all once it's online.

Usage:
    vagrirc.py gen [options] <network_name>
    vagrirc.py (-h | --help)
    vagrirc.py --version

Options:
    --ircd <ircd>           IRCd to provision [default: hybrid].
    --services <services>   Services package to provision [default: anope2].
    --servers <servers>     Number of servers to have on the network [default: 1].
    -h, --help              Show this screen
    --version               Show VagrIRC version
"""
from docopt import docopt
import virc

if __name__ == '__main__':
    arguments = docopt(__doc__, version=virc.name_version)
    print(arguments)
