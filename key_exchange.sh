#!/bin/bash
IFACE="eth1"
VM_NUMBER="$1"
PUB_LIST=$(ls /home/vagrant/Pub_keys/*.pub)
cd /home/vagrant/Pub_keys
#listen for incoming ICMP echo requests
if tcpdump -i "$IFACE" -c 1 icmp and icmp[icmptype] = 8 -nn >> /dev/null; then
    git pull
    for i in $PUB_LIST ; do
        if [[ "$i" != *"alpine$VM_NUMBER"* ]]; then
            cat "$i" >> /home/sftpuser/.ssh/authorized_keys
        fi
    done
fi