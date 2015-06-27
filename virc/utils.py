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

import networkx as nx


def get_members(zip):
    """get_members for zipfile, stripping common directory prefixes.

    Taken from http://stackoverflow.com/questions/8689938
    """
    parts = []
    for name in zip.namelist():
        if not name.endswith('/'):
            parts.append(name.split('/')[:-1])
    prefix = os.path.commonprefix(parts) or ''
    if prefix:
        prefix = '/'.join(prefix) + '/'
    offset = len(prefix)
    for zipinfo in zip.infolist():
        name = zipinfo.filename
        if len(name) > offset:
            zipinfo.filename = name[offset:]
            yield zipinfo


def nodelist(network):
    """Returns a drawable nodelist (for the concentric circle-based drawing functions of networkx)."""
    # first off, find most largestly connected (hub) server for the center
    center = nx.center(network)
    center = center[0]  # returns a list of centers, and we don't want that

    # and create the layers off that
    added_nodes = [center,]
    shells = [(center,),]  # holds recursive shells

    any_added = True
    while any_added:
        any_added = False
        new_shell = []
        for node in shells[-1]:
            new_neighbors = nx.all_neighbors(network, node)
            for n in new_neighbors:
                if n not in added_nodes:
                    new_shell.append(n)
                    added_nodes.append(n)
                    any_added = True

        if len(new_shell) > 0:
            new_shell = (new_shell)  # make a tuple
            shells.append(new_shell)

    return shells
