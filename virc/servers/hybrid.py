#!/usr/bin/env python3
# VagrIRC Virc library
import os

from ..base import BaseServer


class HybridServer(BaseServer):
    """Implements support for the Hybrid IRCd."""
    name = 'hybrid'
    release = '8.2.5'
    url = 'https://github.com/ircd-hybrid/ircd-hybrid/archive/{release}.zip'

    def write_config(self, filename):
        """Write config file to the given filename."""
        print(self.release_folder, filename)
