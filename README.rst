VagrIRC
=======
IRC Testnet provisioning made easy, with Vagrant!

Basically, this is designed to make my IRC development network provisioning more simple and easy.

**DO NOT USE THIS FOR A PRODUCTION NETWORK. IT IS TERRIBLE FOR THAT AND HAS HOLES AND IS IN NO WAY TESTED FOR SECURITY**


Installation
------------
You need to make sure `Python3 <https://www.python.org/downloads/>`_ and `Vagrant <https://www.vagrantup.com/>`_ are installed on your machine to use this tool. Unixy OSes are recommended as no testing has been performed with Windows (though hopefully it should work).

1. ``git clone https://github.com/DanielOaks/vagrirc.git``
2. ``cd vagrirc``
3. ``vagrant plugin install vagrant-cachier``
4. ``pip3 install -r requirements.txt``
5. ``./vagrirc.py generate --oper coolguy:coolpassword --ircd hybrid --services anope2``
6. ``./vagrirc.py write``
7. ``vagrant up``

Step three is optional, but recommended as it means all sorts of packages will get cached between installs, which saves lots of time when provisioning a new machine.

Vagrant will run through the setup of your machine, including compiling the ircd / services / etc, registering your given nick/password via nickserv, and setting you up as an ircd and services oper.

Everything is laid out in the ``irc/`` folder. Underneath there, the ``bin`` folder is where your running services and programs run - and where you can change the configuration files for each program. Keep in mind that simply running ``./vagrirc write`` should not overwrite the contents of that ``bin`` folder, as it is populated during provisioning.

**NOTE:** ``/irc/build/*`` scripts **WILL OVERWRITE YOUR PROJECT'S ``/irc/bin/etc`` FOLDER**. For service bots like ``acid``, running the automatic build script will overwrite any changes you've made and your git repo in there.


FAQ
---

* I've changed a configuration file and want to apply it to my running VM.

    In this case, the safest thing to do is to restart your machine, ie:

    1. ``vagrant halt``
    2. ``vagrant up``

    However, you can also ssh into the machine using ``vagrant ssh``, kill the running IRCd (and whatever other services and service bots are left running), and then use the scripts in the ``launch/`` directory to manually launch the network (``launch_core`` launches just the IRCd and services, ``launch_rest`` launches any selected service bots).

    I tend to simply cd into the ``bin`` folder of the component I'm testing / developing and launching it in a 'foreground' mode. Some software let you specify ``-f``, some ``-foreground``, that let you launch the component and stay attached to the shell so you can easily ctrl+c and close it. However, this may mess up databases and cause issues, so it's not recommended.

    **Note:** Some software also includes a foreground launch script under ``/irc/launch/software_name/launch_foreground``. This launches the software into the foreground, as described above, and keeps it attached to the shell.


* I can't get something to work, or something's broken!

    Feel free to make an issue or send a PR on the `Github repo <https://github.com/DanielOaks/vagrirc>`_.

    Alternatively, you can contact me by email at daniel@danieloaks.net or message me on Freenode under ``dan-`` .


License
-------
CC0 1.0 Universal on all my code.

Part of the ``environment/shell/*.sh`` core files are from the `PuPHPet <https://github.com/puphpet/puphpet>`_ project, which is used under the `MIT License <http://opensource.org/licenses/mit-license.php>`_.
