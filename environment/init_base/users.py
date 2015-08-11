#!/usr/bin/env python3
# VagrIRC Initialization Bot

# Written in 2015 by Daniel Oaks <daniel@danieloaks.net>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

import socket
from time import sleep

from ircreactor.envelope import RFC1459Message


class User:
    """User, connects and executes commands."""

    def __init__(self, nick, username, commands):
        self._new_data = ''

        # user info
        self.nick = nick
        self.username = username
        self.realname = '*'
        self.commands = commands

        # connection info
        self.network = '127.0.0.1'
        self.port = 6667

        # allowed commands
        self.command_map = {
            'nickserv': self.cmd_nickserv,
        }

    # send/receive
    def recv(self, number_of_bytes=4096):
        """Receive bytes from the IRC server."""
        try:
            new_data = self.sock.recv(number_of_bytes).decode('utf-8', 'replace')
        except socket.timeout as ex:
            error = ex.args[0]

            if error == 'timed out':
                return []
            else:
                raise ex

        self._new_data += new_data
        raw_messages = []
        message_buffer = ''

        for char in self._new_data:
            if char in ('\r', '\n'):
                if len(message_buffer):
                    print(' ->', message_buffer)
                    raw_messages.append(message_buffer)
                    message_buffer = ''
                continue

            message_buffer += char

        # convert to actual rfc1459 messages
        messages = []

        for msg in raw_messages:
            messages.append(RFC1459Message.from_message(msg))

        return messages

    def send_raw(self, data):
        """Send the given data to the IRC server."""
        print('<- ', data.rstrip())
        self.sock.send(data.encode('utf-8', 'ignore'))

    def send(self, message):
        """Send the given message to the IRC server."""
        if isinstance(message, RFC1459Message):
            message = message.to_message()
        self.send_raw('{}\r\n'.format(message))

    def send_message(self, verb, **kwargs):
        """Send the given message to the IRC server."""
        msg = RFC1459Message.from_data(verb, **kwargs)
        self.send(msg)

    # init
    def run(self):
        """Connect, execute commands, and then disconnect."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.network, self.port))
        self.sock.settimeout(0.3)

        # should really be async but we're lazy
        self.recv()

        self.send_message('NICK', params=[self.nick])
        self.send_message('USER', params=[self.username, 0, '*', self.realname])

        # main event loop
        online = True
        while online:
            messages = self.recv()
            for message in messages:
                if message.verb == '001':
                    self.rpl_welcome()
                    online = False
                elif message.verb.lower() == 'ping':
                    self.send_message('PONG', params=message.params)

        self.recv()
        sleep(1.5)
        self.recv()
        self.quit()

    def rpl_welcome(self):
        # yay lazy event loop!
        for name, info in self.commands:
            cmd = self.command_map.get(name, None)
            if cmd:
                cmd(info)
                self.recv()

    def quit(self):
        self.send_message('QUIT')

    # irc commands
    def privmsg(self, target, msg):
        """Send a PRIVMSG."""
        self.send_message('PRIVMSG', params=[target, msg])

    # command list
    def cmd_nickserv(self, info):
        self.privmsg('NickServ', info)
