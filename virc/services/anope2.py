#!/usr/bin/env python3
# VagrIRC Virc library
import os

from ..base import BaseServices


class Anope2Services(BaseServices):
    """Implements support for Anope2 Services."""
    name = 'anope2'
    release = '2.0.1'
    url = 'https://github.com/anope/anope/archive/{release}.zip'

    def write_config(self, folder):
        """Write config file to the given folder."""
        print('write config!', self.source_folder, folder)
        if not os.path.exists(folder):
            os.makedirs(folder)

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        build_file = """#!/usr/bin/env sh
cd {src_folder}

test -d build || mkdir build
cd build

cmake '-DINSTDIR:STRING={bin_folder}' -DCMAKE_BUILD_TYPE:STRING=DEBUG -DUSE_RUN_CC_PL:BOOLEAN=OFF -DUSE_PCH:BOOLEAN=OFF ..

make
make install
""".format(src_folder=src_folder, bin_folder=bin_folder, config_folder=config_folder)

        build_filename = os.path.join(folder, 'build.sh')

        with open(build_filename, 'w') as b_file:
            b_file.write(build_file)

        return True
