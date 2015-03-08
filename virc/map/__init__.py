#!/usr/bin/env python3
# VagrIRC Virc library


class MapBaseServer:
    """Represents a server in some capacity."""
    hub = False  # connects to more than one other server
    client = False  # connects to clients
    hidden = False  # hidden to clients
    services = False  # provides services

    def __init__(self):
        self.links = []


class MapHubServer(MapBaseServer):
    """Represents a hub server."""
    hub = True
    hidden = True


class MapClientServer(MapBaseServer):
    """Represents a client-facing server."""
    client = True


class MapServicesServer(MapBaseServer):
    """Represents a services server."""
    services = True
    hidden = True
