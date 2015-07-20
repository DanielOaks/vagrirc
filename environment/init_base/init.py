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

import os
import json

from users import User

init_dir = os.path.dirname(os.path.abspath(__file__))

# join users one-by-one and execute commands
users_filename = os.path.join(init_dir, 'users.json')
with open(users_filename) as users_file:
    users = json.loads(users_file.read())

for info in users:
    user = User(**info)
    user.run()
