install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
keyboard us
key --skip
network --bootproto dhcp
rootpw redhat
firewall --disabled
selinux --enforcing
timezone --utc Asia/Shanghai
firstboot --disable
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
#clearpart --all --initlabel
#autopart
# The following is the partition information you requested
# Note that any partitions you deleted are not expressed
# here so unless you clear all partitions first, this is
# not guaranteed to work
clearpart --all --initlabel
#volgroup VolGroup --pesize=131072 pv.008002
#logvol / --fstype=ext4 --name=LogVol_root --vgname=VolGroup --grow --size=1
#logvol swap --name=LogVol_swap --vgname=VolGroup --size=8192

part /boot --fstype=ext4 --size=500
part swap --size=2000
part / --fstype=ext4 --grow --size=5000
#part pv.008002 --grow --size=1


xconfig --startxonboot
poweroff

%packages
@base
@client-mgmt-tools
@core
@debugging
@basic-desktop
@desktop-debugging
@desktop-platform
@directory-client
@fonts
@general-desktop
@graphical-admin-tools
@input-methods
@internet-browser
@java-platform
@legacy-x
@network-file-system-client
@perl-runtime
@print-client
@remote-desktop-clients
@server-platform
@server-policy
@x11
mtools
pax
python-dmidecode
oddjob
sgpio
genisoimage
wodim
abrt-gui
certmonger
pam_krb5
krb5-workstation
libXmu
perl-DBD-SQLite
python-twisted
at-spi-python
tigervnc-server
sendmail

%post --interpreter /bin/bash
#OS configure for ldtp gui test
gconftool-2 --set /desktop/gnome/interface/accessibility --type=boolean true
gconftool-2 -s /apps/gnome-session/options/show_root_warning --type=boolean false
gconftool-2 -s /apps/gnome-screensaver/idle_activation_enabled --type=boolean false
gconftool-2 -s /apps/gnome-power-manager/ac_sleep_display --type=int 0

#stop the update of PackageKit
gconftool-2 --set /apps/gnome-packagekit/update-icon/frequency_get_updates --type=int 0

#automatic login
sed -i '/\[daemon\]/aAutomaticLogin=root\nAutomaticLoginEnable=True' /etc/gdm/custom.conf

%post --interpreter /usr/bin/python
import socket, os
os.system('dhclient')
os.system('chkconfig sshd on')
os.system('iptables -F')
os.system('echo 0 > /selinux/enforce')
os.system('chkconfig NetworkManager on')
os.system('sed -i "/^HWADDR/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
