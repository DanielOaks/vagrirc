# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  # Ubuntu is updated regularly enough, should work decently.
  config.vm.box = "ubuntu/trusty64"
  config.vm.box_check_update = false  # you can check this manually

  # Hostname
  config.vm.hostname = "vagrirc"

  # But of course. For if you want to connect custom clients.
  config.vm.network "private_network", ip: "192.168.22.11"
  config.vm.network "forwarded_port", guest: 6667, host: 9997

  # Cache packages so we don't spend a million years downloading
  #   each time we startup
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.enable :apt
    config.cache.enable :gem
    config.cache.scope = :box
  end

  # Folder for IRC stuff.
  if RUBY_PLATFORM.downcase.include?("darwin") or RUBY_PLATFORM.downcase.include?("linux")
    enable_nfs = true

    if Vagrant.has_plugin?("vagrant-cachier")
      config.cache.synced_folder_opts = {
        type: :nfs,
        mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
      }
    end
  else
    enable_nfs = false
  end

  config.vm.synced_folder "./irc", "/irc", :nfs => enable_nfs
  config.vm.synced_folder "./environment", "/environment", :nfs => enable_nfs

  # stop irritating messages on ubuntu
  # see also: http://foo-o-rama.com/vagrant--stdin-is-not-a-tty--fix.html
  config.vm.provision "fix-no-tty", type: "shell" do |s|
    s.privileged = false
    s.inline = "sudo sed -i '/tty/!s/mesg n/tty -s \\&\\& mesg n/' /root/.profile"
  end

  # Base Software Provisioning
  # these files are split up like this so vagrant-cachier can do its work
  config.vm.provision "shell", path: "environment/shell/1.base.packages.sh"
  config.vm.provision "shell", path: "environment/shell/2.additional.sh"
  config.vm.provision "shell", path: "environment/shell/3.rvm.sh"
  config.vm.provision "shell", path: "environment/shell/4.ruby.sh"
  config.vm.provision "shell", path: "environment/shell/5.puppet.sh"

  # Puppet
  config.vm.provision "shell", inline: "gem install librarian-puppet"
  config.vm.provision "shell", inline: "cp /environment/Puppetfile /tmp"
  config.vm.provision "shell", inline: "cd /tmp && librarian-puppet install --verbose"

  config.vm.provision "puppet" do |puppet|
    # if we don't do this, MySQL breaks
    puppet.facter = {
      "fqdn" => "localhost",
    }
    puppet.environment_path = "environment"
    puppet.environment = "puppet"
    puppet.options = ['--modulepath=/tmp/modules']
  end

  # provision IRC software!
  config.vm.provision "shell", inline: "chmod +x /irc/build/build && /irc/build/build", privileged: false
  config.vm.provision "shell", inline: "chmod +x /irc/launch/launch_core && /irc/launch/launch_core", privileged: false, run: "always"

  # create clients and channels with NickServ and such
  config.vm.provision "shell", inline: "chmod +x /irc/init/init && /irc/init/init", privileged: true

  # now that users and such exist, launch rest of the software
  config.vm.provision "shell", inline: "chmod +x /irc/launch/launch_rest && /irc/launch/launch_rest", privileged: false, run: "always"

  # tell them where to go
  config.vm.post_up_message = "Your IRC server should now be accessible from irc://localhost:9997/"

end
