#!/usr/bin/env python3
# VagrIRC Virc library
import random
import string


class MapBaseServer:
    """Represents a server in some capacity."""
    hub = False  # connects to more than one other server
    client = False  # connects to clients
    hidden = False  # hidden to clients
    services = False  # provides services

    def __init__(self, software):
        self.links = []
        self.software = software  # name of the software package powering this node
        self.sid = '{}{}{}'.format(random.randint(0,9), random.randint(0,9), random.choice(string.ascii_uppercase))

    def link_to(self, server):
        """Link to the given server."""
        self.links.append(server)
        server.links.append(self)


class MapHubServer(MapBaseServer):
    """Represents a hub server."""
    hub = True
    hidden = True

    def __init__(self, software, for_services=False):
        MapBaseServer.__init__(self, software)
        self.max_server_links = random.randint(2, 3)
        self.for_services = for_services

    def can_add_server(self):
        return len(self.links) + 1 <= self.max_server_links


class MapClientServer(MapBaseServer):
    """Represents a client-facing server."""
    client = True


class MapServicesServer(MapBaseServer):
    """Represents a services server."""
    services = True
    hidden = True


def find_empty_hub(server, ignore_ids=[]):
    """Spiders a network, looking for a hub that can accept connections.

    If none are found, returns None.
    """
    found = None

    for s in server.links:
        if s.sid in ignore_ids:
            continue
        if s.hub:
            if s.can_add_server():
                found = s
                break
            else:
                found = find_empty_hub(s, ignore_ids=[s.sid])
                if found is not None:
                    break

    return found


def find_real_hubs(server, ignore_ids=[]):
    """Find all the hubs in a given network.

    Ignores hubs marked as 'for services'.
    """
    found = []

    if server.hub and server.sid not in ignore_ids:
        found.append(server)

    for s in server.links:
        if s.sid in ignore_ids:
            continue
        if s.hub and not s.for_services:
            found.append(server)
            new_links = find_real_hubs(s, ignore_ids=[s.sid])
            found = found + new_links

    return found
