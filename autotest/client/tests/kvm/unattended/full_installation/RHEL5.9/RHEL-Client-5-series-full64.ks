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
@afrikaans-support
@arabic-support
@assamese-support
@authoring-and-publishing
@base
@base-x
@basque-support
@bengali-support
@brazilian-support
@breton-support
@british-support
@bulgarian-support
@catalan-support
@chinese-support
@core
@croatian-support
@czech-support
@danish-support
@development-libs
@development-tools
@dialup
@dns-server
@dutch-support
@editors
@engineering-and-scientific
@estonian-support
@faeroese-support
@finnish-support
@french-support
@gaelic-support
@galician-support
@games
@german-support
@gnome-desktop
@gnome-software-development
@graphical-internet
@graphics
@greek-support
@gujarati-support
@hebrew-support
@hindi-support
@hungarian-support
@icelandic-support
@indonesian-support
@irish-support
@italian-support
@japanese-support
@java
@java-development
@kannada-support
@kde-desktop
@korean-support
@legacy-network-server
@legacy-software-development
@legacy-software-support
@lithuanian-support
@mail-server
@malayalam-support
@marathi-support
@mysql
@network-server
@norwegian-support
@office
@oriya-support
@polish-support
@portuguese-support
@printing
@punjabi-support
@romanian-support
@ruby
@russian-support
@serbian-support
@server-cfg
@sinhala-support
@slovak-support
@slovenian-support
@smb-server
@sound-and-video
@spanish-support
@sql-server
@swedish-support
@system-tools
@tamil-support
@telugu-support
@text-internet
@thai-support
@turkish-support
@ukrainian-support
@urdu-support
@web-server
@welsh-support
@x-software-development
@zulu-support
agg
audit
bluez-utils-cups
bogl
bogl-bterm
cvs-inetd
dejagnu
dvgrab
emacs
emacs-nox
epic
eruby
exim
exim-doc
expect
fipscheck
gftp
gnuplot-emacs
hplip3
icon-naming-utils
iscsi-initiator-utils
java-1.6.0-openjdk
java-1.6.0-openjdk-devel
java-1.7.0-openjdk
java-1.7.0-openjdk-devel
jpilot
k3b
kdegames
kdegraphics
kdemultimedia
kdepim
kexec-tools
libdbi-dbd-pgsql
libgconf-java
libgnome-java
libgtk-java
libksba
libsane-hpaio
lynx
memtest86+
mikmod
mod_nss
mysql-connector-odbc64
nedit
openoffice.org-base
openoffice.org-emailmerge
openoffice.org-javafilter
openoffice.org-pyuno
openoffice.org-testtools
perl-Convert-ASN1
perl-Crypt-SSLeay
perl-DateManip
perl-LDAP
perl-libxml-perl
perl-Mozilla-LDAP
perl-TimeDate
perl-XML-Dumper
perl-XML-Grove
perl-XML-NamespaceSupport
perl-XML-SAX
perl-XML-Twig
pexpect
postfix
postgresql-contrib
postgresql-docs
postgresql-jdbc
postgresql-odbc
postgresql-odbc64
postgresql-tcl
pth
python-dmidecode
python-imaging
python-suds
qt-MySQL
qt-ODBC
rsh-server
ruby-ri
rusers-server
scribus
sgpio
system-config-boot
system-switch-mail-gnome
talk-server
taskjuggler
telnet-server
tetex-xdvi
tftp
thunderbird
unixODBC-kde
vim-X11
vnc-server
wacomexpresskeys
xcdroast
xchat
xfig
xorg-x11-server-Xnest
xorg-x11-server-Xvfb
xorg-x11-xbitmaps
yum-utils

%post --interpreter /usr/bin/python
import socket, os
os.system('dhclient')
os.system('chkconfig sshd on')
os.system('iptables -F')
os.system('echo 0 > /selinux/enforce')
os.system('sed -i "/^HWADDR/d" /etc/sysconfig/network-scripts/ifcfg-eth0')
os.system('mv /etc/yum.repos.d/ /etc/yum.repos.d.bk')
os.system('mkdir /etc/yum.repos.d')
os.system('cp -r /etc/yum.repos.d.bk/redhat.repo /etc/yum.repos.d')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("autotest_host_ip", 12323))
client.send("done")
client.close()
