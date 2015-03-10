#!/usr/bin/env python3
# VagrIRC Virc library
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
