#!/usr/bin/env python3
# VagrIRC Virc library
import random
import string
import networkx as nx


class IrcNetwork(nx.Graph):
    """Represents an IRC network."""
    ...


class MapBaseServer:
    """Represents a server in some capacity."""
    hub = False  # connects to more than one other server
    core = False  # whether this is a 'core' hub server
    client = False  # connects to clients
    hidden = False  # hidden to clients
    services = False  # provides services

    def __init__(self, network, software):
        self.network = network
        self.software = software  # name of the software package powering this node

        self.network.add_node(self)

    def link_to(self, server):
        """Link to the given server."""
        self.network.add_edge(self, server)

    def can_add_client_server(self):
        """Whether we can add a client server to this server."""
        return False

    def can_add_hub_server(self):
        """Whether we can add a hub server to this server."""
        return False


class MapHubServer(MapBaseServer):
    """Represents a hub server."""
    hub = True
    hidden = True

    def __init__(self, network, software, for_services=False):
        MapBaseServer.__init__(self, network, software)
        self.max_client_server_links = random.randint(2, 3)
        self.max_hub_server_links = 1
        self.for_services = for_services

    def can_add_client_server(self):
        """Whether we can add a client server to this server."""
        links = [edge for edge in self.network.edges([self]) if edge[1].client]

        return len(links) + 1 <= self.max_client_server_links

    def can_add_hub_server(self):
        """Whether we can add a_hub server to this server."""
        links = [edge for edge in self.network.edges([self]) if edge[1].hub]

        return len(links) + 1 <= self.max_hub_server_links


class MapCoreHubServer(MapHubServer):
    core = True

    def __init__(self, network, software):
        MapHubServer.__init__(self, network, software, for_services=False)
        self.max_client_server_links = 0  # random.randint(-5, 1)
        if self.max_client_server_links < 0:
            self.max_client_server_links = 0

        self.max_hub_server_links = random.randint(3, 7)


class MapClientServer(MapBaseServer):
    """Represents a client-facing server."""
    client = True


class MapServicesServer(MapBaseServer):
    """Represents a services server."""
    services = True
    hidden = True


def find_empty_hub(network, is_core=False):
    """Spiders a network, looking for a hub that can accept connections.

    If none are found, returns None.
    """
    for server in network.nodes():
        if is_core:
            if server.can_add_hub_server():
                return server
        else:
            if server.can_add_client_server():
                return server


def find_real_hubs(network, is_core=False):
    """Find all the hubs in a given network.

    Ignores hubs marked as 'for services'.
    """
    found = []

    for server in network.nodes():
        if server.hub and not server.for_services:
            if is_core is not None and server.core != is_core:
                continue
            found.append(server)

    return found


def network_stats(network):
    """Counts the types of servers in the given network."""
    stats = {
        'core_hubs': 0,
        'normal_hubs': 0,
        'service_hubs': 0,
        'client_servers': 0,
        'services_servers': 0,

        'shown': 0,
        'hidden': 0,
    }

    for server in network.nodes():
        if server.client:
            stats['client_servers'] += 1
        elif server.hub and server.for_services:
            stats['service_hubs'] += 1
        elif server.hub and server.core:
            stats['core_hubs'] += 1
        elif server.hub:
            stats['normal_hubs'] += 1
        elif server.services:
            stats['services_servers'] += 1

        if server.hidden:
            stats['hidden'] += 1
        else:
            stats['shown'] += 1

    return stats
