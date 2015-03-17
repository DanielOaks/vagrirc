#!/usr/bin/env python3
# VagrIRC Virc library
import random
import networkx as nx
import matplotlib.pyplot as plt

from . import map
from . import servers
from . import services
from .utils import nodelist

version = '0.0.1'
name_version = 'VagrIRC {}'.format(version)


class VircManager:
    """Can create and map out an IRC network."""
    def __init__(self):
        self.network = None

    def generate(self, ircd_type=None, services_type=None, use_services=True, server_count=1, hub_chance=0.35):
        """Generate the given IRC server map."""
        self.network = map.IrcNetwork()

        # make sure we have a valid ircd
        if ircd_type:
            ircd_type = servers.available[ircd_type]
        else:
            ircd_type = servers.available.values()[0]

        # make sure we have valid services
        if services_type:
            services_type = services.available[services_type]
        else:
            services_type = services.available.values()[0]

        # generate base network
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

        stats = map.network_stats(self.network)

        # draw network map to a file
        try:
            pos = nx.graphviz_layout(self.network, prog='sfdp', args='-Goverlap=false -Gmaxiter=500 -Gcenter=1')
            mov = True
        except:
            nl = nodelist(self.network)
            pos = nx.shell_layout(self.network, nlist=nl)
            mov = False
            print('Warning: Using Shell layout instead of Graphviz layout. Display may not look nice or legible.')

        # core hubs
        # NOTE: we do this because nx.draw seems to apply colours weirdly when the
        #   number of args here matches the number of servers, eg if 3 core hubs
        #   and 3 numbers in colour tuple, apply all sorts of dodgy stuff, etc
        if stats['core_hubs'] == 3:
            core_hub_color = (0.2, 0.3, 0.4, 1.0)
        else:
            core_hub_color = (0.2, 0.3, 0.4)

        nx.draw(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.hub and n.core],
            'edgelist': [],
            'node_color': core_hub_color,
            'node_size': 150,
            'node_shape': 'h',
        })

        # regular hubs
        if stats['normal_hubs'] == 3:
            normal_hub_color = (0.5, 0.6, 0.7, 1.0)
        else:
            normal_hub_color = (0.5, 0.6, 0.7)

        nx.draw(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.hub and not n.core],
            'edgelist': [],
            'node_color': normal_hub_color,
            'node_size': 150,
            'node_shape': 'h',
        })

        # client servers
        if stats['client_servers'] == 3:
            client_color = (0.9, 0.2, 0.3, 1.0)
        else:
            client_color = (0.9, 0.2, 0.3)

        nx.draw(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if not n.hub],
            'edgelist': [],
            'node_color': client_color,
            'node_size': 120,
            'node_shape': 'h',
        })

        nx.draw(self.network, pos, **{
            'nodelist': [],
        })

        # draw labels
        def labelpos(position_dict, x=0, y=0):
            """Modify the given label dict and return the real position dict."""
            new_pos = {}
            # other graph layouts break this pos, so just disable it
            if mov:
                for s in position_dict:
                    new_pos[s] = (position_dict[s][0] + x, position_dict[s][1] + y)
            return new_pos

        # nx.draw_networkx_labels(self.network, labelpos(pos, x=-2), **{
        #     'edgelist': [],
        #     'labels': {s: s.sid for s in self.network.nodes()},
        #     'font_family': 'monospace',
        #     'font_size': 4,
        #     'font_color': [0, 0, 0],
        # })

        plt.savefig('Server Map.pdf')
