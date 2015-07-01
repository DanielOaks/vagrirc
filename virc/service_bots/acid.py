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
import configparser

import yaml

from ..base import BaseServiceBot
from ..utils import generate_pass


class AcidServiceBot(BaseServiceBot):
    """Implements support for the Hybrid IRCd."""
    name = 'acid'
    vcs = 'git'
    url = 'https://gitlab.com/rizon/acid.git'

    def init_info(self, config_folder=None):
        """Create our info."""
        self.info['users'] = {}

        # load users from config file
        config_filename = os.path.join(config_folder, 'pyva.yml')
        if not os.path.exists(config_filename):
            return
        with open(config_filename, 'r') as config_file:
            config_data = config_file.read()

        conf = yaml.load(config_data)

        # loop through users
        for info in conf['clients']:
            nick = info['nick']
            user = info['user']
            password = info['nspass']

            self.info['users'][nick] = {
                'services': {
                    'password': password,
                    'level': 'acid service bot',
                },
                'username': user,
            }

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        config_files = {
            'pyva-native': [
                os.path.join(self.source_folder, 'pyva', 'pyva-native', 'pyva-cpp', 'make.example.properties'),
                os.path.join(folder, 'make.properties'),
            ],
            'acid': [
                os.path.join(self.source_folder, 'acid', 'acidictive.example.yml'),
                os.path.join(folder, 'acidictive.yml'),
            ],
            'pyva': [
                os.path.join(self.source_folder, 'pyva', 'pyva.example.yml'),
                os.path.join(folder, 'pyva.yml'),
            ],
            'conf': [
                os.path.join(self.source_folder, 'pyva', 'config.example.ini'),
                os.path.join(folder, 'config.ini'),
            ],
            'sql': os.path.join(folder, 'acid.sql'),
        }

        # pyva-native compilation makefile
        orig, new = config_files['pyva-native']
        shutil.copyfile(orig, new)

        # pyva config file
        # # # #
        orig, new = config_files['pyva']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        conf = yaml.load(config_data)

        # loop through users
        for i, nfo in enumerate(list(conf['clients'])):
            conf['clients'][i]['nspass'] = generate_pass()

        # and writing it out
        with open(new, 'w') as config_file:
            config_file.write(yaml.dump(conf))

        # aciditive config file
        # # # #
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
        conf['serverinfo']['name'] = 'acid.dnt'

        # and writing it out
        with open(new, 'w') as config_file:
            config_file.write(yaml.dump(conf))

        # config.ini config file
        # # # #
        orig, new = config_files['conf']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        conf = configparser.ConfigParser()
        conf.read_string(config_data, orig)

        # setting info
        conf['database']['host'] = '127.0.0.1'
        conf['database']['user'] = 'pyps'
        conf['database']['passwd'] = 'marleymoo'
        conf['database']['db'] = 'pypsd'

        # and writing it out
        with open(new, 'w') as config_file:
            conf.write(config_file)

        # sql file
        # # # #
        sql_lines = []
        for name, info in info['users'].items():
            if info.get('level', None) == 'root':
                name = name.replace('\\', '\\\\').replace('"', '\\"')  # XXX - really bad escaping
                sql_lines.append('INSERT IGNORE INTO `access` (user,flags) VALUES ("{}",1)\n'.format(name))

        with open(config_files['sql'], 'w') as sql_file:
            sql_file.write('\n'.join(sql_lines))

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
mkdir -p {bin_folder}
cp -R {src_folder}/* {bin_folder}
cd {bin_folder}

cp {config_folder}/make.properties {bin_folder}/pyva/pyva-native/pyva-cpp/

mvn install

ln -s pyva/pyva-native/pyva-cpp/libpyva.so libpyva.so
sudo pip2.7 install -r pyva/requirements.txt --allow-external py-dom-xpath --allow-unverified py-dom-xpath

cp {config_folder}/acidictive.yml {bin_folder}/acidictive.yml
cp {config_folder}/pyva.yml {bin_folder}/pyva.yml
cp {config_folder}/config.ini {bin_folder}/config.ini

mysql -u 'acid' --password=acidpass --database=acidcore < {bin_folder}/acid/acidcore.sql
mysql -u 'acid' --password=acidpass --database=acidcore < {config_folder}/acid.sql
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        launch_file = """#!/usr/bin/env sh

cd {bin_folder}
JAR=acid/target/acid-acid-4.0-SNAPSHOT-jar-with-dependencies.jar
LD_PRELOAD="/usr/lib64/libpython2.7.so" java -XX:+HeapDumpOnOutOfMemoryError -Xms64m -Xmx256m -jar $JAR >geoserv.log 2>&1 &
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
