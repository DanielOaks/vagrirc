#!/usr/bin/env python3
# VagrIRC Virc library
import os
from zipfile import ZipFile

import requests

from .base import BaseServices
from ..utils import get_members


class Anope2Services(BaseServices):
    """Implements support for Anope2 Services."""
    name = 'anope2'
    release = '2.0.1'
    def download_release(self):
        url = 'https://github.com/anope/anope/archive/{}.zip'.format(self.release)
        cache_folder = os.path.join(self.cache_directory, self.release)

        # see if it already exists
        if os.path.exists(cache_folder):
            return True

        # download archive
        tmp_filename = os.path.join(self.cache_directory, 'tmp_download.zip')
        with open(tmp_filename, 'wb') as handle:
            r = requests.get(url, stream=True)

            if not r.ok:
                return False

            ONE_MEGABYTE = 1024 * 1024
            for block in r.iter_content(ONE_MEGABYTE):
                if not block:
                    break
                handle.write(block)

        # unzip into directory
        with ZipFile(tmp_filename, 'r') as source_zip:
            source_zip.extractall(cache_folder, get_members(source_zip))

        # remove temp file
        os.remove(tmp_filename)
