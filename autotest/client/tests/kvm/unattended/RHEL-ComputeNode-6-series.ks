install
KVM_TEST_MEDIUM
text
reboot
lang en_US.UTF-8
keyboard us
key --skip
network --bootproto dhcp
rootpw redhat
firewall --enabled --ssh
selinux --enforcing
timezone --utc Asia/Shanghai
firstboot --disable
bootloader --location=mbr --append="console=tty0 console=ttyS0,115200"
zerombr
clearpart --all --initlabel
part /boot --fstype=ext4 --size=500
part swap --size=2000
part / --fstype=ext4 --grow --size=5000
#autopart
poweroff

%packages
@base
@client-mgmt-tools
@core
@debugging
@infiniband
@java-platform
@network-file-system-client
@performance
@perl-runtime
@scientific
@server-platform
pax
python-dmidecode
sgpio
perl-DBD-SQLite
numpy
atlas

%post --interpreter /bin/bash
#stop the update of PackageKit
gconftool-2 --set /apps/gnome-packagekit/update-icon/frequency_get_updates --type=int 0

%post --interpreter /usr/bin/python
import socket, os
os.system('dhclient')
os.system('chkconfig sshd on')
os.system('iptables -F')
os.system('echo 0 > /selinux/enforce')
#os.system('chkconfig NetworkManager on')
os.system('sed -i "/^HWADDR/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
os.system("""echo 'ifname=`ip link|grep ": eth"|grep "DOWN"|cut -d: -f 2|sed "s/ //"`
if [[ -n $ifname ]]; then
    iffile="/etc/sysconfig/network-scripts/ifcfg-"$ifname
    mv /etc/sysconfig/network-scripts/ifcfg-eth* $iffile
    sed -i "s/^DEVICE=.*/DEVICE=\"$ifname\"/" $iffile
    service network restart
fi' >> /etc/rc.local""")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
