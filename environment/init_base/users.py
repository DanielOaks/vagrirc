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

from envelope import RFC1459Message


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
        self._new_data += self.sock.recv(number_of_bytes).decode('utf-8', 'replace')
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

    # init
    def run(self):
        """Connect, execute commands, and then disconnect."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.network, self.port))

        # should really be async but we're lazy
        self.recv()

        self.send('NICK {}'.format(self.nick))
        self.send('USER {} 0 * :{}'.format(self.username, self.realname))

        # main event loop
        online = True
        while online:
            messages = self.recv()
            for message in messages:
                if message.verb.lower() == '001':
                    self.rpl_welcome()
                    online = False

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
        self.send('QUIT')

    # irc commands
    def privmsg(self, target, msg):
        """Send a PRIVMSG."""
        self.send('PRIVMSG {} :{}'.format(target, msg))

    # command list
    def cmd_nickserv(self, info):
        self.privmsg('NickServ', info)
