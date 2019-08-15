# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|

  #Box Settings
  config.vm.box = "ubuntu/bionic64"

  #Provider Settings
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4096
    vb.cpus = 2

  end
  #
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 81, host: 8081
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 5432, host: 65432
  config.vm.network "forwarded_port", guest: 3200, host: 3200
  config.vm.network "forwarded_port", guest: 4000, host: 4000
  # Folder Settings
  config.vm.synced_folder "./app", "/home/vagrant/app"
  config.vm.synced_folder ".", "/home/vagrant/all"
  config.vm.provision :shell, inline: "sudo apt update"
  config.vm.provision :shell, path: "./app/installation/reboot.sh", run: 'always'
end
