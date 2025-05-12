#!/bin/bash
while true; do
    VM_QUANTITY=$(cat /home/vagrant/quantity.txt)
    echo "$(date '+%Y-%m-%d %H:%M:%S') created by $HOSTNAME" >> /home/vagrant/temp_logs/log.txt

    VM_NUMBER=$(echo "$HOSTNAME" | grep -oE '[0-9]+')

    for i in $(seq 1 $VM_QUANTITY); do
        sftp -i "/home/vagrant/alpine${VM_NUMBER}_ed25519" -o StrictHostKeyChecking=no sftpuser@192.168.56.1${i} <<< "put /home/vagrant/temp_logs/log.txt uploads/logs_${VM_NUMBER}.txt"
    done
    sudo cat /home/sftpuser/uploads/sftp.log | grep "Accepted publickey for sftpuser from 192.168.56." > /home/sftpuser/uploads/${HOSTNAME}.log
    sleep 300
    
done
