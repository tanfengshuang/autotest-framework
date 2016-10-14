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

xconfig --startxonboot
poweroff

%packages
@afrikaans-support
@albanian-support
@amazigh-support
@arabic-support
@armenian-support
@assamese-support
@azerbaijani-support
@backup-client
@base
@basic-desktop
@basque-support
@belarusian-support
@bengali-support
@bhutanese-support
@brazilian-support
@breton-support
@british-support
@bulgarian-support
@burmese-support
@catalan-support
@chhattisgarhi-support
@chichewa-support
@chinese-support
@client-mgmt-tools
@compat-libraries
@console-internet
@coptic-support
@core
@croatian-support
@czech-support
@danish-support
@debugging
@desktop-debugging
@desktop-platform
@dial-up
@directory-client
@dutch-support
@emacs
@esperanto-support
@estonian-support
@ethiopic-support
@faroese-support
@fijian-support
@filipino-support
@finnish-support
@fonts
@french-support
@frisian-support
@friulian-support
@gaelic-support
@galician-support
@general-desktop
@georgian-support
@german-support
@graphical-admin-tools
@graphics
@greek-support
@gujarati-support
@hebrew-support
@hiligaynon-support
@hindi-support
@hungarian-support
@icelandic-support
@indonesian-support
@input-methods
@interlingua-support
@internet-applications
@internet-browser
@inuktitut-support
@irish-support
@italian-support
@japanese-support
@java-platform
@kannada-support
@kashmiri-support
@kashubian-support
@kazakh-support
@kde-desktop
@khmer-support
@kinyarwanda-support
@konkani-support
@korean-support
@kurdish-support
@lao-support
@latin-support
@latvian-support
@legacy-unix
@legacy-x
@lithuanian-support
@low-saxon-support
@luxembourgish-support
@macedonian-support
@mainframe-access
@maithili-support
@malagasy-support
@malayalam-support
@malay-support
@maltese-support
@manx-support
@maori-support
@marathi-support
@mongolian-support
@nepali-support
@network-file-system-client
@network-tools
@northern-sotho-support
@norwegian-support
@occitan-support
@office-suite
@oriya-support
@performance
@perl-runtime
@persian-support
@polish-support
@portuguese-support
@print-client
@punjabi-support
@remote-desktop-clients
@romanian-support
@ruby-runtime
@russian-support
@sanskrit-support
@sardinian-support
@security-tools
@serbian-support
@server-platform
@sindhi-support
@sinhala-support
@slovak-support
@slovenian-support
@smart-card
@somali-support
@southern-ndebele-support
@southern-sotho-support
@spanish-support
@swahili-support
@swati-support
@swedish-support
@system-management-messaging-client
@tagalog-support
@tajik-support
@tamil-support
@technical-writing
@telugu-support
@tetum-support
@tex
@thai-support
@tibetan-support
@tsonga-support
@tswana-support
@turkish-support
@turkmen-support
@ukrainian-support
@upper-sorbian-support
@urdu-support
@uzbek-support
@venda-support
@vietnamese-support
@virtualization
@virtualization-client
@virtualization-platform
@virtualization-tools
@walloon-support
@welsh-support
@x11
@xhosa-support
@zulu-support
abrt-gui
aide
amtu
arptables_jf
arpwatch
audispd-plugins
authd
bacula-client
brltty
cachefilesd
certmonger
cjkuni-fonts-ghostscript
cpupowerutils
ctags-etags
cups-lpd
dcraw
device-mapper-persistent-data
docbook-utils-pdf
dos2unix
dropwatch
dump
dumpet
ebtables
ecryptfs-utils
edac-utils
efax
emacs-auctex
emacs-gnuplot
emacs-nox
evolution-exchange
fence-virtd-libvirt
fence-virtd-multicast
fence-virtd-serial
fetchmail
finger
finger-server
flightrecorder
ftp
gdb-gdbserver
genisoimage
glibc-utils
gnome-pilot
gpm
hesinfo
hmaccalc
hplip
hplip-gui
icedtea-web
ImageMagick
inkscape
ipset
iptraf
iptstate
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
ldapjdk
lftp
libguestfs-java
libguestfs-tools
libreoffice-base
libreoffice-emailmerge
libreoffice-headless
libreoffice-javafilter
libreoffice-ogltrans
libreoffice-presentation-minimizer
libreoffice-report-builder
libreoffice-wiki-publisher
libsss_sudo
libvirt-cim
libvirt-java
libvirt-snmp
libXmu
linuxptp
lksctp-tools
logwatch
lslk
memtest86+
mipv6-daemon
mkbootdisk
mksh
mrtg
mtools
mutt
ncompress
ncurses-term
netlabel_tools
netpbm-progs
NetworkManager-openswan
nmap
nscd
nss_db
nss-pam-ldapd
oddjob
opencryptoki
openldap-clients
openscap
openscap-utils
oprofile-jit
pam_krb5
pam_ldap
papi
pax
perl-Date-Calc
perl-Date-Manip
perl-DBD-SQLite
perl-Frontier-RPC
perl-LDAP
perl-Mozilla-LDAP
perl-suidperl
perl-Sys-Virt
planner
pptp
PyPAM
python-dmidecode
python-saslwrapper
python-volume_key
qemu-guest-agent
qemu-kvm-tools
qt-mysql
rdesktop
rp-pppoe
rsh
rsh-server
rsyslog-gnutls
rsyslog-gssapi
rsyslog-relp
ruby-irb
rusers
rusers-server
rwho
samba-winbind
sdparm
sg3_utils
sgpio
sox
squashfs-tools
star
stunnel
subscription-manager-migration
subscription-manager-migration-data
systemtap-client
systemtap-initscript
talk
talk-server
taskjuggler
tboot
tcp_wrappers
telnet
telnet-server
terminus-fonts
texinfo
tftp
thunderbird
tpm-tools
trousers
tunctl
tuned
tuned-utils
udftools
unix2dos
uuidd
virt-v2v
volume_key
wireshark
wodim
x3270-text
x86info
xchat
xfig
xmltoman
xmlto-tex
xorg-x11-xdm
xterm
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
os.system('chkconfig NetworkManager on')
os.system('sed -i "/^HWADDR/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
