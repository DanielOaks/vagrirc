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
    client = False  # connects to clients
    hidden = False  # hidden to clients
    services = False  # provides services

    def __init__(self, network, software):
        self.network = network
        self.software = software  # name of the software package powering this node
        self.sid = '{}{}{}'.format(random.randint(0,9), random.randint(0,9), random.choice(string.ascii_uppercase))

        self.network.add_node(self)

    def link_to(self, server):
        """Link to the given server."""
        self.network.add_edge(self, server)

    def can_add_server(self):
        """Whether we can add a client server to this server."""
        return False


class MapHubServer(MapBaseServer):
    """Represents a hub server."""
    hub = True
    hidden = True

    def __init__(self, network, software, for_services=False):
        MapBaseServer.__init__(self, network, software)
        self.max_server_links = random.randint(2, 3)
        self.for_services = for_services

    def can_add_server(self):
        """Whether we can add a client server to this server."""
        links = self.network.edges([self])

        return len(links) + 1 <= self.max_server_links


class MapClientServer(MapBaseServer):
    """Represents a client-facing server."""
    client = True


class MapServicesServer(MapBaseServer):
    """Represents a services server."""
    services = True
    hidden = True


def find_empty_hub(network):
    """Spiders a network, looking for a hub that can accept connections.

    If none are found, returns None.
    """
    for server in network.nodes():
        if server.can_add_server():
            return server


def find_real_hubs(network):
    """Find all the hubs in a given network.

    Ignores hubs marked as 'for services'.
    """
    found = []

    for server in network.nodes():
        if server.hub and not server.for_services:
            found.append(server)

    return found
