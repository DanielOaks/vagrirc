#!/usr/bin/env python3
# VagrIRC Virc library

# Written in 2015 by Daniel Oaks <daniel@danieloaks.net>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import os
import re

from ..base import BaseServices


# Removal Regexes
config_initial_replacements = [
    re.compile(r'(?:[\s\n]|^)/\*(.|[\r\n])*?\*/'),  # c style comments
    (re.compile(r'(module[\s\n]+?{[\s\n]+?name = "os_session")'), r'#\1'),  # comment out os_session block
    re.compile(r'\n#[a-zA-Z0-9]+\s*\n?\s*{[^}]+}'),  # remove commented out blocks
    (re.compile(r'\n(?:\s*\n)+'), r'\n'),  # remove blank lines
    (re.compile(r'^[\s\n]*([\S\s]*?)[\s\n]*$'), r'\1\n'),  # remove start/end blank space, make sure newline at end
    ('usemail = yes', 'usemail = no'),  # we don't use mail
    ('operserv.example.conf', 'operserv.conf'),  # we change session limit settings
]

config_replacements = {
    'name': ('services.localhost.net', '{value}'),
    'sid': ('#id = "00A"', 'id = "{value}"'),
    'network_name': ('networkname = "LocalNet"', 'networkname = "{value}"'),
}

UPLINK_BLOCK = r"""uplink
{{
    host = "127.0.0.1"
    ipv6 = no
    ssl = no
    port = {port}
    password = "{password}"
}}"""

OPERATOR_BLOCK = r"""oper
{{
    name = "{name}"
    type = "{level}"
    vhost = "oper.dnt"
}}"""


class Anope2Services(BaseServices):
    """Implements support for Anope2 Services."""
    name = 'anope2'
    release = '2.0.1'
    url = 'https://github.com/anope/anope/archive/{release}.zip'

    def init_users(self, info):
        """Return a list of 'users' to join to the network, along with commands.

        Used during network provisioning to register accounts with NickServ,
        register and set channel info such as topic, etc.
        """
        users = []

        for name, uinfo in info['users'].items():
            # only worry about users with nickserv / etc to setup
            if 'services' not in uinfo:
                continue

            sinfo = uinfo['services']

            # define base user info
            nick = sinfo.get('account_name', name)
            user = uinfo.get('username', 'initbot')
            commands = []

            # if they need to be registered with nickserv
            if 'password' in sinfo:
                # fake email if they don't have one
                register_args = {
                    'password': sinfo['password'],
                    'email': uinfo.get('email', '{}@example.com'.format(name)),
                }

                commands.append(['nickserv', 'register {password} {email}'.format(**register_args)])

            # assemble new user
            new_user = {
                'nick': nick,
                'username': user,
                'commands': commands,
            }

            users.append(new_user)

        return users

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        # master config file
        # # # #
        original_config_file = os.path.join(self.source_folder, 'data', 'example.conf')
        with open(original_config_file, 'r') as config_file:
            config_data = config_file.read()

        # removing useless junk
        for rep in config_initial_replacements:
            # replacement
            if isinstance(rep, (list, tuple)):
                rep, sub = rep

            # removal
            else:
                sub = ''

            if isinstance(rep, str):
                config_data = config_data.replace(rep, sub)
            else:
                config_data = rep.sub(sub, config_data)

        # inserting actual values
        for key, value in self.info.items():
            if key in config_replacements:
                rep, sub = config_replacements[key]
                sub = sub.format(value=value)

                if isinstance(rep, str):
                    config_data = config_data.replace(rep, sub)
                else:
                    config_data = rep.sub(sub, config_data)
            else:
                # print('anope2 config: skipping key:', key)
                ...

        # external ircd module to load
        server_sw = self.info['links'][0]['server_software']
        if server_sw == 'hybrid':
            server_sw_name = 'hybrid'
            config_data = config_data.replace('casemap = "ascii"', 'casemap = "rfc1459"')
        elif server_sw == 'plexus4':
            server_sw_name = 'plexus'
            config_data = config_data.replace('casemap = "ascii"', 'casemap = "rfc1459"')
        elif server_sw == 'inspircd':
            server_sw_name = 'inspircd20'
        else:
            raise Exception('unknown server sw in anope config setting: [{}]'.format(server_sw))

        config_data = config_data.replace('name = "inspircd20"', 'name = "{}"'.format(server_sw_name))

        # replacing uplink block
        uplink_regex = re.compile(r'uplink[\s\n]*\{[^\}]+\}')
        uplink = UPLINK_BLOCK.format(port=self.info['links'][0]['port'],
                                     password=self.info['links'][0]['password'])
        config_data = uplink_regex.sub(uplink, config_data)

        # opers
        for name, info in info['users'].items():
            if 'services' not in info:
                continue

            level = info['services'].get('level', None)
            if level is None:
                level = info.get('level', None)  # may also be root

            # convert from general names to specific names
            if level == 'root':
                level = 'Services Root'
            elif level == 'service bot':
                level = 'Services Root'  # xxx - lazy, but works for now

            # only add operator block if they have a valid level
            if level:
                services_name = info['services']['name'] if 'name' in info['services'] else name
                password = info['services']['password']

                config_data += OPERATOR_BLOCK.format(level=level, name=services_name, password=password)

        # writing out config file
        output_config_dir = os.path.join(folder, 'conf')

        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)

        output_config_file = os.path.join(output_config_dir, 'services.conf')
        with open(output_config_file, 'w') as config_file:
            config_file.write(config_data)

        # operserv config file
        # # # #
        original_config_file = os.path.join(self.source_folder, 'data', 'operserv.example.conf')
        with open(original_config_file, 'r') as config_file:
            config_data = config_file.read()

        # removing useless junk
        for rep in config_initial_replacements:
            # replacement
            if isinstance(rep, (list, tuple)):
                rep, sub = rep

            # removal
            else:
                sub = ''

            if isinstance(rep, str):
                config_data = config_data.replace(rep, sub)
            else:
                config_data = rep.sub(sub, config_data)

        output_config_file = os.path.join(output_config_dir, 'operserv.conf')
        with open(output_config_file, 'w') as config_file:
            config_file.write(config_data)

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
cd {src_folder}

test -d build || mkdir build
cd build

cmake '-DINSTDIR:STRING={bin_folder}' -DCMAKE_BUILD_TYPE:STRING=DEBUG -DUSE_RUN_CC_PL:BOOLEAN=OFF -DUSE_PCH:BOOLEAN=OFF ..

make
make install

cp /irc/configs/services_anope2/conf/services.conf /irc/bin/services_anope2/conf/services.conf
cp /irc/configs/services_anope2/conf/operserv.conf /irc/bin/services_anope2/conf/operserv.conf
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        launch_file = """#!/usr/bin/env sh
{bin_folder}/bin/services
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
