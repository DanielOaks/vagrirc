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
]

config_regexes = {
    'name': (re.compile(r'(serverinfo \{\n\s*name = )[^\;]+(;)'), r'\1"{value}"\2'),
    'sid': (re.compile(r'(\n\s*sid = )"[0-9a-zA-Z]{3}"(;)'), r'\1"{value}"\2'),
    'client_port': (re.compile(r'(\nauth \{[^\}]+\};)'), r'\1\nlisten{{\n    port = {value};\n}};')
}


class HybridServer(BaseServer):
    """Implements support for the Hybrid IRCd."""
    name = 'hybrid'
    release = '8.2.5'
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

        # inserting actual values
        for key, value in self.info.items():
            if key in config_regexes:
                regex, sub = config_regexes[key]
                sub = sub.format(value=value)
                config_data = regex.sub(sub, config_data)
            else:
                print('hybrid regex: skipping key:', key)

        # writing out config file
        output_config_dir = os.path.join(folder, 'etc')

        if not os.path.exists(output_config_dir):
            os.makedirs(output_config_dir)

        output_config_file = os.path.join(output_config_dir, 'reference.conf')
        with open(output_config_file, 'w') as config_file:
            config_file.write(config_data)
