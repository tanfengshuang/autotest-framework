install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
langsupport --default=en_US.UTF-8 en_US.UTF-9
keyboard us
network --bootproto dhcp
rootpw redhat
firewall --disabled
selinux --enforcing
timezone --utc America/New_York
firstboot --disable
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
clearpart --all --initlabel
autopart
poweroff

%packages
@ base
@development-libs
@development-tools
gcc4
gcc4-gfortran
patch
make
nc
ntp
redhat-lsb

%post
cd home
dhclient
chkconfig sshd on
iptables -F
echo 0 > selinux/enforce
sed -i '/^HWADDR/d' /etc/sysconfig/network-scripts/ifcfg-eth0
echo "s0:2345:respawn:/sbin/agetty -L -f /etc/issue 115200 ttyS0 vt100" >> /etc/inittab
echo "ttyS0" >> /etc/securetty
wget http://fileshare.englab.nay.redhat.com/pub/section2/kvm/pub/download/Python-2.6.6.tar.bz2
tar xjf Python-2.6.6.tar.bz2
cd Python-2.6.6
./configure --prefix=/usr/local --exec-prefix=/usr/local
make
make install
ln -sf /usr/local/bin/python /usr/bin/python
sleep 10
cat > post_script.py <<ABC
import socket, os
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
ABC
python post_script.py
%end
