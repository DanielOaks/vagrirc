#!/usr/bin/env python3
# VagrIRC Virc library
import os

import yaml
import networkx as nx

from . import map

extension = 'yaml'


def save(filename, network):
    """Save the given network map to a file."""
    info = {
        'servers': {},
        'links': {},
    }

    # servers
    for server in network.nodes():
        server_info = server.info

        server_info['software'] = server.software

        for attr in ['hub', 'core', 'client', 'hidden', 'services']:
            if getattr(server, attr, False):
                server_info[attr] = True

        info['servers'][server_info['sid']] = server_info

    # links
    for link in network.edges():
        link_nx_info = nx.get_edge_attributes(network, link)[link]
        link_info = {}
        for name, dic in link_nx_info:
            link_info[name] = dic
        
        sids = tuple(sorted([link[0].info['sid'], link[1].info['sid']]))
        
        info['links'][sids] = link_info

    # writing to file
    with open(filename, 'w') as outfile:
        outfile.write(yaml.dump(info, default_flow_style=False))
