import sys, os, subprocess, commands
import logging

class ent_env:

# ========================================================
# 	1. Sub-Man Testing Parameters
# ========================================================

	# [A] Global parameters
	proxy = "squid.corp.redhat.com:3128"
	username_qa = "qa@redhat.com"
        password_qa = "HWj8TE28Qi0eP2c"

	# [B] Acceptance/Smoke Test parameters
	# # RHEL-Everything-7
	username70 = "stage_rhel7_test"
	password70 = "redhat"
	autosubprod70 = "Red Hat Enterprise Linux 7 Public Beta"
	installedproductname70 = "Red Hat Enterprise Linux 7 Public Beta"
	productid70 = "RH00069"
	pid70 = "226"
	pkgtoinstall70 = "yum-utils"
	productrepo70 = "rhel-7-public-beta-rpms"
	betarepo70 = "rhel-7-public-beta-rpms"
	servicelevel70 = "Self-Support"
	releaselist70 = "7.0"

	# # RHEL-Everything-ppc64-7
	username71 = "stage_rhel7_test"
	password71 = "redhat"
	autosubprod71 = "Red Hat Enterprise Linux Beta for IBM POWER"
	installedproductname71 = "Red Hat Enterprise Linux Beta for IBM POWER"
	productid71 = "RH00070"
	pid71 = "227"
	pkgtoinstall71 = "yum-utils"
	productrepo71 = "rhel-7-for-power-public-beta-rpms"
	betarepo71 = "rhel-7-for-power-public-beta-rpms"
	servicelevel71 = "Self-Support"
	releaselist71 = "7.0"

	# # RHEL-Everything-s390x-7
	username72 = "stage_rhel7_test"
	password72 = "redhat"
	autosubprod72 = "Red Hat Enterprise Linux Beta for IBM System z"
	installedproductname72 = "Red Hat Enterprise Linux Beta for IBM System z"
	productid72 = "RH00071"
	pid72 = "228"
	pkgtoinstall72 = "yum-utils"
	productrepo72 = "rhel-7-for-system-z-public-beta-rpms"
	betarepo72 = "rhel-7-for-system-z-public-beta-rpms"
	servicelevel72 = "Self-Support"
	releaselist72 = "7.0"


	# #RHEL-Client-7
	username77 = "stage_rhel_test_new"
	password77 = "redhat"
	autosubprod77 = "Red Hat Enterprise Linux Desktop Beta"
	installedproductname77 = "Red Hat Enterprise Linux Desktop Beta"
	productid77 = "MCT0967"
	pid77 = "68"
	pkgtoinstall77 = "yum-utils"
	productrepo77 = "rhel-7-public-beta-rpms"
	betarepo77 = "rhel-7-public-beta-rpms"
	servicelevel77 = "Self-Support"
	releaselist77 = "7.0"

	# #RHEL-Server-7
	username78 = "stage_test_22_new"
	password78 = "redhat"
	autosubprod78 = "Red Hat Enterprise Linux Server Beta"
	installedproductname78 = "Red Hat Enterprise Linux Server Beta"
	productid78 = "RH0586408"
	pid78 = "69"
	pkgtoinstall78 = "yum-utils"
	productrepo78 = "rhel-7-public-beta-rpms"
	betarepo78 = "rhel-7-public-beta-rpms"
	servicelevel78 = "Self-Support"
	releaselist78 = "7.0"
	prefix1="/subscription"

	# #RHEL-Workstation-7
	username73 = "stage_rhel_test_new"
	password73 = "redhat"
	autosubprod73 = "Red Hat Enterprise Linux Workstation Beta"
	installedproductname73 = "Red Hat Enterprise Linux Workstation Beta"
	productid73 = "RH0923296"
	pid73 = "71"
	pkgtoinstall73 = "yum-utils"
	productrepo73 = "rhel-7-public-beta-rpms"
	betarepo73 = "rhel-7-public-beta-rpms"
	servicelevel73 = "Self-Support"
	releaselist73 = "7.0"

	# #RHEL-ComputeNode-7
	username74 = "stage_test_23_new"
	password74 = "redhat"
	autosubprod74 = "Red Hat Enterprise Linux Server Beta for HPC Compute Node"
	installedproductname74 = "Red Hat Enterprise Linux Server Beta for HPC Compute Node"
	productid74 = "RH0604852"
	pid74 = "76"
	pkgtoinstall74 = "yum-utils"
	productrepo74 = "rhel-7-public-beta-rpms"
	betarepo74 = "rhel-7-public-beta-rpms"
	servicelevel74 = "Self-Support"
	releaselist74 = "7.0"

	# #RHEL-Server-s390x-7
	username76 = "stage_test_21_new"
	password76 = "redhat"
	autosubprod76 = "Red Hat Enterprise Linux Beta for IBM System z"
	installedproductname76 = "Red Hat Enterprise Linux Beta for IBM System z"
	productid76 = "RH0416249"
	pid76 = "72"
	pkgtoinstall76 = "yum-utils"
	productrepo76 = "rhel-7-public-beta-rpms"
	betarepo76 = "rhel-7-public-beta-rpms"
	servicelevel76 = "Self-Support"
	releaselist76 = "7.0"

	# #RHEL-Server-ppc64-7
	username75 = "stage_test_14_new"
	password75 = "redhat"
	autosubprod75 = "Red Hat Enterprise Linux Beta for IBM POWER"
	installedproductname75 = "Red Hat Enterprise Linux Beta for IBM POWER"
	productid75 = "RH0326831"
	pid75 = "74"
	pkgtoinstall75 = "yum-utils"
	productrepo75 = "rhel-7-public-beta-rpms"
	betarepo75 = "rhel-7-public-beta-rpms"
	servicelevel75 = "Self-Support"
	releaselist75 = "7.0"

	# #RHEL-Server-ppc64le-7
	username80 = "stage_power_2_new"
	password80 = "redhat"
	autosubprod80 = "Red Hat Enterprise Linux for IBM Power"
	installedproductname80 = "Red Hat Enterprise Linux for IBM Power"
	productid80 = "RH00284"
	pid80 = "279"
	pkgtoinstall80 = "yum-utils"
	productrepo80 = "rhel-7-public-beta-rpms"
	betarepo80 = "rhel-7-public-beta-rpms"
	servicelevel80 = "Self-Support"
	releaselist80 = "7.0"

	# #RHEL-Server-aarch64-7
	username79 = "stage_test_rhel_arm_new"
	password79 = "redhat"
	autosubprod79 = "Red Hat Enterprise Linux Server for ARM Development Preview (No Support) (20 Instances)"
	installedproductname79 = "Red Hat Enterprise Linux Server for ARM Development Preview"
	productid79 = "MCT3115"
	pid79 = "294" #eng prod id for Development Preview: 261, for ARM Beta: 295, for ARM GA: 294, for rhel7.2Beta: 294
	pkgtoinstall79 = "yum-utils"
	productrepo79 = "rhel-server-for-arm-development-preview-rpms"
	betarepo79 = "rhel-server-for-arm-development-preview-rpms"
	servicelevel79 = "Standard"
	releaselist79 = "1.2"


	# #RHEL-Client-6
	username1 = "stage_test_26_new"
	password1 = "redhat"
	autosubprod1 = "Red Hat Enterprise Linux Desktop"
	installedproductname1 = "Red Hat Enterprise Linux Desktop"
	productid1 = "RH0823221"
	pid1 = "68"
	pkgtoinstall1 = "zsh"
	productrepo1 = "rhel-6-desktop-rpms"
	betarepo1 = "rhel-6-desktop-beta-rpms"
	servicelevel1 = "STANDARD"
	releaselist1 = "6.1,6.2,6.3,6.4,6Client"

	# #RHEL-Server-6
	username2 = "stage_test_12_new"
	password2 = "redhat"
	autosubprod2 = "Red Hat Enterprise Linux Server"
	installedproductname2 = "Red Hat Enterprise Linux Server"
	productid2 = "RH0103708"
	pid2 = "69"
	pkgtoinstall2 = "zsh"
	productrepo2 = "rhel-6-server-rpms"
	betarepo2 = "rhel-6-server-beta-rpms"
	servicelevel2 = "PREMIUM"
	releaselist2 = "6.1,6.2,6.3,6.4,6Server"

	# #RHEL-Workstation-6
	username6 = "stage_rhscl_dts_test_new" #"stage_test_27"
	password6 = "redhat"
	autosubprod6 = "Red Hat Enterprise Linux Workstation"
	installedproductname6 = "Red Hat Enterprise Linux Workstation"
	productid6 = "RH0958488"
	pid6 = "71"
	pkgtoinstall6 = "zsh"
	productrepo6 = "rhel-6-workstation-rpms"
	betarepo6 = "rhel-6-workstation-beta-rpms"
	servicelevel6 = "STANDARD"
	releaselist6 = "6.1,6.2,6.3,6.4,6Workstation"

	# #RHEL-ComputeNode-6
	username7 = "stage_test_23_new"
	password7 = "redhat"
	autosubprod7 = "Red Hat Enterprise Linux for Scientific Computing"
	installedproductname7 = "Red Hat Enterprise Linux for Scientific Computing"
	productid7 = "RH0604852"
	pid7 = "76"
	pkgtoinstall7 = "zsh"
	productrepo7 = "rhel-6-hpc-node-rpms"
	betarepo7 = "rhel-6-hpc-node-beta-rpms"
	servicelevel7 = "SELF-SUPPORT"
	releaselist7 = "6.1,6.2,6.3,6.4,6ComputeNode"

	# #RHEL-Server-s390x-6
	username8 = "stage_test_21_new"
	password8 = "redhat"
	autosubprod8 = "Red Hat Enterprise Linux for IBM System z"
	installedproductname8 = "Red Hat Enterprise Linux for IBM System z"
	productid8 = "RH0416249"
	pid8 = "72"
	pkgtoinstall8 = "zsh"
	productrepo8 = "rhel-6-for-system-z-rpms"
	betarepo8 = "rhel-6-for-system-z-beta-rpms"
	servicelevel8 = "STANDARD"
	releaselist8 = "6.1,6.2,6.3,6.4,6Server"

	# #RHEL-Server-ppc64-6
	username9 = "stage_power_1_new" #"stage_test_14"
	password9 = "redhat"
	autosubprod9 = "Red Hat Enterprise Linux for IBM POWER"
	installedproductname9 = "Red Hat Enterprise Linux for IBM POWER"
	productid9 = "RH00283" #"RH0326831"
	pid9 = "74"
	pkgtoinstall9 = "zsh"
	productrepo9 = "rhel-6-for-power-rpms"
	betarepo9 = "rhel-6-for-power-beta-rpms"
	servicelevel9 = "STANDARD"
	releaselist9 = "6.1,6.2,6.3,6.4,6Server"


	# #RHEL-Client-5
	username3 = "stage_test_26"
	password3 = "redhat"
	autosubprod3 = "Red Hat Enterprise Linux Desktop"
	installedproductname3 = "Red Hat Enterprise Linux Desktop"
	productid3 = "RH0823221"
	pid3 = "68"
	pkgtoinstall3 = "zsh"
	productrepo3 = "rhel-5-desktop-rpms"
	betarepo3 = "rhel-5-desktop-beta-rpms"
	servicelevel3 = "STANDARD"
	releaselist3 = "5.7,5.8,5.9,5Client"

	# #RHEL-Server-5
	username4 = "stage_test_12"
	password4 = "redhat"
	autosubprod4 = "Red Hat Enterprise Linux Server"
	installedproductname4 = "Red Hat Enterprise Linux Server"
	productid4 = "RH0103708"
	pid4 = "69"
	pkgtoinstall4 = "zsh"
	productrepo4 = "rhel-5-server-rpms"
	betarepo4 = "rhel-5-server-beta-rpms"
	servicelevel4 = "PREMIUM"
	releaselist4 = "5.7,5.8,5.9,5Server"

	# #RHEL-Workstation-5
	username5 = "stage_rhel_test" #"stage_test_27"
	password5 = "redhat"
	autosubprod5 = "Red Hat Enterprise Linux Workstation"
	installedproductname5 = "Red Hat Enterprise Linux Workstation"
	productid5 = "RH0923296" #"RH0958488"
	pid5 = "71"
	pkgtoinstall5 = "zsh"
	productrepo5 = "rhel-5-workstation-rpms"
	betarepo5 = "rhel-5-workstation-beta-rpms"
	servicelevel5 = "STANDARD"
	releaselist5 = "5.7,5.8,5.9,5Client"

	# #RHEL-Server-s390x-5
	username10 = "stage_test_21"
	password10 = "redhat"
	autosubprod10 = "Red Hat Enterprise Linux for IBM System z"
	installedproductname10 = "Red Hat Enterprise Linux for IBM System z"
	productid10 = "RH0416249"
	pid10 = "72"
	pkgtoinstall10 = "zsh"
	productrepo10 = "rhel-5-for-system-z-rpms"
	betarepo10 = "rhel-5-for-system-z-beta-rpms"
	servicelevel10 = "STANDARD"
	releaselist10 = "5.7,5.8,5.9,5Server"

	# #RHEL-Server-ppc64-5
	username11 = "stage_test_14"
	password11 = "redhat"
	autosubprod11 = "Red Hat Enterprise Linux for IBM POWER"
	installedproductname11 = "Red Hat Enterprise Linux for IBM POWER"
	productid11 = "RH0326831"
	pid11 = "74"
	pkgtoinstall11 = "zsh"
	productrepo11 = "rhel-5-for-power-rpms"
	betarepo11 = "rhel-5-for-power-beta-rpms"
	servicelevel11 = "STANDARD"
	releaselist11 = "5.7,5.8,5.9,5Server"


	# [C] SAM Test parameters
	# #RHEL-Client-5
	# username1s = "admin"
	# password1s = "admin"
	# autosubprod1s = "Red Hat Enterprise Linux Desktop"
	# installedproductname1s = "Red Hat Enterprise Linux Desktop"
	# productid1s = "RH0823221"
	# pid1s = "68"
	# pkgtoinstall1s = "zsh"
	# productrepo1s = "rhel-5-desktop-rpms"
	# betarepo1s = "rhel-5-desktop-beta-rpms"
	# servicelevel1s = "STANDARD"
	# Add by wanghui
	username1s = "admin"
	password1s = "admin"
	# autosubprod1s = "Red Hat Employee Subscription"
	autosubprod1s = "Red Hat Enterprise Linux Desktop"
	installedproductname1s = "Red Hat Enterprise Linux Desktop"
	productid1s = "RH0823221"
	pid1s = "68"
	pkgtoinstall1s = "zsh"
	productrepo1s = "rhel-5-desktop-rpms"
	betarepo1s = "rhel-5-desktop-beta-rpms"
	servicelevel1s = "Standard"
	releaselist1s = "5.7,5.8,5.9,5Client"


	# #RHEL-Server-5
	# username2s = "admin"
	# password2s = "admin"
	# autosubprod2s = "Red Hat Enterprise Linux Server"
	# installedproductname2s = "Red Hat Enterprise Linux Server"
	# productid2s = "RH0197181"
	# pid2s = "69"
	# pkgtoinstall2s = "zsh"
	# productrepo2s = "rhel-5-server-rpms"
	# betarepo2s = "rhel-5-server-beta-rpms"
	# servicelevel2s = "STANDARD"
	# Add by wanghui
	username2s = "admin"
	password2s = "admin"
	# autosubprod2s = "Red Hat Employee Subscription"
	autosubprod2s = "Red Hat Enterprise Linux Server"
	installedproductname2s = "Red Hat Enterprise Linux Server"
	#modified by qianzhan
	#productid2s = "SYS0395"
	productid2s = "MCT2738"
	pid2s = "69"
	pkgtoinstall2s = "zsh"
	productrepo2s = "rhel-5-server-rpms"
	betarepo2s = "rhel-5-server-beta-rpms"
	servicelevel2s = "None"
	releaselist2s = "5.7,5.8,5.9,5Server"

	# #RHEL-Workstation-5
	username3s = "admin"
	password3s = "admin"
	autosubprod3s = "Red Hat Enterprise Linux Workstation"
	installedproductname3s = "Red Hat Enterprise Linux Workstation"
	productid3s = "RH0958488"
	pid3s = "71"
	pkgtoinstall3s = "zsh"
	productrepo3s = "rhel-5-workstation-rpms"
	betarepo3s = "rhel-5-workstation-beta-rpms"
	servicelevel3s = "STANDARD"
	releaselist3s = "5.7,5.8,5.9,5Workstation"

	# #RHEL-Client-6
	# username4s = "admin"
	# password4s = "admin"
	# autosubprod4s = "Red Hat Enterprise Linux Desktop"
	# installedproductname4s = "Red Hat Enterprise Linux Desktop"
	# productid4s = "RH0823221"
	# pid4s = "68"
	# pkgtoinstall4s = "zsh"
	# productrepo4s = "rhel-6-desktop-rpms"
	# betarepo4s = "rhel-6-desktop-beta-rpms"
	# servicelevel4s = "STANDARD"
	# Add by wanghui
	username4s = "admin"
	password4s = "admin"
	# autosubprod4s = "Red Hat Employee Subscription"
	autosubprod4s = "Red Hat Enterprise Linux Desktop"
	installedproductname4s = "Red Hat Enterprise Linux Desktop"
	productid4s = "SYS0395"
	pid4s = "68"
	pkgtoinstall4s = "zsh"
	productrepo4s = "rhel-6-desktop-rpms"
	betarepo4s = "rhel-6-desktop-beta-rpms"
	servicelevel4s = "STANDARD"
	releaselist4s = "6.1,6.2,6.3,6.4,6Client"

	# #RHEL-Server-6
	# username5s = "admin"
	# password5s = "admin"
	# autosubprod5s = "Red Hat Enterprise Linux Server"
	# installedproductname5s = "Red Hat Enterprise Linux Server"
	# productid5s = "RH0197181"
	# pid5s = "69"
	# pkgtoinstall5s = "zsh"
	# productrepo5s = "rhel-6-server-rpms"
	# betarepo5s = "rhel-6-server-beta-rpms"
	# servicelevel5s = "STANDARD"
	# Add by wanghui
	username5s = "admin"
	password5s = "admin"
	# autosubprod5s = "Red Hat Employee Subscription"
	autosubprod5s = "Red Hat Enterprise Linux Server"
	installedproductname5s = "Red Hat Enterprise Linux Server"
	#modified by qianzhan
	#productid5s = "SYS0395"
	productid5s = "MCT2738"
	pid5s = "69"
	pkgtoinstall5s = "zsh"
	productrepo5s = "rhel-6-server-rpms"
	betarepo5s = "rhel-6-server-beta-rpms"
	servicelevel5s = "None"
	releaselist5s = "6.1,6.2,6.3,6.4,6Server"

	# # RHEL-Server-7
	username6s = "admin"
	password6s = "admin"
	autosubprod6s = "Red Hat Enterprise Linux 7 Server High Touch Beta"
	installedproductname6s = "Red Hat Enterprise Linux 7 Server High Touch Beta"
	productid6s = "RH00076"
	pid6s = "230"
	pkgtoinstall6s = "zsh"
	productrepo6s = "rhel-7-server-htb-rpms"
	servicelevel6s = "Self-Support"
	prefix2="/sam/api"

	# [D] Candlepin Test parameters
	'''
	username1cc = "testuser2"
	password1cc = "password"
	autosubprod1cc = "Awesome OS Server Bits"
	installedproductname1cc = "Awesome OS Server Bits"
	productid1cc = "awesomeos-server-basic-me"
	pkgtoinstall1cc = "zlibs"
	productrepo1cc = "always-enabled-content"
	betarepo1cc = "never-enabled-content"
	servicelevel1cc = "Standard"
	'''
	usernamecc = "testuser2"
	passwordcc = "password"
	pkgtoinstallcc = "zlibs"
	productrepocc = "always-enabled-content"
	betarepocc = "never-enabled-content"
	servicelevelcc = "Standard"
	pidcc = "37060"
	autosubprodcc = "Awesome OS"

	# For x86_64 arch Stackable entitlement pool, Healing for expiration pool
	productid1cc = "awesomeos-x86_64"
	pid1cc = "100000000000002"
	productname1cc = "Awesome OS for x86_64 Bits"
	productidMultiE1cc = "awesomeos-x86_64"
	productidstack1cc = "awesomeos-x86_64"
	quantity1cc = "10"
	expires1cc = "2013-04-23"

	# For x86_32 arch Stackable entitlement pool, Healing for expiration pool
	productid2cc = "awesomeos-server-basic-me"
	pid2cc = "37060"
	productname2cc = "Awesome OS Server Bits"
	productidMultiE2cc = "awesomeos-server-basic-me"
	productidstack2cc = "awesomeos-x86_64"
	quantity2cc = "5"
	expires2cc = "2013-04-23"

	# For all the other arch arch Stackable entitlement pool, Healing for expiration pool
	productid3cc = "awesomeos-"
	pid3cc = "100000000000011"
	productname3cc = "9Awesome OS for x86_64/i686/ia64/ppc/ppc64/S390X/S390 Bits"
	productidMultiE3cc = "awesomeos-server-basic-me"
	productidstack3cc = "awesomeos-x86_64"
	quantity3cc = "5"
	expires3cc = "2013-04-23"

	# For RAM based subscription
	productidram = "ram-8gb"
	pidram = "801"
	productnameram = "RAM Limiting Package"
	productidMultiEram = "ram-4gb-stackable"
	productidstackram = "ram-2gb-stackable"
	quantityram = "10"
	expiresram = "2014-08-01"

	# For Core based subscription
	productidcore = "cores-26"
	pidcore = "806"
	productnamecore = "Cores Package"
	productidMultiEcore = "cores-8-stackable"
	productidstackcore = "cores-8-stackable"
	quantitycore = "10"
	expirescore = "2014-08-01"

	# For multi attri subscription
	productidcore = "sock-core-ram-multiattr"
	pidcore = "900"
	productnamecore = "Multi-Attribute"
	productidMultiEcore = "2cores-2ram-multiattr"
	productidstackcore = "sock-core-ram-multiattr"
	quantitycore = "10"
	expirescore = "2014-08-01"


	# Non multi entitlement pool
	productid4cc = "awesomeos-server"
	productname4cc = "Awesome OS Server Bundled"

	# # New function for ram core multi-attribute based product
	def get_newproduct(self, protype):

		env = {}
		if protype == "core":
			env["productname"] = self.productnamecore
			env["productid"] = self.productidcore
			env["pid"] = self.pidcore
			env["expires"] = self.expirescore
			env["quantity"] = self.quantitycore
			env["productidME"] = self.productidMultiEcore
			env["productidstack"] = self.productidstackcore
		elif protype == "ram":
			env["productname"] = self.productnameram
			env["productid"] = self.productidram
			env["pid"] = self.pidram
			env["expires"] = self.expiresram
			env["quantity"] = self.quantityram
			env["productidME"] = self.productidMultiEram
			env["productidstack"] = self.productidstackram
		else:
			env["productname"] = self.productnamemulti
			env["productid"] = self.productidmulti
			env["pid"] = self.pidmulti
			env["expires"] = self.expiresmulti
			env["quantity"] = self.quantitymulti
			env["productidME"] = self.productidMultiEmulti
			env["productidstack"] = self.productidstackmulti
		return env

	# # Common Functions ##
	def get_env(self, params):

		samhostname = params.get("samhostname")
		samhostip = params.get("samhostip")
		guest_name = params.get("guest_name")
		candlepinhostname = params.get("candlepinhostname")
		candlepinhostip = params.get("candlepinhostip")
		baseurl = params.get("baseurl")
		env = {}

		#local candlepin env
		if candlepinhostname != None and candlepinhostip != None and baseurl == 'https://%s:8443' % candlepinhostname:
			env["username"] = self.usernamecc
			env["password"] = self.passwordcc
			env["productrepo"] = self.productrepocc
			env["productrepo"] = self.productrepocc
			env["betarepo"] = self.betarepocc
			env["servicelevel"] = self.servicelevelcc
			env["autosubprod"] = self.autosubprodcc
			# below option seems worthless now remain for future use
			# env["installedproductname"] = self.installedproductname1cc

			if "64" in guest_name:
				env["productname"] = self.productname1cc
				env["productid"] = self.productid1cc
				env["pid"] = self.pid1cc
				env["expires"] = self.expires1cc
				env["quantity"] = self.quantity1cc
				env["productidME"] = self.productidMultiE1cc
				env["productidstack"] = self.productidstack1cc
			elif "32" in guest_name:
				env["productname"] = self.productname2cc
				env["productid"] = self.productid2cc
				env["pid"] = self.pid2cc
				env["expires"] = self.expires2cc
				env["quantity"] = self.quantity1cc
				env["productidME"] = self.productidMultiE2cc
				env["productidstack"] = self.productidstack2cc
			else:
				env["productname"] = self.productname3cc
				env["productid"] = self.productid3cc
				env["pid"] = self.pid3cc
				env["expires"] = self.expires3cc
				env["quantity"] = self.quantity1cc
				env["productidME"] = self.productidMultiE3cc
				env["productidstack"] = self.productidstack3cc

		#stage candlepin env
		elif (samhostname == None or samhostip == None) and (candlepinhostname == None or candlepinhostip == None) :
			if "RHEL-Everything-7" in guest_name:
				env["username"] = self.username70
				env["password"] = self.password70
				env["autosubprod"] = self.autosubprod70
				env["installedproductname"] = self.installedproductname70
				env["productid"] = self.productid70
				env["pid"] = self.pid70
				env["pkgtoinstall"] = self.pkgtoinstall70
				env["productrepo"] = self.productrepo70
				env["betarepo"] = self.betarepo70
				env["servicelevel"] = self.servicelevel70
				env["releaselist"] = self.releaselist70

			if "RHEL-Everything-ppc64-7" in guest_name:
				env["username"] = self.username71
				env["password"] = self.password71
				env["autosubprod"] = self.autosubprod71
				env["installedproductname"] = self.installedproductname71
				env["productid"] = self.productid71
				env["pid"] = self.pid71
				env["pkgtoinstall"] = self.pkgtoinstall71
				env["productrepo"] = self.productrepo71
				env["betarepo"] = self.betarepo71
				env["servicelevel"] = self.servicelevel71
				env["releaselist"] = self.releaselist71

			if "RHEL-Everything-s390x-7" in guest_name:
				env["username"] = self.username72
				env["password"] = self.password72
				env["autosubprod"] = self.autosubprod72
				env["installedproductname"] = self.installedproductname72
				env["productid"] = self.productid72
				env["pid"] = self.pid72
				env["pkgtoinstall"] = self.pkgtoinstall72
				env["productrepo"] = self.productrepo72
				env["betarepo"] = self.betarepo72
				env["servicelevel"] = self.servicelevel72
				env["releaselist"] = self.releaselist72

			if "RHEL-Workstation-7" in guest_name:
				env["username"] = self.username73
				env["password"] = self.password73
				env["autosubprod"] = self.autosubprod73
				env["installedproductname"] = self.installedproductname73
				env["productid"] = self.productid73
				env["pid"] = self.pid73
				env["pkgtoinstall"] = self.pkgtoinstall73
				env["productrepo"] = self.productrepo73
				env["betarepo"] = self.betarepo73
				env["servicelevel"] = self.servicelevel73
				env["releaselist"] = self.releaselist73

			if "RHEL-ComputeNode-7" in guest_name:
				env["username"] = self.username74
				env["password"] = self.password74
				env["autosubprod"] = self.autosubprod74
				env["installedproductname"] = self.installedproductname74
				env["productid"] = self.productid74
				env["pid"] = self.pid74
				env["pkgtoinstall"] = self.pkgtoinstall74
				env["productrepo"] = self.productrepo74
				env["betarepo"] = self.betarepo74
				env["servicelevel"] = self.servicelevel74
				env["releaselist"] = self.releaselist74

			if "RHEL-Server-ppc64-7" in guest_name:
				env["username"] = self.username75
				env["password"] = self.password75
				env["autosubprod"] = self.autosubprod75
				env["installedproductname"] = self.installedproductname75
				env["productid"] = self.productid75
				env["pid"] = self.pid75
				env["pkgtoinstall"] = self.pkgtoinstall75
				env["productrepo"] = self.productrepo75
				env["betarepo"] = self.betarepo75
				env["servicelevel"] = self.servicelevel75
				env["releaselist"] = self.releaselist75

			if "RHEL-Server-ppc64le-7" in guest_name:
				env["username"] = self.username80
				env["password"] = self.password80
				env["autosubprod"] = self.autosubprod80
				env["installedproductname"] = self.installedproductname80
				env["productid"] = self.productid80
				env["pid"] = self.pid80
				env["pkgtoinstall"] = self.pkgtoinstall80
				env["productrepo"] = self.productrepo80
				env["betarepo"] = self.betarepo80
				env["servicelevel"] = self.servicelevel80
				env["releaselist"] = self.releaselist80

			if "RHEL-Server-s390x-7" in guest_name:
				env["username"] = self.username76
				env["password"] = self.password76
				env["autosubprod"] = self.autosubprod76
				env["installedproductname"] = self.installedproductname76
				env["productid"] = self.productid76
				env["pid"] = self.pid76
				env["pkgtoinstall"] = self.pkgtoinstall76
				env["productrepo"] = self.productrepo76
				env["betarepo"] = self.betarepo76
				env["servicelevel"] = self.servicelevel76
				env["releaselist"] = self.releaselist76

			if "RHEL-Client-7" in guest_name:
				env["username"] = self.username77
				env["password"] = self.password77
				env["autosubprod"] = self.autosubprod77
				env["installedproductname"] = self.installedproductname77
				env["productid"] = self.productid77
				env["pid"] = self.pid77
				env["pkgtoinstall"] = self.pkgtoinstall77
				env["productrepo"] = self.productrepo77
				env["betarepo"] = self.betarepo77
				env["servicelevel"] = self.servicelevel77
				env["releaselist"] = self.releaselist77

			if "RHEL-Server-7" in guest_name:
				env["username"] = self.username78
				env["password"] = self.password78
				env["autosubprod"] = self.autosubprod78
				env["installedproductname"] = self.installedproductname78
				env["productid"] = self.productid78
				env["pid"] = self.pid78
				env["pkgtoinstall"] = self.pkgtoinstall78
				env["productrepo"] = self.productrepo78
				env["betarepo"] = self.betarepo78
				env["servicelevel"] = self.servicelevel78
				env["releaselist"] = self.releaselist78
				env["prefix"] = self.prefix1

			if "RHEL-Server-aarch64-7" in guest_name:
				env["username"] = self.username79
				env["password"] = self.password79
				env["autosubprod"] = self.autosubprod79
				env["installedproductname"] = self.installedproductname79
				env["productid"] = self.productid79
				env["pid"] = self.pid79
				env["pkgtoinstall"] = self.pkgtoinstall79
				env["productrepo"] = self.productrepo79
				env["betarepo"] = self.betarepo79
				env["servicelevel"] = self.servicelevel79
				env["releaselist"] = self.releaselist79

			if "RHEL-Client-6" in guest_name:
				env["username"] = self.username1
				env["password"] = self.password1
				env["autosubprod"] = self.autosubprod1
				env["installedproductname"] = self.installedproductname1
				env["productid"] = self.productid1
				env["pid"] = self.pid1
				env["pkgtoinstall"] = self.pkgtoinstall1
				env["productrepo"] = self.productrepo1
				env["betarepo"] = self.betarepo1
				env["servicelevel"] = self.servicelevel1
				env["releaselist"] = self.releaselist1

			elif "RHEL-Server-6" in guest_name:
				env["username"] = self.username2
				env["password"] = self.password2
				env["autosubprod"] = self.autosubprod2
				env["installedproductname"] = self.installedproductname2
				env["productid"] = self.productid2
				env["pid"] = self.pid2
				env["pkgtoinstall"] = self.pkgtoinstall2
				env["productrepo"] = self.productrepo2
				env["betarepo"] = self.betarepo2
				env["servicelevel"] = self.servicelevel2
				env["releaselist"] = self.releaselist2

			elif "RHEL-Workstation-6" in guest_name:
				env["username"] = self.username6
				env["password"] = self.password6
				env["autosubprod"] = self.autosubprod6
				env["installedproductname"] = self.installedproductname6
				env["productid"] = self.productid6
				env["pid"] = self.pid6
				env["pkgtoinstall"] = self.pkgtoinstall6
				env["productrepo"] = self.productrepo6
				env["betarepo"] = self.betarepo6
				env["servicelevel"] = self.servicelevel6
				env["releaselist"] = self.releaselist6

			elif "RHEL-ComputeNode-6" in guest_name:
				env["username"] = self.username7
				env["password"] = self.password7
				env["autosubprod"] = self.autosubprod7
				env["installedproductname"] = self.installedproductname7
				env["productid"] = self.productid7
				env["pid"] = self.pid7
				env["pkgtoinstall"] = self.pkgtoinstall7
				env["productrepo"] = self.productrepo7
				env["betarepo"] = self.betarepo7
				env["servicelevel"] = self.servicelevel7
				env["releaselist"] = self.releaselist7

			elif "RHEL-Server-s390x-6" in guest_name:
				env["username"] = self.username8
				env["password"] = self.password8
				env["autosubprod"] = self.autosubprod8
				env["installedproductname"] = self.installedproductname8
				env["productid"] = self.productid8
				env["pid"] = self.pid8
				env["pkgtoinstall"] = self.pkgtoinstall8
				env["productrepo"] = self.productrepo8
				env["betarepo"] = self.betarepo8
				env["servicelevel"] = self.servicelevel8
				env["releaselist"] = self.releaselist8

			elif "RHEL-Server-ppc64-6" in guest_name:
				env["username"] = self.username9
				env["password"] = self.password9
				env["autosubprod"] = self.autosubprod9
				env["installedproductname"] = self.installedproductname9
				env["productid"] = self.productid9
				env["pid"] = self.pid9
				env["pkgtoinstall"] = self.pkgtoinstall9
				env["productrepo"] = self.productrepo9
				env["betarepo"] = self.betarepo9
				env["servicelevel"] = self.servicelevel9
				env["releaselist"] = self.releaselist9

			elif "RHEL-Client-5" in guest_name:
				env["username"] = self.username3
				env["password"] = self.password3
				env["autosubprod"] = self.autosubprod3
				env["installedproductname"] = self.installedproductname3
				env["productid"] = self.productid3
				env["pid"] = self.pid3
				env["pkgtoinstall"] = self.pkgtoinstall3
				env["productrepo"] = self.productrepo3
				env["betarepo"] = self.betarepo3
				env["servicelevel"] = self.servicelevel3
				env["releaselist"] = self.releaselist3


			elif "RHEL-Server-5" in guest_name:
				env["username"] = self.username4
				env["password"] = self.password4
				env["autosubprod"] = self.autosubprod4
				env["installedproductname"] = self.installedproductname4
				env["productid"] = self.productid4
				env["pid"] = self.pid4
				env["pkgtoinstall"] = self.pkgtoinstall4
				env["productrepo"] = self.productrepo4
				env["betarepo"] = self.betarepo4
				env["servicelevel"] = self.servicelevel4
				env["releaselist"] = self.releaselist4


			elif "RHEL-Workstation-5" in guest_name:
				env["username"] = self.username5
				env["password"] = self.password5
				env["autosubprod"] = self.autosubprod5
				env["installedproductname"] = self.installedproductname5
				env["productid"] = self.productid5
				env["pid"] = self.pid5
				env["pkgtoinstall"] = self.pkgtoinstall5
				env["productrepo"] = self.productrepo5
				env["betarepo"] = self.betarepo5
				env["servicelevel"] = self.servicelevel5
				env["releaselist"] = self.releaselist5

			elif "RHEL-Server-s390x-5" in guest_name:
				env["username"] = self.username10
				env["password"] = self.password10
				env["autosubprod"] = self.autosubprod10
				env["installedproductname"] = self.installedproductname10
				env["productid"] = self.productid10
				env["pid"] = self.pid10
				env["pkgtoinstall"] = self.pkgtoinstall10
				env["productrepo"] = self.productrepo10
				env["betarepo"] = self.betarepo10
				env["releaselist"] = self.releaselist10

			elif "RHEL-Server-ppc64-5" in guest_name:
				env["username"] = self.username11
				env["password"] = self.password11
				env["autosubprod"] = self.autosubprod11
				env["installedproductname"] = self.installedproductname11
				env["productid"] = self.productid11
				env["pid"] = self.pid11
				env["pkgtoinstall"] = self.pkgtoinstall11
				env["productrepo"] = self.productrepo11
				env["betarepo"] = self.betarepo11
				env["releaselist"] = self.releaselist11
		#sam test env
		else:
			if "RHEL-Client-5" in guest_name:
				env["username"] = self.username1s
				env["password"] = self.password1s
				env["autosubprod"] = self.autosubprod1s
				env["installedproductname"] = self.installedproductname1s
				env["productid"] = self.productid1s
				env["pid"] = self.pid1s
				env["pkgtoinstall"] = self.pkgtoinstall1s
				env["productrepo"] = self.productrepo1s
				env["betarepo"] = self.betarepo1s
				env["servicelevel"] = self.servicelevel1s
				env["releaselist"] = self.releaselist1s
				env["prefix"] = self.prefix2

			elif "RHEL-Server-5" in guest_name:
				env["username"] = self.username2s
				env["password"] = self.password2s
				env["autosubprod"] = self.autosubprod2s
				env["installedproductname"] = self.installedproductname2s
				env["productid"] = self.productid2s
				env["pid"] = self.pid2s
				env["pkgtoinstall"] = self.pkgtoinstall2s
				env["productrepo"] = self.productrepo2s
				env["betarepo"] = self.betarepo2s
				env["servicelevel"] = self.servicelevel2s
				env["releaselist"] = self.releaselist2s
				env["prefix"] = self.prefix2

			elif "RHEL-Workstation-5" in guest_name:
				env["username"] = self.username3s
				env["password"] = self.password3s
				env["autosubprod"] = self.autosubprod3s
				env["installedproductname"] = self.installedproductname3s
				env["productid"] = self.productid3s
				env["pid"] = self.pid3s
				env["pkgtoinstall"] = self.pkgtoinstall3s
				env["productrepo"] = self.productrepo3s
				env["betarepo"] = self.betarepo3s
				env["servicelevel"] = self.servicelevel3s
				env["releaselist"] = self.releaselist3s
				env["prefix"] = self.prefix2

			elif "RHEL-Client-6" in guest_name:
				env["username"] = self.username4s
				env["password"] = self.password4s
				env["autosubprod"] = self.autosubprod4s
				env["installedproductname"] = self.installedproductname4s
				env["productid"] = self.productid4s
				env["pid"] = self.pid4s
				env["pkgtoinstall"] = self.pkgtoinstall4s
				env["productrepo"] = self.productrepo4s
				env["betarepo"] = self.betarepo4s
				env["servicelevel"] = self.servicelevel4s
				env["releaselist"] = self.releaselist4s
				env["prefix"] = self.prefix2

			elif "RHEL-Server-6" in guest_name:
				env["username"] = self.username5s
				env["password"] = self.password5s
				env["autosubprod"] = self.autosubprod5s
				env["installedproductname"] = self.installedproductname5s
				env["productid"] = self.productid5s
				env["pid"] = self.pid5s
				env["pkgtoinstall"] = self.pkgtoinstall5s
				env["productrepo"] = self.productrepo5s
				env["betarepo"] = self.betarepo5s
				env["servicelevel"] = self.servicelevel5s
				env["releaselist"] = self.releaselist5s
				env["prefix"] = self.prefix2

			elif "RHEL-Server-7" in guest_name:
				env["username"] = self.username6s
				env["password"] = self.password6s
				env["autosubprod"] = self.autosubprod6s
				env["installedproductname"] = self.installedproductname6s
				env["productid"] = self.productid6s
				env["pid"] = self.pid6s
				env["pkgtoinstall"] = self.pkgtoinstall6s
				env["productrepo"] = self.productrepo6s
				env["betarepo"] = self.betarepo5s
				env["servicelevel"] = self.servicelevel6s
				env["releaselist"] = self.releaselist5s
				env["prefix"] = self.prefix2

		return env

	'''
	def get_repos_and_pkgurlends(self,osver,relserver,product):
		""" get repos and package urls by product
		    @Param 'osver': used to indicate what the version of the testing os is, its value is like '5' for 5 series guest and '6' for 6 series guest.
		    @Param 'relserver': it's the indicator of 'beta' or 'dist'.
		    @Param 'product': used to set which product is being tested. All the products are:
			'client', 'computenode', 'highavailability', 'highperformancenetwork', 'hightouchbeta', 'loadbalancer', 'resilientstorage', 'sap', 'scalablefilesystem', 'server'
		"""

		repo_pkgurlends={}

		if product == "server":
			if "beta" in relserver:
				repo_pkgurlends={
					"rhel-%s-server-beta-rpms" % osver:"os/Packages/",
					"rhel-%s-server-beta-debug-rpms" % osver:"debug/",
					"rhel-%s-server-beta-source-rpms" % osver:"source/SRPMS/",
					"rhel-%s-server-supplementary-beta" % osver:"supplementary/os/Packages/",
					"rhel-%s-server-supplementary-beta-debuginfo" % osver:"supplementary/debug/",
					"rhel-%s-server-supplementary-beta-src" % osver:"supplementary/source/SRPMS/",
					"rhel-%s-server-vt-beta-rpms" % osver:"vt/os/Packages/",
					"rhel-%s-server-vt-beta-debug-rpms" % osver:"vt/os/debug/",
					"rhel-%s-server-vt-beta-source-rpms" % osver:"vt/source/SRPMS/"
				}
			else:
				repo_pkgurlends={
					"rhel-%s-server-rpms" % osver:"os/Packages/",
					"rhel-%s-server-debug-rpms" % osver:"debug/",
					"rhel-%s-server-source-rpms" % osver:"source/SRPMS/",
					"rhel-%s-server-supplementary" % osver:"supplementary/os/Packages/",
					"rhel-%s-server-supplementary-debuginfo" % osver:"supplementary/debug/",
					"rhel-%s-server-supplementary-src" % osver:"supplementary/source/SRPMS/",
					"rhel-%s-server-vt-rpms" % osver:"vt/os/Packages/",
					"rhel-%s-server-vt-debug-rpms" % osver:"vt/os/debug/",
					"rhel-%s-server-vt-source-rpms" % osver:"vt/source/SRPMS/"
				}

		##Note: needed to supplement the corresponding repo data and related pkg-url-end here for all the products
		elif product == "highavailability":
			if "beta" in relserver:
				repo_pkgurlends={}
			else:
				repo_pkgurlends={}

		elif product == "loadbalancer":
			if "beta" in relserver:
				repo_pkgurlends={}
			else:
				repo_pkgurlends={}


		return repo_pkgurlends
	'''

	# ========================================================
	# 	2. SAM Server Testing Parameters
	# ========================================================

	prior_env = "Library"
	default_org = "ACME_Corporation"
	default_env = "env1"
	default_provider = "Red Hat"
	default_provider_repo_url = "https://cdn.redhat.com"
	default_manifest = "default-manifest.zip"

	username1ss = "sam_test_1"
	password1ss = "redhat"
	email1 = "sam_test_1@localhost"
	org1 = "test_org1"
	env1 = "test_env1"
	keyname1 = "test_key1"
	systemname1 = "system_1"

	password2ss = "localhost"
	email2 = "sam_test_1@redhat.com"
	env2 = "test_env100"
	keyname2 = "test_key2"
	systemname2 = "system_2"

	# manifest1 = "hss-qe-sam20111213.zip"
	# manifest1_product1 = "Red Hat Enterprise Linux Server"
	# manifest1_product2 = "Red Hat Enterprise Linux High Availability for RHEL Server"
	# manifest2 = "hss-qe-sam20111213-update1-remove.zip"
	# manifest3 = "hss-qe-sam20111213-update2-add.zip"
	# specific_manifest = "rhel6.2-sam-htb.zip"
	manifest1 = "hss-qe-sam20120509.zip"
	manifest1_product1 = "Resilient Storage"
	manifest1_product2 = "Scalable File System"
	manifest2 = "hss-qe-sam20120509-update1-remove.zip"
	manifest3 = "hss-qe-sam20120509-update2-add.zip"
	specific_manifest = "rhel6.2-sam-htb.zip"


	# ========================================================
	#       3. Candlepin Server Testing Parameters
	# ========================================================

	# username1cc = "testuser2"
	# password1cc = "password"
	# productid1cc = "awesomeos-x86_64"


	# ========================================================
	#       4. Content Testing Parameters
	# ========================================================
	# url of having releasever: https://cdn.qa.redhat.com/content/dist/rhel/server/6/$releasever/$basearch/subscription-asset-manager/1/source/SRPMS
	# url without releasever: https://cdn.qa.redhat.com/content/dist/rhs/server/2.0/$basearch/source/SRPMS

	# ========================================================
	#       5. LDTP GUI test elements
	# ========================================================
	get_window = {
	######## For RHEL 5.X RHSM object locator ########
	'main-window-5.10':		      'Subscription Manager',
	'register-dialog-5':		     'register_dialog',
	'subscribe-dialog-5':		    'Subscribe System',

	######## For RHEL 6.X RHSM object locator ########
	'main-window-6':			 'frmSubscriptionManager',
	'register-dialog-6':		     'dlgregister_dialog',
	'subscribe-dialog-6':		    'frmSubscribeSystem',
	'import-certificate-dialog-6':	   'dlgProvideaSubscriptionCertificate',
	'import-cert-dialog-6':		  'dlgImportCertificates',
	'select-file-dialog-6':		  'dlgSelectAFile',
	'system-facts-dialog-6':		 'dlgfacts_dialog',
	'search-dialog-6':		       'frmSearching',
	'proxy-configuration-dialog-6':	  'dlgProxyConfiguration',
	'information-dialog-6':		  'dlgInformation',
	'question-dialog-6':		     'dlgQuestion',
	'error-dialog-6':			'dlgError',
	'system-preferences-dialog-6':	   'dlgSystemPreferences',
	'subscription-manager-manual-window-6':  'frmSubscriptionManagerManual',
	'onlinedocumentation-window-6':	  'frmRedHatSubscriptionManagement-RedHatCustomerPortal-MozillaFireFox',
	'security-warning-dialog-6':	     'dlgSecurityWarning',
	'about-subscription-manager-dialog-6':   'dlgAboutSubscriptionManager',
	'rhsm-notification-dialog-6':	    'dlgNotification',
	'filter-options-window-6':	       'frmFilterOptions',
	'error-cert-dialog-6':		   'dlgError',
	'sm-gui-warning-classic-dialog-6':	      'dlgWarning',
	#### window in firstboot gui for RHEL6.4
	'firstboot-main-window-6':			       'frm0',
	'firstboot-wng-dialog-6':				'dlgWarning',
	'firstboot-err-dialog-6':				'dlgError',
	# ## window in rhn-classic gui for RHEL6.4
	"classic-main-window-6":		"frmSystemRegistration",
	"classic-confirm-osrelease-window-6":		"dlgConfirmoperationsystemreleaseselection",
	"classic-updates-configured-window-6":		"frmUpdatesConfigured",
	}

	get_tab = {
	######## For RHEL 5.X RHSM object locator ########
	'all-tabs-5':			    'ptl0',
	'my-installed-software-5':	       'My Installed Products',
	'my-subscriptions-5':		    'My Subscriptions',
	'all-available-subscriptions-5':	 'All Available Subscriptions',
	######## For RHEL 6.X RHSM object locator ########
	'all-tabs-6':			    'ptl0',
	'my-installed-software-6':	       'ptabMyInstalledSoftware',
	'my-installed-software-6.4':	     'ptabMyInstalledProducts',
	'my-subscriptions-6':		    'ptabMySubscriptions',
	'all-available-subscriptions-6':	 'ptabAllAvailableSubscriptions',
	}

	get_button = {
	######## For RHEL 5.X RHSM object locator ########
	# button in main window
	'register-button-5':		     'Register System',
	'unregister-button-5':		   'btnUnregister',
	'auto-subscribe-button-5':	       'Auto-subscribe',
	'unsubscribe-button-5':		  'btnUnsubscribe',
	# button in register dialog
	'dialog-register-button-5':	      'register_button',
	'dialog-cancle-button-5':		'cancel_button',
	# button in subscribe dialog
	'dialog-subscribe-button-5':	     'btnSubscribe',
	'dialog-back-button-5':		  'btnBack',
	'dialog-cancle-button-5':		'btnCancel',
	######## For RHEL 6.X RHSM object locator ########
	# button in main window
	'register-button-6':		     'btnRegister',
	'register-button-6.4':		   'btnRegisterSystem',
	'unregister-button-6':		   'btnUnregister',
	'auto-subscribe-button-6':	       'btnAuto-subscribe',
	'auto-subscribe-button-6.4':	     'btnAuto-attach',
	# 'unsubscribe-button-6':		  'btnUnsubscribe',
	'remove-subscriptions-button-6':	 'btnRemove',
	'system-preferences-button-6':	   'btnSystemPreferences',
	'proxy-configuration-button-6':	  'btnProxyConfiguration',
	'view-system-facts-button-6':	    'btnViewSystemFacts',
	'import-certificate-button-6':	   'btnImportCertificate',
	'help-button-6':			 'btnHelp',
	'update-button-6':		       'btnSearch',
	'filters-button-6':		      'btnFilters',
	# button in register dialog
	'dialog-register-button-6':	      'btnregisterbutton',
	'configure-proxy-button-6':	      'btnproxybutton',
	'dialog-cancle-button-6':		'btncancelbutton',
	# button in subscribe dialog
	'dialog-subscribe-button-6':	     'btnSubscribe',
	'dialog-back-button-6':		  'btnBack',
	'dialog-cancle-button-6':		'btnCancel',
	'dialog-cancle-button-6.4':	      'btncancelbutton',
	# button in import-certificate-dialog
	'ok-button-6':			   'btnOK',
	'import-file-button-6':		  'btnImport',
    'type-pem-name-button-6':		'tbtnTypefilename',
	'certificate-location-button-6':	 'btn(None)',
	# button in select-file-dialog
	'type-file-name-button-6':	       'tbtnTypeafilename',
	'open-file-button-6':		    'btnOpen',
	'open-file-button-6.4':		  'btnImport',
	'proxy-close-button-6':		  'btnCloseButton',
	'yes-button-6':			  'btnYes',
	# button in system-preferences-dialog
	'close-button-6':			'btnClose',
	#### button in firstboot gui for RHEL6.4
	'firstboot-fwd-button-6':				'btnForward',
	'firstboot-agr-button-6':				'rbtnYes,IagreetotheLicenseAgreement',
	'firstboot-yes-button-6':				'btnYes',
	'firstboot-ok-button-6':				 'btnOK',
	'firstboot-finish-button-6':		     'btnFinish',
	'firstboot-register-now-button-6':			 "rbtnYes,I'dliketoregisternow",
	'firstboot-register-rhsm-button-6':			 'rbtnRedHatSubscriptionManagement',
	"firstboot-classic-select-button-6":		"rbtnRedHatNetwork(RHN)Classic",
	#### button in rhn_classic gui for RHEL6.4
	"classic-forward-button-6":		"btnForward",
	"classic-confirm-osrelease-yes-button-6":		"btnYes,Continue",
	"classic-updates-configured-finish-button-6":		"btnFinish",
	}

	get_table = {
	######## For RHEL 5.X RHSM object locator ########
	'my-product-table-5':		    'Installed View',
	'my-subscription-table-5':	       'My Subscriptions View',
	'all-subscription-table-5':	      'AllSubscriptionsView',
	'all-product-table-5':		   'tblAllAvailableBundledProductTable',
	'installed-product-table-5':	     'tblInstalledView',
	######## For RHEL 6.X RHSM object locator ########
	'my-product-table-6':		    'tblBundledProductsTable',
	'my-subscription-table-6':	       'ttblMySubscriptionsView',
	'all-subscription-table-6':	      'ttblAllSubscriptionsView',
	'all-product-table-6':		   'tblAllAvailableBundledProductTable',
	'installed-product-table-6':	     'tblInstalledView',
	'facts-view-table-6':		    'ttblfactsview',
	'orgs-view-table-6':		     'tblownertreeview',
	}

	get_text = {
	######## For RHEL 5.X RHSM object locator ########
	'login-text-5':			  'txtaccountlogin',
	'password-text-5':		       'txtaccountpassword',
	######## For RHEL 6.X RHSM object locator ########
	'login-text-6':			  'account_login',
	'password-text-6':		       'account_password',
	# text in select-file-dialog
	'location-text-6':		       'txtLocation',
	'proxy-location-text-6':		 'txtProxyLocation',
	'server-url-text-6':		     'txtserverentry',
	# firstboot for RHEL6.4
	'firstboot-login-text-6':		 'txtaccountlogin',
	'firstboot-password-text-6':		 'txtaccountpassword',
	# rhn_classic for RHEL6.4 ; firstboot-classic for RHEL6.4
	"classic-login-text-6":		"txtLogin",
	"classic-password-text-6":		"txtPassword",
	"classic-set-systemname-text-6":		"txtSystemName",

	}

	get_menu = {
	######## For RHEL 5.X RHSM object locator ########
	######## For RHEL 6.X RHSM object locator ########
	# under System menu
	'system-menu-6':			   'mnuSystem',
	'register-menu-6':			 'mnuRegister',
	'unregister-menu-6':		       'mnuUnregister',
	'importcert-menu-6':		       'mnuImportCert',
	'viewsystemfacts-menu-6':		  'mnuViewSystemFacts',
	'configureproxy-menu-6':		   'mnuConfigureProxy',
	'preferences-menu-6':		      'mnuPreferences',
	'quit-menu-6':			     'mnuQuit',
	# under Help menu
	'help-menu-6':			     'mnuHelp',
	'gettingstarted-menu-6':		   'mnuGettingStarted',
	'onlinedocumentation-menu-6':	      'mnuOnlineDocumentation',
	'about-menu-6':			    'mnuAbout',
	# service level menu
	'notset-menu-6':			   'mnuNotSet',
	'premium-menu-6':			  'mnuPremium',
	# release version menu
	'61-menu-6':			       'mnu61',
	'62-menu-6':			       'mnu62',
	'63-menu-6':			       'mnu63',
	'64-menu-6':			       'mnu64',
	'6server-menu-6':			  'mnu6Server',
	# import cert
	'ImportCertificate-menu-6':		'mnuImportCert',
	}

	get_checkbox = {
	######## For RHEL 5.X RHSM object locator ########
	######## For RHEL 6.X RHSM object locator ########
	'manual-attach-checkbox-6':		'chkautobind',
	'proxy-checkbox-6':			'chkProxyCheckbox',
	'match-system-checkbox-6':		 'chkMatchSystem',
	'match-installed-checkbox-6':	      'chkMatchInstalled',
	'do-not-overlap-checkbox-6':	       'chkDoNotOverlap',
	# ##firstboot checkbox for RHEL6.4
	'firstboot-manual-checkbox-6':		   'chkautobind',
	'firstboot_activationkey-checkbox-6':	   'chkIwilluseanActivationKey',

	}

	get_label = {
	######## For RHEL 5.X RHSM object locator ########
	######## For RHEL 6.X RHSM object locator ########
	'import-cert-success-label-6':	      	'lblCertificateimportwassuccessful',
	'register-error-label-6':		   	'lblUnabletoregisterthesystemInvalidusernameorpasswordTocreatealogin,pleasevisithttps//wwwredhatcom/wapps/ugc/registerhtmlPleasesee/var/log/rhsm/rhsmlogformoreinformation',
	'search-subscriptions-hint-label-6':		'lbl2applied',
	'error-user-label-6':			   'lblUserusertestisnotabletoregisterwithanyorgs',
	'warning-classic-already-label-6':	      'lblWARNINGThissystemhasalreadybeenregisteredwithRedHatusingRHNClassicThetoolyouareusingisattemptingtore-registerusingRedHatSubscriptionManagementtechnologyRedHatrecommendsthatcustomersonlyregisteronceTolearnhowtounregisterfromeitherservicepleaseconsultthisKnowledgeBaseArticlehttps//accessredhatcom/kb/docs/DOC-45563',
	###### firstboot label in RHEL6.4
	'firstboot-registeration-warning-label-6':  	'lblYoursystemwasregisteredforupdatesduringinstallation',
	'firstboot_creat_user-label-6':	     	"lblYoumustcreatea'username'forregular(non-administrative)useofyoursystemTocreateasystem'username',pleaseprovidetheinformationrequestedbelow",
	'firstboot-skip-auto-label-6':		    		"lblYouhaveoptedtoskipauto-attach",
	"firstboot-classic-reviewsubscription-label-6":		"lblReviewSubscription",
	"firstboot-classic-finishupdate-label-6":			"lblFinishUpdatesSetup",
	###### rhn_classic label in RHEL6.4
	"classic-software-update-label-6":		"lblSetUpSoftwareUpdates",
	"classic-choose-service-label-6":		"lblChooseService",
	"classic-redhat-account-label-6":		"lblRedHatAccount",
	"classic-OS-realeaseversion-label-6":		"lblOperatingSystemReleaseVersion",
	"classic-create-profile-label-6":		"lblCreateProfile",
	"classic-review-subscription-label-6":		"lblReviewSubscription",
	}

	get_combobox = {
	######## For RHEL 5.X RHSM object locator ########
	######## For RHEL 6.X RHSM object locator ########
	'service-level-notset-combobox-6':	  'cboNotSet',
	'service-level-premium-combobox-6':	 'cboPremium',
	'service-level-none-combobox-6':	    'cboNone',
	'release-version-combobox-6':	       'cbo1',
	'release-version-6server-combobox-6':       'cbo6Server',
	}
	get_progressbar = {
	##for RHEL 6.x ####
	'register-progressbar-6':		   'pbarregisterprogressbar',

	}
