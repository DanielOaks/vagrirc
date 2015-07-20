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
import yaml
import shutil

from ..base import BaseServiceBot
from ..utils import generate_pass


class MooServiceBot(BaseServiceBot):
    """Rizon's Moo Bot."""
    name = 'moo'
    vcs = 'git'
    url = 'https://gitlab.com/rizon/moo.git'

    requires = {
        'ircd': 'plexus4',
        'services': 'anope2',
    }

    def init_info(self, config_folder=None):
        """Create our info."""
        self.info['users'] = {}

        # load users from config file
        config_filename = os.path.join(config_folder, 'moo.yml')
        if not os.path.exists(config_filename):
            return
        with open(config_filename, 'r') as config_file:
            config_data = config_file.read()

        conf = yaml.load(config_data)

        # moo
        info = conf['general']

        nick = info['nick']
        user = info['ident']
        ns_password = info['nickserv']['pass']
        oper_name = info['oper']['name']
        oper_password = info['oper']['pass']

        self.info['users'][nick] = {
            'services': {
                'password': ns_password,
                'level': 'moo service bot',
            },
            'ircd': {
                'oper': True,
                'oper_name': oper_name,
                'oper_pass': oper_password,
            },
            'username': user,
        }

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        modules_folder = os.path.join(folder, 'modules')

        if not os.path.exists(modules_folder):
            os.makedirs(modules_folder)

        config_files = {
            'moo': [
                os.path.join(self.source_folder, 'moo.yml.template'),
                os.path.join(folder, 'moo.yml'),
            ],
            'grapher': [
                os.path.join(self.source_folder, 'grapher', 'grapher.yml.template'),
                os.path.join(modules_folder, 'grapher.yml'),
            ],
            'vote': [
                os.path.join(self.source_folder, 'vote', 'vote.yml.template'),
                os.path.join(modules_folder, 'vote.yml'),
            ],
            'antiidle': [
                os.path.join(self.source_folder, 'antiidle', 'antiidle.yml.template'),
                os.path.join(modules_folder, 'antiidle.yml'),
            ],
            'core': [
                os.path.join(self.source_folder, 'core', 'core.yml.template'),
                os.path.join(modules_folder, 'core.yml'),
            ],
            'dnsbl': [
                os.path.join(self.source_folder, 'dnsbl', 'dnsbl.yml.template'),
                os.path.join(modules_folder, 'dnsbl.yml'),
            ],
            'logging': [
                os.path.join(self.source_folder, 'logging', 'logging.yml.template'),
                os.path.join(modules_folder, 'logging.yml'),
            ],
            'osflood': [
                os.path.join(self.source_folder, 'osflood', 'osflood.yml.template'),
                os.path.join(modules_folder, 'osflood.yml'),
            ],
        }

        # moo config file
        # # # #
        orig, new = config_files['moo']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        conf = yaml.load(config_data)

        # setting info
        conf['general']['server'] = '127.0.0.1'
        conf['mail']['path'] = '/tmp/idontexistthisisjusttomakemoonotsendmail'

        conf['general']['nickserv']['pass'] = generate_pass()
        conf['general']['oper']['pass'] = generate_pass()

        conf['plugins'].remove('proxyscan')
        conf['plugins'].remove('servercontrol')
        conf['plugins'].remove('servermonitor')
        conf['plugins'].remove('tickets')
        conf['plugins'].remove('commits')

        # and writing it out
        with open(new, 'w') as config_file:
            config_file.write(yaml.dump(conf))

        # grapher
        # # # #
        orig, new = config_files['grapher']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        graph_folder = '{bin_folder}/moo/graphs'.format(bin_folder='/irc/bin/servicebot_moo')
        config_data = config_data.replace('/home/adam/rizon/moo/graphs', graph_folder)

        with open(new, 'w') as config_file:
            config_file.write(config_data)

        # vote
        # # # #
        orig, new = config_files['vote']
        with open(orig, 'r') as config_file:
            config_data = config_file.read()

        # don't want it actually sending emails
        config_data = config_data.replace('rizon.net', 'example.com')

        with open(new, 'w') as config_file:
            config_file.write(config_data)

        # other config files
        # # # #
        for name in ['antiidle', 'core', 'dnsbl', 'logging', 'osflood']:
            orig, new = config_files[name]

            shutil.copyfile(orig, new)

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
mkdir -p {bin_folder}
cp -R {src_folder}/. {bin_folder}
cd {bin_folder}

cp {config_folder}/moo.yml {bin_folder}/moo.yml
cp {config_folder}/modules/antiidle.yml {bin_folder}/antiidle.yml
cp {config_folder}/modules/core.yml {bin_folder}/core.yml
cp {config_folder}/modules/dnsbl.yml {bin_folder}/dnsbl.yml
cp {config_folder}/modules/grapher.yml {bin_folder}/grapher.yml
cp {config_folder}/modules/logging.yml {bin_folder}/logging.yml
cp {config_folder}/modules/osflood.yml {bin_folder}/osflood.yml
cp {config_folder}/modules/vote.yml {bin_folder}/vote.yml

mvn package
""".format(src_folder=src_folder, bin_folder=bin_folder,
           build_folder=build_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        # foreground
        launch_file = """#!/usr/bin/env sh

cd {bin_folder}
JAR=moo/target/moo-moo-3.0-SNAPSHOT-jar-with-dependencies.jar
ARGS='-XX:+HeapDumpOnOutOfMemoryError -Xmx16M'
java $ARGS -jar $JAR"""

        launch_file = launch_file.format(src_folder=src_folder, bin_folder=bin_folder,
                                         config_folder=config_folder)

        launch_filename = os.path.join(folder, 'launch_foreground')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file + '\n')

        # regular
        launch_file = launch_file + " >moo.log 2>&1 &\n"

        launch_filename = os.path.join(folder, 'launch')

        with open(launch_filename, 'w') as l_file:
            l_file.write(launch_file)

        return True
