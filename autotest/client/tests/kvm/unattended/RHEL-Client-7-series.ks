#version=RHEL7
# System authorization information

# Use network installation
#url --url="http://download.englab.nay.redhat.com/pub/rhel/rel-eng/RHEL-7.0-20131121.0/compose/Server/x86_64/os/"
KVM_TEST_MEDIUM
# Run the Setup Agent on first boot
text
firstboot --disabled
firewall --disabled

# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8
# Root password
rootpw redhat
# System timezone
timezone Asia/Shanghai --isUtc
# System bootloader configuration
bootloader --location=mbr
# Partition clearing information
clearpart --all --initlabel
autopart

xconfig --startxonboot
poweroff

#%post --interpreter /bin/bash
#chmod +w /etc/rc.d/rc.local
#sed -i 's/exit 0//' /etc/rc.d/rc.local
#echo "cd /root && wget http://hp-z220-11.qe.lab.eng.nay.redhat.com/home/xhe/bin/ready_git7.py" >> /etc/rc.local
#echo "python /root/ready_git7.py" >> /etc/rc.d/rc.local
#chmod -w /etc/rc.d/rc.local
#chmod +x /etc/rc.d/rc.local
##sed -i 's/:5:/:3:/' /etc/inittab
#%end

#Last reboot
#packages selection
%packages --ignoremissing
@base
@core
#@virtualization-client
#@virtualization-hypervisor
#@virtualization-platform
#@virtualization-tools
#@virtualization
#@desktop-debugging
#@dial-up
#@fonts
#@gnome-desktop
#@guest-desktop-agents
#@input-methods
#@internet-browser
#@multimedia
#@print-client
@x11
nmap
bridge-utils
rpcbind
qemu-kvm-tools
expect
pexpect
git
#make
#gcc
yum-utils
%end
