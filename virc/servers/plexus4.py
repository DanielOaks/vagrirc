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

from ..base import BaseServer

# Removal Regexes
config_initial_replacements = [
    re.compile(r'/\*(.|[\r\n])*?\*/'),  # c style comments
    re.compile(r'\n\s*//.*'),  # c++ style comments
    re.compile(r'\n\s*#.*'),  # shell style comments
    (re.compile(r'\n(?:\s*\n)+'), r'\n'),  # remove blank lines
    (re.compile(r'^[\s\n]*([\S\s]*?)[\s\n]*$'), r'\1\n'),  # remove start/end blank space, make sure newline at end

    re.compile(r'\nmotd \{([^\}]*?)\};'),
    re.compile(r'\nlisten \{([^\}]*?)\};'),
    re.compile(r'\noperator \{([^\}]*?)\};'),
    re.compile(r'\nconnect \{([^\}]*?)\};'),
    re.compile(r'\ncluster \{([^\}]*?)\};'),
    re.compile(r'\nshared \{([^\}]*?)\};'),
    re.compile(r'\nkill \{([^\}]*?)\};'),
    re.compile(r'\ndeny \{([^\}]*?)\};'),
    re.compile(r'\nexempt \{([^\}]*?)\};'),
    re.compile(r'\ngecos \{([^\}]*?)\};'),

    re.compile(r'\nauth \{([^\}]*?)letmein([^\}]*?)\};'),
    re.compile(r'\nauth \{([^\}]*?)tld([^\}]*?)\};'),
    re.compile(r'\nresv \{([^\}]*?)helsinki([^\}]*?)\};'),

    re.compile(r'(\nauth \{[^\}]+redirserv[^\}]+\};)'),

    # basic config options
    re.compile(r'\n\s*havent_read_conf.+'),
    re.compile(r'\n\s*flags = need_ident;'),
    ('hub = no;', 'hub = yes;'),
    ('throttle_time = 1 second;', 'throttle_time = 0;'),  # else we get locked out during config
    ('services.rizon.net', 'services--network-suffix--'),
    ('hidden_name = "*.rizon.net";', 'hidden_name = "*--network-suffix--";'),
]

config_replacements = {
    'name': (re.compile(r'(serverinfo \{\n\s*name = )[^\;]+(;)'), r'\1"{value}"\2'),
    'sid': (re.compile(r'(\n\s*sid = )"[^"]+?"(;)'), r'\1"{value}"\2'),
    'network_name': (r'Rizon', r'{value}'),
}

CONN_BLOCK = r"""connect {{
    name = "{remote_name}";
    host = "127.0.0.1";
    send_password = "{password}";
    accept_password = "{password}";
    encrypted = no;
    port = {port};
}};"""

LISTEN_BLOCK = r"""\1\nlisten {{
    port = {client_port};
    flags = hidden, server;
    port = {link_ports};
}};
{connect_blocks}"""

OPERATOR_BLOCK = '''operator {{
    name = "{name}";

    user = "*@127.0.0.1";
    user = "*@localhost";
    user = "*@10.*";

    password = "{password}";
    encrypted = no;

    whois = "is an IRC Operator";
    ssl_connection_required = no;

    class = "opers";
    umodes = locops, servnotice, wallop, external, cconn, debug, farconnect,
        skill, unauth;
    snomasks = full, rej, skill, link, link:remote, unauth, spy;
    flags = kill, kill:remote, connect, connect:remote, kline, unkline,
        xline, globops, restart, die, rehash, admin, operwall, module;
}};
'''


class Plexus4Server(BaseServer):
    """A fork of ircd-hybrid for Rizon Chat Network."""
    name = 'plexus4'
    vcs = 'git'
    url = 'https://gitlab.com/rizon/plexus4.git'

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        # load original config file
        original_config_file = os.path.join(self.source_folder, 'doc', 'reference.conf')
        with open(original_config_file, 'r') as config_file:
            config_data = config_file.read()

        # removing useless junk
        for rep in config_initial_replacements:
            # replacement
            if isinstance(rep, (list, tuple)):
                rep, sub = rep

                # lazy variables
                sub = sub.replace('--network-suffix--', self.info['network_suffix'])

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
                print('plexus4 regex: skipping key:', key)

        # listening ports
        lregex = re.compile(r'(\nauth \{[^\}]+\};)')

        connect_blocks = []

        ports = []
        for link in self.info['links']:
            ports.append(str(link['port']))
            connect_blocks.append(CONN_BLOCK.format(remote_name=link['remote_name'],
                                                    password=link['password'],
                                                    port=link['port']))

        link_ports = ', '.join(ports)

        sub = LISTEN_BLOCK.format(client_port=self.info['client_port'],
                                  link_ports=link_ports,
                                  connect_blocks='\n'.join(connect_blocks))

        config_data = lregex.sub(sub, config_data)

        # users
        for name, info in info['users'].items():
            if 'ircd' not in info:
                continue

            if 'oper' in info['ircd'] and info['ircd']['oper']:
                oper_name = info['ircd']['oper_name'] if 'oper_name' in info['ircd'] else name
                oper_pass = info['ircd']['oper_pass']

                config_data += OPERATOR_BLOCK.format(name=oper_name, password=oper_pass)

        # writing out config file
        if not os.path.exists(folder):
            os.makedirs(folder)

        output_config_file = os.path.join(folder, 'reference.conf')
        with open(output_config_file, 'w') as config_file:
            config_file.write(config_data)

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
cd {src_folder}
sh autogen.sh
chmod +x ./configure
./configure --prefix={bin_folder} --enable-lua --enable-libjansson --enable-halfops --enable-chanaq
make
make install

cp {config_folder}/reference.conf {bin_folder}/etc/ircd.conf
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        launch_file = """#!/usr/bin/env sh
{bin_folder}/bin/ircd
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
