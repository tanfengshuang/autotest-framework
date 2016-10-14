#version=RHEL7
# System authorization information
auth --enableshadow --passalgo=sha512

# Use network installation
#url --url="http://download.englab.nay.redhat.com/pub/rhel/rel-eng/RHEL-7.0-20131121.0/compose/Server/x86_64/os/"
KVM_TEST_MEDIUM
# Run the Setup Agent on first boot
firstboot --disabled
firewall --disabled
# Keyboard layouts
keyboard --vckeymap=us --xlayouts='us'
# System language
lang en_US.UTF-8
# Root password
rootpw --iscrypted $1$pDj5hfT7$SKwmFsQdYEnyCJ5qKphwE1
# System timezone
timezone Asia/Shanghai --isUtc
# System bootloader configuration
bootloader --location=mbr
# Partition clearing information
clearpart --all --initlabel
autopart

xconfig --startxonboot
poweroff

#Last reboot
#packages selection
%packages --ignoremissing
@base
@core
@virtualization-client
@virtualization-hypervisor
@virtualization-platform
@virtualization-tools
@virtualization
@desktop-debugging
@dial-up
@fonts
@gnome-desktop
@guest-desktop-agents
@input-methods
@internet-browser
@multimedia
@print-client
@x11
nmap
bridge-utils
rpcbind
qemu-kvm-tools
expect
pexpect
git
make
gcc
%end
