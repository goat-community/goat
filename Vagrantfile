# -*- mode: ruby -*-
# vi: set ft=ruby :


Vagrant.configure("2") do |config|

  #Box Settings
  config.vm.box = "ubuntu/bionic64"
  config.disksize.size = '25GB'

  #Provider Settings
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 4096
    vb.cpus = 2



  end
  #
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.network "forwarded_port", guest: 81, host: 8081
  config.vm.network "forwarded_port", guest: 3000, host: 3000
  config.vm.network "forwarded_port", guest: 65432, host: 65432
  config.vm.network "forwarded_port", guest: 31951, host: 31951

  # Folder Settings

  config.vm.synced_folder "./app", "/home/vagrant/app"
  config.vm.synced_folder "./scripts", "/home/vagrant/scripts"

  config.vm.provision :shell, inline: "python3 app/installation/install_docker.py"
  config.vm.provision :shell, inline: "docker-compose up -d", run: 'always'
end
