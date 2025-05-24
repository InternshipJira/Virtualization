#!/bin/bash
sudo apk update
sudo apk upgrade
sudo apk add git bash perl wget tar cronie openssh-server coreutils tcpdump syslog-ng
wget https://sourceforge.net/projects/rkhunter/files/latest/download -O rkhunter.tar.gz
tar -xvzf rkhunter.tar.gz
cd rkhunter-*
sudo ./installer.sh --install
cd ..

USER="sftpuser"
export TOKEN="$1"
rc-update add cronie
service cronie start

touch /home/vagrant/quantity.txt
echo "$4" > /home/vagrant/quantity.txt


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

SFTP_CONFIG2="
# SFTP-specific logging
filter f_sftp_auth { facility(auth); };
destination d_sftp { file("/home/sftpuser/uploads/sftp.log"); };
log { source(s_sys); filter(f_sftp_auth); destination(d_sftp); };

"

SFTP_CONFIG="
SyslogFacility AUTH
Match Group sftpgroup
    ChrootDirectory /home/sftpuser
    PubkeyAuthentication yes
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication no
    
"

touch /home/$USER/uploads/sftp.log


sudo service sshd restart

sudo echo "$SFTP_CONFIG" >> /etc/ssh/sshd_config
sudo echo "$SFTP_CONFIG2" >> /etc/syslog-ng/syslog-ng.conf
sudo sed -i 's|^#\?Subsystem\s\+sftp.*|Subsystem sftp internal-sftp -f LOCAL6 -l INFO|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?PubkeyAuthentication.*|PubkeyAuthentication yes|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?AuthorizedKeysFile.*|AuthorizedKeysFile .ssh/authorized_keys|' /etc/ssh/sshd_config
sudo sed -i 's|^#\?PasswordAuthentication.*|PasswordAuthentication no|' /etc/ssh/sshd_config

sudo service syslog-ng restart


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

rkhunter --propupd
rkhunter --update

nohup bash /home/vagrant/key_exchange.sh "$2" > /dev/null 2>&1 &
if [ $2 -eq $4 ];then
    for i in $(seq 1 $4); do
        echo "Pinging 192.168.56.1$i"
        ping -c 1 "192.168.56.1$i" > /dev/null
    done
    PUB_LIST=$(ls /home/vagrant/Pub_keys/*.pub)
    git pull
    for i in $PUB_LIST ; do
        if [[ "$i" != *"alpine$2"* ]]; then
            echo $i
            cat "$i" >> /home/vagrant/.ssh/authorized_keys
            cat "$i" >> /home/sftpuser/.ssh/authorized_keys
        fi
    done
fi

cd ..
chmod +x /home/vagrant/generating_logs.sh
mkdir temp_logs
nohup ./generating_logs.sh > /dev/null 2>&1 &
echo "nohup ./generating_logs.sh > /dev/null 2>&1 &" /etc/local.d/myscript.start
sudo chown $USER:sftpgroup /home/sftpuser/uploads/sftp.log
echo "0 3 * * * /usr/bin/rkhunter -c --enable all --disable none --rwo --sk --nocolors || true" >> /home/vagrant/mycron.txt
crontab /home/vagrant/mycron.txt