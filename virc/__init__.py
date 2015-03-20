#!/usr/bin/env python3
# VagrIRC Virc library
import os
import random
import string

import names
import networkx as nx
import matplotlib.pyplot as plt

from . import map
from . import serial
from . import servers
from . import services
from .utils import nodelist

version = '0.0.1'
name_version = 'VagrIRC {}'.format(version)


class VircManager:
    """Can create and map out an IRC network."""
    def __init__(self, irc_dir=None):
        self.network = None

        if irc_dir is None:
            irc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'irc'))
        self.irc_dir = irc_dir

        if not os.path.exists(self.irc_dir):
            os.makedirs(self.irc_dir)

    def generate(self, ircd_type=None, services_type=None, use_services=True, server_count=1):
        """Generate the given IRC server map."""
        self.network = map.IrcNetwork()

        # make sure we have a valid ircd
        if ircd_type:
            ircd_type = servers.available[ircd_type]().name
        else:
            ircd_type = servers.available.values()[0]().name

        # make sure we have valid services
        if services_type:
            services_type = services.available[services_type]().name
        else:
            services_type = services.available.values()[0]().name

        # generate network
        #
        for i in range(server_count):
            # first run, only a single server!
            if len(self.network.nodes()) < 1:
                map.MapClientServer(self.network, ircd_type)
                continue

            # second server is always a hub server
            if len(self.network.nodes()) < 2:
                only_client_server = self.network.nodes()[0]
                new_hub = map.MapHubServer(self.network, ircd_type)
                new_hub.link_to(only_client_server)
                continue

            # network stats
            stats = map.network_stats(self.network)

            # see if we can add a new client server
            empty_hub = map.find_empty_hub(self.network)

            # add our own hub
            if empty_hub is None:
                normal_hubs = map.find_real_hubs(self.network)
                empty_core_hub = map.find_empty_hub(self.network, is_core=True)

                if empty_core_hub is None:
                    if stats['core_hubs'] > 0:
                        hubs = map.find_real_hubs(self.network, is_core=True)
                    else:
                        hubs = normal_hubs

                    empty_core_hub = map.MapCoreHubServer(self.network, ircd_type)
                    empty_core_hub.link_to(random.choice(hubs))

                # create new hub and link it to the given core hub
                new_hub = map.MapHubServer(self.network, ircd_type)
                new_hub.link_to(empty_core_hub)
                continue

            # else, add a new client server!
            new_client_server = map.MapClientServer(self.network, ircd_type)
            new_client_server.link_to(empty_hub)
            continue

        # add a services server
        stats = map.network_stats(self.network)
        if stats['core_hubs'] > 0:
            hubs = map.find_real_hubs(self.network, is_core=True)
        elif stats['normal_hubs'] > 0:
            hubs = map.find_real_hubs(self.network)
        else:
            hubs = self.network.nodes()  # just grab the client server

        new_services = map.MapServicesServer(self.network, services_type)
        new_services.link_to(random.choice(hubs))

        # calc stats
        stats = map.network_stats(self.network)

        # draw network map to a file
        #
        node_edge_color = '#cccccc'

        try:
            pos = nx.graphviz_layout(self.network, prog='sfdp', args='-Goverlap=false -Gmaxiter=500 -Gcenter=1')
            mov = True
        except:
            nl = nodelist(self.network)
            pos = nx.shell_layout(self.network, nlist=nl)
            mov = False
            print('Warning: Using Shell layout instead of Graphviz layout. Display may not look nice or legible.')

        # services
        # NOTE: we do this because nx.draw seems to apply colours weirdly when the
        #   number of args here matches the number of servers, eg if 3 core hubs
        #   and 3 numbers in colour tuple, apply all sorts of dodgy stuff, etc
        if stats['services_servers'] == 3:
            services_color = (0.7, 0.9, 0.7, 1.0)
        else:
            services_color = (0.7, 0.9, 0.7)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.services],
            'node_color': services_color,
            'node_size': 150,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # core hubs
        if stats['core_hubs'] == 3:
            core_hub_color = (0.5, 0.6, 0.7, 1.0)
        else:
            core_hub_color = (0.5, 0.6, 0.7)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.hub and n.core],
            'node_color': core_hub_color,
            'node_size': 150,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # regular hubs
        if stats['normal_hubs'] == 3:
            normal_hub_color = (0.8, 0.8, 0.9, 1.0)
        else:
            normal_hub_color = (0.8, 0.8, 0.9)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.hub and not n.core],
            'node_color': normal_hub_color,
            'node_size': 150,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # client servers
        if stats['client_servers'] == 3:
            client_color = (0.9, 0.7, 0.7, 1.0)
        else:
            client_color = (0.9, 0.7, 0.7)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if not n.hub and not n.services],
            'node_color': client_color,
            'node_size': 120,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # lines
        nx.draw(self.network, pos, **{
            'nodelist': [],
            'edge_color': '#bbbbbb',
        })

        # server configs
        #

        # assign server names and client ports
        current_client_port = 6667
        used_names = []
        used_sids = []

        for server in self.network.nodes():
            info = {}

            # generate name
            server_name = names.get_first_name().lower()
            while server_name in used_names:
                server_name = names.get_first_name().lower()
            used_names.append(server_name)

            info['name'] = server_name

            if server.hub:
                info['name'] += '_hub'
            elif server.services:
                info['name'] += '_services'

            # generate sid
            sid = '72A'
            while sid in used_sids:
                sid = '{}{}{}'.format(random.randint(0,9), random.randint(0,9), random.choice(string.ascii_uppercase))
            used_sids.append(sid)

            info['sid'] = sid

            # port for clients to connect on
            if server.client:
                info['client_port'] = current_client_port
                current_client_port += 1

            # and set info
            server.info = info

        # assign ports and passwords for server links
        current_server_port = 10000
        while current_server_port <= current_client_port:
            current_server_port += 500

        used_passwords = []

        for link in self.network.edges():
            info = []

            # port for things to connect on
            info.append(('port', current_server_port))
            current_server_port += 1

            # generate link password
            password = '{}_{}'.format(names.get_last_name().lower(), random.randint(0, 9999))
            while password in used_passwords or len(password) < 9:
                password = '{}_{}'.format(names.get_last_name().lower(), random.randint(0, 9999))

            info.append(('password', password))

            nx.set_edge_attributes(self.network, link, info)

        # labels
        nx.draw_networkx_labels(self.network, pos, **{
            'edgelist': [],
            'labels': {s: s.info['name'] for s in self.network.nodes()},
            'font_family': 'monospace',
            'font_size': 6,
            'font_color': [0.2, 0.2, 0.2],
        })

        map_filename = os.path.join(self.irc_dir, 'Server Map.pdf')
        plt.savefig(map_filename)

        # save network
        serial_filename = os.path.join(self.irc_dir, 'map.yaml')
        serial.save(serial_filename, self.network)
