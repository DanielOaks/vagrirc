#!/usr/bin/env python3
# VagrIRC Virc library
import random

from . import map
from . import servers
from . import services

version = '0.0.1'
name_version = 'VagrIRC {}'.format(version)


class VircManager:
    """Can create and map out an IRC network."""
    def __init__(self):
        self.network = None

    def generate(self, ircd_type=None, services_type=None, use_services=True, server_count=1, hub_chance=0.35):
        """Generate the given IRC server map."""
        # make sure we have a valid ircd
        if ircd_type:
            ircd_type = servers.available[ircd_type]
        else:
            ircd_type = servers.available[0]

        # make sure we have valid services
        if services_type:
            services_type = services.available[services_type]
        else:
            services_type = services.available[0]

        # generate base network
        for i in range(server_count):
            # first run, only a single server!
            if self.network is None:
                self.network = map.MapClientServer(ircd_type)
                continue

            # second server is always a hub server
            if len(self.network.links) < 1:
                self.network.links.append(map.MapHubServer(ircd_type))
                continue

            # see if we can add a new client server
            empty_hub = map.find_empty_hub(self.network)

            # add our own hub
            if empty_hub is None:
                hubs = map.find_real_hubs(self.network)

                # create new hub and link it to a random existing one
                new_hub = map.MapHubServer(ircd_type)
                new_hub.link_to(random.choice(hubs))

                continue

            # else, add a new client server!
            new_client_server = map.MapClientServer(ircd_type)
            new_client_server.link_to(empty_hub)
            continue
