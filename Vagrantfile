# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  # We use Centos because it's a nice, stable, and works well.
  config.vm.box = "chef/centos-6.6"

  # Hostname
  config.vm.hostname = "vagrirc"

  # But of course. For if you want to connect custom clients.
  config.vm.network "private_network", ip: "192.168.22.11"
  config.vm.network "forwarded_port", guest: 6667, host: 9997

  # Cache packages so we don't spend a million years downloading
  #   each time we startup
  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
    config.cache.synced_folder_opts = {
      type: :nfs,
      mount_options: ['rw', 'vers=3', 'tcp', 'nolock']
    }
  end

  # Folder for IRC stuff.
  if RUBY_PLATFORM.downcase.include?("darwin") or RUBY_PLATFORM.downcase.include?("linux")
    enable_nfs = true
  else
    enable_nfs = false
  end

  config.vm.synced_folder "./irc", "/irc", :nfs => enable_nfs
  config.vm.synced_folder "./environment", "/environment", :nfs => enable_nfs

  # We use Puppet to provision MySQL and such
  config.vm.provision "shell", path: "environment/shell/core.sh"

  config.vm.provision "shell", inline: "gem install librarian-puppet"
  config.vm.provision "shell", inline: "cp /environment/Puppetfile /tmp"
  config.vm.provision "shell", inline: "cd /tmp && librarian-puppet install --verbose"

  config.vm.provision "puppet" do |puppet|
    # if we don't do this, MySQL breaks
    puppet.facter = { 
      "fqdn" => "localhost",
    }
    puppet.options = ['--modulepath=/tmp/modules']
    puppet.manifests_path = "environment/manifests"
    puppet.manifest_file = ""
  end

end
