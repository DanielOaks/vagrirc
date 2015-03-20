#!/usr/bin/env python3
# VagrIRC Virc library
import os
from zipfile import ZipFile

import appdirs
import requests

from .utils import get_members


class ReleaseDownloader:
    """Represents a basic release downloader."""
    name = None
    release = None
    url = None
    _download_type = None
    _slug_type = None

    def __init__(self):
        if self.name is None:
            raise Exception('Class variable `name` must be overridden')

        appname = 'vagrirc'
        appauthor = 'danieloaks'
        self.base_cache_directory = appdirs.user_cache_dir(appname, appauthor)

        # server_* slug here to stop possible collisions with services/etc names
        slug = '{}_{}'.format(self._slug_type, self.name)
        self.cache_directory = os.path.join(self.base_cache_directory, slug)

        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)

        # fill out dl type ourselves if we can
        if self._download_type is None:
            if isinstance(self.url, str) and len(self.url.split('.')) > 1:
                # could also strip out # magic if necessary, later
                self._download_type = self.url.rsplit('.', 1)[-1]

    def download_release(self):
        """Download our expected release of the server, if not already cached."""
        if self.url is None:
            return False

        url = self.url.format(release=self.release)
        self.source_folder = os.path.join(self.cache_directory, self.release)

        # see if it already exists
        if os.path.exists(self.source_folder):
            return True

        # download file
        tmp_filename = os.path.join(self.cache_directory, 'tmp_download.{}'.format(self._download_type))
        with open(tmp_filename, 'wb') as handle:
            r = requests.get(url, stream=True)

            if not r.ok:
                return False

            ONE_MEGABYTE = 1024 * 1024
            for block in r.iter_content(ONE_MEGABYTE):
                if not block:
                    break
                handle.write(block)

        # extract into directory
        if self._download_type == 'zip':
            with ZipFile(tmp_filename, 'r') as source_zip:
                source_zip.extractall(self.source_folder, get_members(source_zip))
        else:
            raise Exception('Cannot extract/parse given download type')

        # remove temp file
        os.remove(tmp_filename)


class BaseServer(ReleaseDownloader):
    _slug_type = 'server'
    info = {}

    def write_config(self, filename):
        """Write config file to the given filename."""
        ...


class BaseServices(ReleaseDownloader):
    _slug_type = 'services'

    def write_config(self, filename):
        """Write config file to the given filename."""
        ...
