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
import shutil

import yaml

from ..base import BaseServiceBot


class AcidServiceBot(BaseServiceBot):
    """Implements support for the Hybrid IRCd."""
    name = 'acid'
    vcs = 'git'
    url = 'https://gitlab.com/rizon/acid.git'

    def init_info(self):
        """Create our info."""
        self.info['users'] = {
            'moo': {
                'services': {
                    'password': 'moomoo',
                    'level': 'service bot',
                },
                'email': 'moo@example.com',
            }
        }

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        config_files = {
            'pyva-native': [
                os.path.join(self.source_folder, 'pyva', 'pyva-native', 'pyva-cpp', 'make.example.properties'),
                os.path.join(folder, 'pyva', 'pyva-native', 'pyva-cpp', 'make.properties'),
            ],
            'acid': [
                os.path.join(self.source_folder, 'acid', 'acidictive.example.yml'),
                os.path.join(folder, 'acid', 'acidictive.yml'),
            ],
        }

        # create folders
        output_config_dir = os.path.join(folder, 'pyva', 'pyva-native', 'pyva-cpp')
        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)
        output_config_dir = os.path.join(folder, 'acid')
        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)

        # pyva-native compilation makefile
        orig, new = config_files['pyva-native']
        shutil.copyfile(orig, new)

        # aciditive config file
        orig, new = config_files['acid']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        conf = yaml.load(config_data)

        # setting info
        conf['uplink']['host'] = '127.0.0.1'
        conf['uplink']['pass'] = self.info['links'][0]['password']
        conf['uplink']['port'] = self.info['links'][0]['port']

        conf['database'][0]['host'] = 'jdbc:mysql://127.0.0.1:3306/acidcore?autoReconnect=true'
        conf['database'][0]['name'] = 'acidcore'
        conf['database'][0]['user'] = 'acid'
        conf['database'][0]['pass'] = 'acidpass'

        conf['debug'] = True

        # and writing it out
        with open(new, 'w') as config_file:
            config_file.write(yaml.dump(conf))

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
cp -R {src_folder} {bin_folder}
cd {bin_folder}

cp {config_folder}/pyva/pyva-native/pyva-cpp/make.properties {bin_folder}/pyva/pyva-native/pyva-cpp/

mvn install

ln -s pyva/pyva-native/pyva-cpp/libpyva.so libpyva.so
pip install -r requirements.txt

cp {config_folder}/acid/acidictive.yml {bin_folder}/acid/acidictive.yml
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build.sh')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True
