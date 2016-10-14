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
@compat-libraries
@console-internet
@core
@debugging
@dial-up
@directory-client
@fonts
@hardware-monitoring
@infiniband
@java-platform
@legacy-unix
@mysql-client
@network-file-system-client
@performance
@perl-runtime
@postgresql-client
@ruby-runtime
@scientific
@server-platform
@storage-client-iscsi
@system-admin-tools
@system-management
@system-management-messaging-client
@system-management-snmp
@virtualization
@virtualization-client
@virtualization-platform
@virtualization-tools
atlas
audispd-plugins
authd
brltty
cachefilesd
certmonger
compat-dapl
compat-openmpi
compat-openmpi-psm
conman
cpupowerutils
crypto-utils
cups-lpd
device-mapper-persistent-data
dos2unix
dtach
dump
dumpet
ecryptfs-utils
edac-utils
efax
expect
fence-agents
fence-virtd-libvirt
fence-virtd-multicast
fence-virtd-serial
fetchmail
fftw
fftw-devel
fftw-static
finger
finger-server
flightrecorder
freeipmi
freeipmi-bmc-watchdog
freeipmi-ipmidetectd
ftp
gdb-gdbserver
genisoimage
glibc-utils
gpm
gsl
gsl-devel
gsl-static
hardlink
hesinfo
i2c-tools
icedtea-web
infiniband-diags
ipmitool
irssi
isdn4k-utils
jwhois
kabi-yum-plugins
kernel-doc
krb5-appl-clients
krb5-appl-servers
krb5-pkinit-openssl
krb5-workstation
ksh
lapack
ldapjdk
lftp
libdbi-dbd-mysql
libdbi-dbd-pgsql
libguestfs-java
libguestfs-tools
libibcommon
libsss_sudo
libvirt-cim
libvirt-java
libvirt-snmp
linuxptp
lm_sensors
logwatch
lslk
lsscsi
mc
memtest86+
mgetty
mkbootdisk
mksh
mpich2
mpitests-mvapich
mpitests-mvapich2
mpitests-openmpi
mstflint
mtools
mutt
mvapich
mvapich2
mvapich2-psm-devel
mvapich-psm-devel
mvapich-psm-static
mysql-connector-java
ncompress
ncurses-term
net-snmp-perl
net-snmp-python
nscd
nss_db
nss-pam-ldapd
numpy
oddjob
openhpi
openhpi-subagent
OpenIPMI
openldap-clients
openmpi
openmpi-devel
opensm
oprofile-jit
pam_krb5
pam_ldap
papi
pax
perftest
perl-Date-Calc
perl-Date-Manip
perl-DBD-MySQL
perl-DBD-Pg
perl-DBD-SQLite
perl-Frontier-RPC
perl-LDAP
perl-Mozilla-LDAP
perl-suidperl
perl-Sys-Virt
pexpect
postgresql-jdbc
pptp
PyPAM
python-dmidecode
python-saslwrapper
python-volume_key
qemu-guest-agent
qemu-kvm-tools
qperf
qpid-tests
rdist
rp-pppoe
rrdtool
rsh
rsh-server
rsyslog-gnutls
rsyslog-gssapi
rsyslog-relp
ruby-irb
ruby-qpid-qmf
rusers
rusers-server
rwho
samba-winbind
scipy
screen
scrub
sdparm
sg3_utils
sgpio
sox
squashfs-tools
srptools
star
subscription-manager-migration
subscription-manager-migration-data
symlinks
systemtap-client
systemtap-initscript
talk
talk-server
tboot
tcl-pgtcl
tcp_wrappers
telnet
telnet-server
tftp
tree
tunctl
tuned
tuned-utils
udftools
unix2dos
uuidd
virt-v2v
vlock
volume_key
watchdog
wodim
x86info
xdelta
yum-plugin-aliases
yum-plugin-changelog
yum-plugin-downloadonly
yum-plugin-tmprepo
yum-plugin-verify
yum-plugin-versionlock
yum-presto
zsh

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

