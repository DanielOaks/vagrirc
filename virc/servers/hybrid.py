#!/usr/bin/env python3
# VagrIRC Virc library
import os
import re

from ..base import BaseServer

# Removal Regexes
config_initial_regexes = [
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

    # basic config options
    re.compile(r'\n\s*havent_read_conf.+'),
    re.compile(r'\n\s*flags = need_ident;'),
]

config_regexes = {
    'name': (re.compile(r'(serverinfo \{\n\s*name = )[^\;]+(;)'), r'\1"{value}"\2'),
    'sid': (re.compile(r'(\n\s*sid = )"[0-9a-zA-Z]{3}"(;)'), r'\1"{value}"\2'),
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
    flags = hidden;
    port = {link_ports};
}};
{connect_blocks}"""


class HybridServer(BaseServer):
    """Implements support for the Hybrid IRCd."""
    name = 'hybrid'
    release = '8.2.8'
    url = 'https://github.com/ircd-hybrid/ircd-hybrid/archive/{release}.zip'

    def write_config(self, folder):
        """Write config file to the given folder."""
        # load original config file
        original_config_file = os.path.join(self.source_folder, 'doc', 'reference.conf')
        with open(original_config_file, 'r') as config_file:
            config_data = config_file.read()

        # removing useless junk
        for regex in config_initial_regexes:
            # replacement
            if isinstance(regex, (list, tuple)):
                regex, sub = regex

            # removal
            else:
                sub = ''

            config_data = regex.sub(sub, config_data)

        # special stuff
        config_data = config_data.replace('hub = no;', 'hub = yes;')

        # inserting actual values
        for key, value in self.info.items():
            if key in config_regexes:
                regex, sub = config_regexes[key]
                sub = sub.format(value=value)
                config_data = regex.sub(sub, config_data)
            else:
                print('hybrid regex: skipping key:', key)

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

        # writing out config file
        output_config_dir = os.path.join(folder, 'etc')

        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)

        output_config_file = os.path.join(output_config_dir, 'reference.conf')
        with open(output_config_file, 'w') as config_file:
            config_file.write(config_data)

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
cd {src_folder}
chmod +x ./configure
./configure --prefix={bin_folder}
make
make install

cp {config_folder}/etc/reference.conf {bin_folder}/etc/ircd.conf
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build.sh')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        launch_file = """#!/usr/bin/env sh
{bin_folder}/bin/ircd
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch.sh')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
