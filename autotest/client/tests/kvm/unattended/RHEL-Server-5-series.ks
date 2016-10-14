install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
keyboard us
key 2515dd4e215225dd
network --bootproto dhcp
rootpw redhat
firewall --disabled
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
@development-libs
@development-tools
kexec-tools
iscsi-initiator-utils
fipscheck
device-mapper-multipath
sgpio
emacs
libsane-hpaio
xorg-x11-utils
xorg-x11-server-Xnest
yum-utils
at-spi-devel

%post --interpreter /bin/bash
#OS configure for ldtp gui test
gconftool-2 --set /desktop/gnome/interface/accessibility --type=boolean true
gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false
gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false
gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0
sed -i '/\[daemon\]/aAutomaticLogin=admin\nAutomaticLoginEnable=True' /etc/gdm/custom.conf
useradd -o -u 0 -g 0 -M -d /root -s /bin/bash admin

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
