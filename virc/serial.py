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

import yaml
import networkx as nx

from . import map

extension = 'yaml'


def dump(network):
    """Serialize the given network map to a string."""
    info = network.info
    info['servers'] = {}
    info['links'] = {}

    # servers
    for server in network.nodes():
        server_info = {}

        for attr in ['software', 'client', 'hidden', 'services', 'service_bot']:
            if not hasattr(server, attr):
                continue

            value = getattr(server, attr, None)

            if isinstance(value, bool):
                if value:
                    server_info[attr] = True
                else:
                    server_info[attr] = False
            else:
                server_info[attr] = value

        server_info['info'] = server.info

        info['servers'][server.info['sid']] = server_info

    # links
    for link in network.edges():
        link_nx_info = nx.get_edge_attributes(network, link)[link]
        link_info = {}
        for name, dic in link_nx_info:
            link_info[name] = dic

        sids = tuple(sorted([link[0].info['sid'], link[1].info['sid']]))

        info['links'][sids] = link_info

    # serializing
    return yaml.dump(info, default_flow_style=False)


def load(in_str):
    """Load the given network from the given map."""
    servers = {}
    network = map.IrcNetwork()

    # WARNING: THIS LOADING METHOD IS UNSAFE,
    #   BUT REQUIRED BECAUSE OTHERWISE YAML DOES NOT UNDERSTAND THE TUPLE
    #   DICTIONARY KEYS AND BREAKS. THANKS YAML.
    nw_info = yaml.load(in_str)

    if not nw_info:
        network.info = {}
        return network

    for sid, info in nw_info.get('servers', {}).items():
        software = info.get('software', None)
        client = info.get('client', False)
        hidden = info.get('hidden', False)
        services = info.get('services', False)
        service_bot = info.get('service_bot', False)

        if client:
            server = map.MapClientServer(network, software)
        elif services:
            server = map.MapServicesServer(network, software)
        elif service_bot:
            server = map.MapServiceBot(network, software)
        else:
            print(sid, info)
            raise Exception('Something broke!')

        if hidden:
            server.hidden = True

        server.info = info.get('info', {})

        servers[sid] = server

    for link, info in nw_info.get('links', {}).items():
        link_info = []
        for name, val in info.items():
            link_info.append((name, val))
        link_info = tuple(link_info)

        servers[link[0]].link_to(servers[link[1]], info=link_info)

    # set network info
    if 'servers' in nw_info:
        del nw_info['servers']
    if 'links' in nw_info:
        del nw_info['links']

    network.info = nw_info

    return network
