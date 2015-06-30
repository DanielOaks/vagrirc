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

import os
import json
import random
import string
import shutil

import networkx as nx
import matplotlib.pyplot as plt

from . import map
from . import serial
from . import servers
from . import services
from . import service_bots
from .utils import nodelist, generate_pass

version = '0.0.1'
name_version = 'VagrIRC {}'.format(version)

INIT_FILE_TEMPLATE = '''#!/usr/bin/env python3
{lines}
'''


class VircManager:
    """Can create and map out an IRC network."""
    def __init__(self, irc_dir=None):
        self.network = None

        if irc_dir is None:
            irc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'irc'))
        self.irc_dir = irc_dir

        if not os.path.exists(self.irc_dir):
            os.makedirs(self.irc_dir)

        self.map_filename = os.path.join(self.irc_dir, 'Server Map.pdf')
        self.serial_filename = os.path.join(self.irc_dir, 'map.yaml')
        self.configs_base_dir = os.path.join(self.irc_dir, 'configs')
        self.build_base_dir = os.path.join(self.irc_dir, 'build')
        self.launch_base_dir = os.path.join(self.irc_dir, 'launch')
        self.init_base_dir = os.path.join(self.irc_dir, 'init')
        self.src_base_dir = os.path.join(self.irc_dir, 'src')
        self.bin_base_dir = os.path.join(self.irc_dir, 'bin')

        self.network_name = 'VagrIRC'

    def save_network_map(self):
        with open(self.serial_filename, 'w') as serial_file:
            serial_file.write(serial.dump(self.network))

    def load_network_map(self):
        with open(self.serial_filename, 'r') as serial_file:
            self.network = serial.load(serial_file.read())

    def write_init_files(self):
        """Write necessary init files for our software."""
        # remove old config files
        if os.path.exists(self.init_base_dir):
            shutil.rmtree(self.init_base_dir)
        init_base = os.path.join('environment', 'init_base')  # XXX - dodgy
        shutil.copytree(init_base, self.init_base_dir)

        # info
        server_list = self.server_list()
        info = self.info_from_server_list(server_list)

        # users
        host_init_users_file = os.path.join(self.init_base_dir, 'users.json')
        users = []

        for node, server in server_list:
            new_users = server.init_users(info)

            if node.services:
                new_users.extend(users)
                users = new_users
            else:
                users.extend(new_users)

        with open(host_init_users_file, 'w') as users_file:
            users_file.write(json.dumps(users, sort_keys=True, indent=4, separators=(',', ': ')))

    def write_build_files(self):
        """Write necessary build files for our software."""
        # remove old config files
        if os.path.exists(self.build_base_dir):
            shutil.rmtree(self.build_base_dir)
        os.makedirs(self.build_base_dir)
        if os.path.exists(self.launch_base_dir):
            shutil.rmtree(self.launch_base_dir)
        os.makedirs(self.launch_base_dir)

        # build file links
        build_files = []
        launch_core_files = []
        launch_rest_files = []

        for node, server in self.server_list():
            server_build_folder = os.path.join(self.build_base_dir, server.slug)
            server_launch_folder = os.path.join(self.launch_base_dir, server.slug)
            server_bin_folder = os.path.join('/irc/bin', server.slug)
            server_src_folder = os.path.join('/irc/src', server.slug)
            guest_build_folder = os.path.join('/irc/build', server.slug)
            guest_config_folder = os.path.join('/irc/configs', server.slug)

            # build folder
            os.makedirs(server_build_folder)

            bf = server.write_build_files(server_build_folder,
                                          server_src_folder,
                                          server_bin_folder,
                                          guest_build_folder,
                                          guest_config_folder,)

            if bf:
                build_file = os.path.join('/irc/build', server.slug, 'build')
                build_files.append(build_file)

            # launch folder
            os.makedirs(server_launch_folder)

            lf = server.write_launch_files(server_launch_folder,
                                          server_src_folder,
                                          server_bin_folder,
                                          guest_build_folder,
                                          guest_config_folder,)

            if lf:
                launch_file = os.path.join('/irc/launch', server.slug, 'launch')
                # XXX - to create a proper dependency manager solution here
                # or just be lazy and do a launch priority

                # init launch files
                if node.client:
                    launch_core_files = [launch_file] + launch_core_files
                elif node.services:
                    launch_core_files.append(launch_file)
                else:
                    launch_rest_files.append(launch_file)

        # write build files
        with open(os.path.join(self.build_base_dir, 'build'), 'w') as build_file:
            build_file.write('#!/usr/bin/env sh\n')
            for filename in build_files:
                build_file.write('chmod +x ' + filename + '\n')
                build_file.write(filename + '\n')

        # write launch files
        with open(os.path.join(self.launch_base_dir, 'launch_core'), 'w') as launch_file:
            launch_file.write('#!/usr/bin/env sh\n')
            for filename in launch_core_files:
                launch_file.write('chmod +x ' + filename + '\n')
                launch_file.write(filename + '\n')

        with open(os.path.join(self.launch_base_dir, 'launch_rest'), 'w') as launch_file:
            launch_file.write('#!/usr/bin/env sh\n')
            for filename in launch_rest_files:
                launch_file.write('chmod +x ' + filename + '\n')
                launch_file.write(filename + '\n')

    def write_source_files(self):
        """Write software files."""
        # remove old source files
        if os.path.exists(self.src_base_dir):
            shutil.rmtree(self.src_base_dir)
        os.makedirs(self.src_base_dir)

        # write software folders
        for node, server in self.server_list():
            src_folder = os.path.join(self.src_base_dir, server.slug)

            shutil.copytree(server.source_folder, src_folder)

    def write_server_configs(self):
        """Write config files for all our servers."""
        # remove old config files
        if os.path.exists(self.configs_base_dir):
            shutil.rmtree(self.configs_base_dir)
        os.makedirs(self.configs_base_dir)

        # write new config files
        server_list = self.server_list()
        info = self.info_from_server_list(server_list)

        for node, server in server_list:
            server_config_folder = os.path.join(self.configs_base_dir, server.slug)
            os.makedirs(server_config_folder)

            server.write_config(server_config_folder, info)

    def info_from_server_list(self, server_list):
        """Return info and server list."""
        info = dict(self.network.info)

        for node, server in server_list:
            server_config_folder = os.path.join(self.configs_base_dir, server.slug)
            server.init_info(config_folder=server_config_folder)

            info['users'].update(server.info['users'])

        return info

    def server_list(self):
        srv_list = []

        for node in self.network.nodes():
            server = self.node_to_server(node)
            server.slug = '{}_{}'.format(server._slug_type, node.software)

            srv_list.append((node, server))

        return srv_list

    def node_to_server(self, node):
        # create server
        if node.client:
            server = servers.available[node.software]()
        elif node.services:
            server = services.available[node.software]()
        elif node.service_bot:
            server = service_bots.available[node.software]()

        # set server info
        server.info = node.info

        # may be configurable later
        server.info['network_name'] = self.network_name

        server.info['links'] = []
        for link in self.network.edges():
            # only write link info for this node
            if link[0] != node and link[1] != node:
                continue

            base_info = nx.get_edge_attributes(self.network, link)
            if not base_info:
                base_info = nx.get_edge_attributes(self.network, (link[1], link[0]))

            try:
                link_info = base_info[link]
            except KeyError:
                link_info = base_info[(link[1], link[0])]

            info = {k: v for (k,v) in link_info}

            if link[0] == node:
                info['remote_name'] = link[1].info['name']
            elif link[1] == node:
                info['remote_name'] = link[0].info['name']

            if not node.client:
                if link[0].client:
                    info['server_software'] = link[0].software
                elif link[1].client:
                    info['server_software'] = link[1].software

            server.info['links'].append(info)

        return server

    def generate(self, ircd_type=None, services_type=None, use_services=True, service_bots=[], opers=[]):
        """Generate the given IRC server map."""
        self.network = map.IrcNetwork()
        self.network.info = {
            'users': {}
        }

        # set network info, opers etc
        for name, password in opers:
            self.network.info['users'][name] = {
                'ircd': {
                    'oper': True,
                    'oper_pass': password,
                },
                'services': {
                    'password': password,
                    'level': 'root',
                },
                'email': 'oper@example.com',
            }

        # ensure ircd and services exist
        ircd_type = servers.available[ircd_type]().name
        services_type = services.available[services_type]().name

        # generate network
        #
        map.MapClientServer(self.network, ircd_type)
        only_client_server = self.network.nodes()[0]

        # add a services server
        new_services = map.MapServicesServer(self.network, services_type)
        new_services.link_to(only_client_server)

        # add service bots
        for bot_type in service_bots:
            new_bot = map.MapServiceBot(self.network, bot_type)
            new_bot.link_to(only_client_server)

        # server configs
        #

        # assign server names and client ports
        current_client_port = 6667
        used_names = []
        used_sids = []

        for server in self.network.nodes():
            info = {
                'users': {},
            }

            # generate name
            if server.services:
                server_name = 'services'
            else:
                server_name = server.software
            while server_name in used_names:
                server_name = names.get_first_name().lower()
            used_names.append(server_name)

            info['name'] = server_name + '.dnt'

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
        current_link_port = 10000
        while current_link_port <= current_client_port:
            current_link_port += 500

        used_passwords = []

        for link in self.network.edges():
            info = []

            # port for things to connect on
            info.append(('port', current_link_port))
            current_link_port += 1

            # generate link password
            password = generate_pass()
            while password in used_passwords:
                password = generate_pass()

            info.append(('password', password))

            nx.set_edge_attributes(self.network, link, info)

        # save network map
        self.save_network_map()

        # draw a pretty diagram of the network
        self.draw_network_diagram()

    def draw_network_diagram(self):
        """Draw a diagram of our network."""
        # calc stats
        stats = map.network_stats(self.network)

        # draw network map to a file
        #
        edge_color = '#bbbbbb'
        node_edge_color = '#cccccc'

        try:
            pos = nx.graphviz_layout(self.network, prog='sfdp', args='-Goverlap=false -Gmaxiter=500 -Gcenter=1')
            mov = True
        except:
            nl = nodelist(self.network)
            pos = nx.shell_layout(self.network, nlist=nl)
            mov = False
            print('Warning: Using Shell layout instead of Graphviz layout. Display may not look nice or legible.')

        # client servers
        # NOTE: we do this because nx.draw seems to apply colours weirdly when the
        #   number of args here matches the number of servers, eg if 3 client servers
        #   and 3 numbers in colour tuple, apply all sorts of dodgy stuff, etc
        if stats['client_servers'] == 3:
            client_color = (0.9, 0.7, 0.7, 1.0)
        else:
            client_color = (0.9, 0.7, 0.7)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if not n.services and not n.service_bot],
            'node_color': client_color,
            'node_size': 120,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # services
        if stats['service_servers'] == 3:
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

        # service bots
        if stats['service_bots'] == 3:
            service_bots_color = (0.7, 0.7, 0.9, 1.0)
        else:
            service_bots_color = (0.7, 0.7, 0.9)

        nodes = nx.draw_networkx_nodes(self.network, pos, **{
            'nodelist': [n for n in self.network.nodes() if n.service_bot],
            'node_color': service_bots_color,
            'node_size': 150,
            'node_shape': 'h',
        })
        if nodes is not None:
            nodes.set_edgecolor(node_edge_color)

        # lines
        nx.draw(self.network, pos, **{
            'nodelist': [],
            'edge_color': edge_color,
        })

        # labels
        nx.draw_networkx_labels(self.network, pos, **{
            'edgelist': [],
            'labels': {s: s.info['name'] for s in self.network.nodes()},
            'font_family': 'monospace',
            'font_size': 6,
            'font_color': [0.2, 0.2, 0.2],
        })

        plt.savefig(self.map_filename)
