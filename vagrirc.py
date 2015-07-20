#!/usr/bin/env python3
# VagrIRC Manager

# Written in 2015 by Daniel Oaks <daniel@danieloaks.net>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

"""VagrIRC - IRC development network provisioning made easy!

Maps out an IRC network, and creates all the config and shell files.

Basically, this is designed to be used before booting up a virtual machine
using Vagrant. This tool maps out a network, and then creates all the required
configuration files and shell scripts for the virtual machine to provision it
all once it's online.

Usage:
    vagrirc.py generate (--oper <name:password>)... [options]
    vagrirc.py write
    vagrirc.py (list | list-software)
    vagrirc.py (-h | --help)
    vagrirc.py --version

Options:
    --ircd <ircd>                IRCd to provision [default: hybrid].
    --services <services>        Services package to provision [default: anope2].
    --service-bots <bots>...     Service bots to include (separated by comma <,>).
    --rizon                      Setup a network with Rizon's services, ircd, and bots.
    --with-moo                   Include moo while setting up a Rizon network.
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
        name = 'VagrIRC'
        suffix = '.dnt'

        if arguments['--rizon']:
            ircd = 'plexus4'
            services = 'anope2'
            if arguments['--with-moo']:
                service_bots = 'acid,moo'
            else:
                service_bots = 'acid'
            name = 'Rizon'
            suffix = '.rizon.net'

        service_bots = service_bots.split(',')
        oper_usernames_and_passwords = [
            name.split(':', 1) for name in arguments.get('<name:password>', [])
        ]

        manager.generate(ircd_type=ircd, services_type=services, service_bots=service_bots,
                         opers=oper_usernames_and_passwords, name=name, suffix=suffix)

    elif arguments['write']:
        manager = virc.VircManager()
        manager.load_network_map()
        manager.download_source()
        manager.write_server_configs()
        manager.write_source_files()
        manager.write_build_files()
        manager.write_init_files()

    elif arguments['list'] or arguments['list-software']:
        manager = virc.VircManager()
        sw = manager.supported_software()

        def req(info):
            if not info:
                return ''

            out = 'Requires '

            reqs = []

            for sw_type in ['ircd', 'services', 'service bots']:
                sw = info.get(sw_type)
                if sw:
                    if not isinstance(sw, (list, tuple)):
                        sw = [sw]
                    reqs.append('{} [{}]'.format(sw_type, ','.join(sw)))

            out += ', '.join(reqs)

            return out

        print('Supported Software')

        print('\n** IRCd **')
        for name, info in sorted(sw.get('ircd', {}).items()):
            print('  {} : {} {}'.format(name, info['description'], req(info['requires'])))

        print('\n** Services **')
        for name, info in sorted(sw.get('services', {}).items()):
            print('  {} : {} {}'.format(name, info['description'], req(info['requires'])))

        print('\n** Service Bots **')
        for name, info in sorted(sw.get('service bots', {}).items()):
            print('  {} : {} {}'.format(name, info['description'], req(info['requires'])))
