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
from zipfile import ZipFile

import appdirs
import requests

from .utils import get_members


class ReleaseDownloader:
    """Represents a basic release downloader."""
    name = None
    release = None
    vcs = None
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
        if self.release is None and self.vcs:
            self.release = 'trunk'
        self.source_folder = os.path.join(self.cache_directory, self.release)
        self.external_source_folder = self.name

        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)

        # fill out dl type ourselves if we can
        if self._download_type is None:
            if isinstance(self.url, str) and len(self.url.split('.')) > 1:
                # could also strip out # magic if necessary, later
                self._download_type = self.url.rsplit('.', 1)[-1]

        self.download_release()

    def download_release(self):
        """Download our expected release of the server, if not already cached."""
        if self.url is None:
            return False

        if self.vcs == 'git':
            import git

            return True  # XXX - temp, testing, should not be here
            if os.path.exists(self.source_folder):
                repo = git.Repo(self.source_folder)
                repo.remotes.origin.fetch()
                repo.remotes.origin.pull()
            else:
                repo = git.Repo.init(self.source_folder)
                origin = repo.create_remote('origin', self.url)
                assert origin.exists()
                origin.fetch()
                # track remote branch
                repo.create_head('master', origin.refs.master).set_tracking_branch(origin.refs.master)
                origin.pull()

            for submodule in repo.submodules:
                submodule.update(init=True)

            repo.heads.master.checkout()

        else:
            # see if it already exists
            if os.path.exists(self.source_folder):
                return True

            url = self.url.format(release=self.release)

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


class BaseSoftware(ReleaseDownloader):
    info = {}

    def init_info(self):
        """Initialise user/channel/etc info."""
        ...

    def init_users(self, info):
        """Return a list of 'users' to join to the network, along with commands.

        Used during network provisioning to register accounts with NickServ,
        register and set channel info such as topic, etc.
        """
        return []

    def write_config(self, folder, info):
        """Write config file to the given folder."""
        ...

    def write_build_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write build files to the given folder."""
        ...

    def write_launch_files(self, folder, src_folder, bin_folder, build_folder, config_folder):
        """Write launch files to the given folder."""
        ...


class BaseServer(BaseSoftware):
    _slug_type = 'ircd'


class BaseServices(BaseSoftware):
    _slug_type = 'services'


class BaseServiceBot(BaseSoftware):
    _slug_type = 'servicebot'
