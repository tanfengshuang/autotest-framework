install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
keyboard us
key 660266e267419c67
network --bootproto dhcp
rootpw redhat
firewall --enabled --ssh
selinux --enforcing
timezone --utc Asia/Shanghai
firstboot --disable
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
clearpart --all --initlabel
autopart
xconfig --startxonboot
poweroff

%packages
@admin-tools
@base
@core
@dialup
@editors
@gnome-desktop
@games
@graphical-internet
@graphics
@java
@legacy-software-support
@office
@printing
@sound-and-video
@text-internet
@base-x
kexec-tools
iscsi-initiator-utils
fipscheck
sgpio
emacs
libsane-hpaio
xorg-x11-server-Xnest
yum-utils

%post --interpreter /usr/bin/python
import socket, os
os.system('dhclient')
os.system('chkconfig sshd on')
os.system('iptables -F')
os.system('echo 0 > /selinux/enforce')
os.system('sed -i "/^HWADDR/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
