#!/usr/bin/env python3
# VagrIRC Manager
"""VagrIRC - IRC development network provisioning made easy!

Maps out an IRC network, and creates all the config and shell files.

Basically, this is designed to be used before booting up a virtual machine
using Vagrant. This tool maps out a network, and then creates all the required
configuration files and shell scripts for the virtual machine to provision it
all once it's online.

Usage:
    vagrirc.py generate (--oper <name:password>)... [options]
    vagrirc.py write
    vagrirc.py (-h | --help)
    vagrirc.py --version

Options:
    --ircd <ircd>                IRCd to provision [default: hybrid].
    --services <services>        Services package to provision [default: anope2].
    --service-bots <bots>...     Service bots to include (separated by comma <,>).
    (--oper <name:password>)...  Make an oper / opers with the given names and passwords.
    -h, --help                   Show this screen
    --version                    Show VagrIRC version
"""
from docopt import docopt
import virc

if __name__ == '__main__':
    arguments = docopt(__doc__, version=virc.name_version)

    if arguments['generate']:
        manager = virc.VircManager()
        ircd = arguments['--ircd']
        services = arguments['--services']
        service_bots = arguments.get('--service-bots', '')
        if service_bots is None:
            service_bots = ''
        service_bots = service_bots.split(',')
        oper_usernames_and_passwords = [name.split(':', 1) for name in arguments.get('<name:password>', [])]

        manager.generate(ircd_type=ircd, services_type=services, service_bots=service_bots, opers=oper_usernames_and_passwords)

    elif arguments['write']:
        manager = virc.VircManager()
        manager.load_network_map()
        manager.write_server_configs()
        manager.write_source_files()
        manager.write_build_files()
        manager.write_init_files()
