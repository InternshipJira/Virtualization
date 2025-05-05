#!/bin/bash
sudo apk update
sudo apk upgrade
sudo apk add bash perl wget tar git cronie openssh-server coreutils
wget https://sourceforge.net/projects/rkhunter/files/latest/download -O rkhunter.tar.gz
tar -xvzf rkhunter.tar.gz
cd rkhunter-*
sudo ./installer.sh --install
cd ..

USER="sftpuser"
export TOKEN="$1"

mkdir -p /home/$USER/.ssh
mkdir  /home/$USER/uploads

sudo addgroup sftpgroup
sudo adduser -G sftpgroup -h /home/$USER -s /sbin/nologin "$USER"
echo "sftpuser:$3" | sudo chpasswd


sudo chown root:root /home/$USER
sudo chmod 755 /home/$USER

sudo chown $USER:sftpgroup /home/$USER/uploads
sudo chmod 755 /home/$USER/uploads

sudo chown -R $USER:sftpgroup /home/$USER/.ssh
sudo chmod 700 /home/$USER/.ssh

sudo touch /home/$USER/.ssh/authorized_keys
sudo chown $USER:sftpgroup /home/$USER/.ssh/authorized_keys
sudo chmod 600 /home/$USER/.ssh/authorized_keys

SFTP_CONFIG="
Match Group sftpgroup
    ChrootDirectory /home/sftpuser
    PubkeyAuthentication yes
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication no
    
"
sudo echo "$SFTP_CONFIG" >> /etc/ssh/sshd_config
sudo sed -i 's|^#\?Subsystem\s\+sftp.*|Subsystem sftp internal-sftp|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?PubkeyAuthentication.*|PubkeyAuthentication yes|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?AuthorizedKeysFile.*|AuthorizedKeysFile .ssh/authorized_keys|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?PasswordAuthentication.*|PasswordAuthentication no|' /etc/ssh/sshd_config



PRIVATE_KEY=""$HOSTNAME"_ed25519"
PUBLIC_KEY=""$PRIVATE_KEY".pub"

sudo -u vagrant ssh-keygen -t ed25519 -f $PRIVATE_KEY -N ""

rc-service sshd restart
git clone https://kasshntr:$TOKEN@github.com/kaashntr/Pub_keys.git
cd Pub_keys
git config --global user.name "$HOSTNAME"
git config --global user.email "$USER@$HOSTNAME"
cp -f /home/vagrant/$PUBLIC_KEY .
git add $PUBLIC_KEY
git commit -m "123"
git push

echo "0 3 * * * /usr/bin/rkhunter --cronjob --report-warnings-only" > mycron.txt
crontab mycron.txt

rkhunter --propupd

#rkhunter --check

