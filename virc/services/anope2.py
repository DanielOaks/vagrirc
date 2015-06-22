#!/usr/bin/env python3
# VagrIRC Virc library
import os
import re

from ..base import BaseServices


# Removal Regexes
config_initial_replacements = [
    re.compile(r'(?:[\s\n]|^)/\*(.|[\r\n])*?\*/'),  # c style comments
    re.compile(r'\n#[a-zA-Z0-9]+\s*\n?\s*{[^}]+}'),  # remove commented out blocks
    (re.compile(r'\n(?:\s*\n)+'), r'\n'),  # remove blank lines
    (re.compile(r'^[\s\n]*([\S\s]*?)[\s\n]*$'), r'\1\n'),  # remove start/end blank space, make sure newline at end
    ('usemail = yes', 'usemail = no'),  # we don't use mail
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
}}
"""


class Anope2Services(BaseServices):
    """Implements support for Anope2 Services."""
    name = 'anope2'
    release = '2.0.1'
    url = 'https://github.com/anope/anope/archive/{release}.zip'

    def write_config(self, folder):
        """Write config file to the given folder."""
        # load original config file
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
                print('anope2 config: skipping key:', key)

        # external ircd module to load
        server_sw = self.info['links'][0]['server_software']
        if server_sw == 'hybrid':
            server_sw_name = 'hybrid'
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

        # writing out config file
        output_config_dir = os.path.join(folder, 'conf')

        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)

        output_config_file = os.path.join(output_config_dir, 'services.conf')
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
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build.sh')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        launch_file = """#!/usr/bin/env sh
{bin_folder}/bin/services
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch.sh')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
