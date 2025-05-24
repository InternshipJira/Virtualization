VM_COUNT = ENV['MACHINE_QUANTITY'].to_i
Vagrant.configure("2") do |config|
  (1..VM_COUNT).each do |i|
    config.vm.define "alpine#{i}" do |alpine|
      alpine.vm.hostname = "alpine#{i}"
      TOKEN = ENV['TOKEN']
      alpine.vm.box = "generic/alpine318"
      alpine.vm.network "private_network", type: "static", ip: "192.168.56.1#{i}"
      alpine.vm.provision "shell", path: "provision.sh", args: ["#{TOKEN}", "#{i}"]
      alpine.vm.provision "file", source: "key_exchange.sh", destination: "/home/vagrant/key_exchange.sh"
    end
  end
end