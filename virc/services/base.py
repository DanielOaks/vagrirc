#!/usr/bin/env python3
# VagrIRC Virc library
import os

import appdirs


class BaseServices:
    """Represents a services package."""
    name = None
    release = None
    def __init__(self):
        if self.name is None:
            raise Exception('Class variable `name` must be overridden')

        appname = 'vagrirc'
        appauthor = 'danieloaks'
        self.base_cache_directory = appdirs.user_cache_dir(appname, appauthor)

        # server_* slug here to stop possible collisions with services/etc names
        slug = 'services_{}'.format(self.name)
        self.cache_directory = os.path.join(self.base_cache_directory, slug)

        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)

    def download_release(self):
        """Download our expected release of the server, if not already cached."""
        ...

    def write_config(self, filename, info):
        """Write config file to the given filename."""
        ...
