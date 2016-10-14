import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID267325_access_cdn_through_thumbslug_using_plain_http(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:  
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		pkgtoinstall = ee().get_env(params)["pkgtoinstall"]
		#register to and auto-attach
		register_and_autosubscribe(session, username, password, autosubprod)
		# set rhsm.conf file to plain http
		set_conf_plain(session)
		#install a pkg
		cmd = "yum install -y %s" % (pkgtoinstall)
		(ret, output) = eu().runcmd(session, cmd, "install selected package %s" % pkgtoinstall, timeout=20000)
		if ret != 0 and "Error Downloading Packages:" in output and "No more mirrors to try" in output:
			logging.info("It's successful to verify that system cannot access CDN  contents through thumbslug by using plain http")
		else:
			raise error.TestFail("Test Failed - failed to verify that system cannot access CDN  contents through thumbslug by using plain http")
		# restore rhsm.conf file
		restore_conf(session)
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when doing install one package of subscribed product:" + str(e))
	finally:
		uninstall_givenpkg(session, pkgtoinstall)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

def register_and_autosubscribe(session, username, password, autosubprod):
	cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
	(ret, output) = eu().runcmd(session, cmd, "register_and_autosubscribe", timeout=20000)
	if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
		logging.info("It's successful to register and auto-attach")
	else:
		raise error.TestFail("Test Failed - failed to register or auto-attach.")

def set_conf_plain(session):
	cmd = "sed -i 's/baseurl= https:\/\/samserv.redhat.com:8088/baseurl= http:\/\/samserv.redhat.com:8088/g' /etc/rhsm/rhsm.conf;cat /etc/rhsm/rhsm.conf | grep baseurl"
	(ret, output) = eu().runcmd(session, cmd, "set_conf_plain")
	if ret == 0 and "baseurl= http://samserv.redhat.com:8088" in output:
		logging.info("It's successful to set the rhsm.conf to plain http")
	else:
		raise error.TestFail("Test Failed - failed to set the rhsm.conf to plain http")
	
def restore_conf(session):
	cmd = "sed -i 's/baseurl= http:\/\/samserv.redhat.com:8088/baseurl= https:\/\/samserv.redhat.com:8088/g' /etc/rhsm/rhsm.conf;cat /etc/rhsm/rhsm.conf | grep baseurl"
	(ret, output) = eu().runcmd(session, cmd, "set_conf_plain")
	if ret == 0 and "baseurl= https://samserv.redhat.com:8088" in output:
		logging.info("It's successful to restore the rhsm.conf")
	else:
		raise error.TestFail("Test Failed - failed to restore the rhsm.conf")

def uninstall_givenpkg(session, testpkg):
	cmd = "rpm -qa | grep %s"%(testpkg)
	(ret, output) = eu().runcmd(session, cmd, "check package %s" % testpkg, timeout=20000)
	if ret ==1:
		logging.info("There is no need to remove package")
	else:
		cmd = "yum remove -y %s" % (testpkg)
		(ret, output) = eu().runcmd(session, cmd, "remove select package %s" % testpkg, timeout=20000)
		if ret == 0 and "Complete!" in output and "Removed" in output:
			logging.info("The package %s is uninstalled successfully." % (testpkg))
		elif ret == 0 and "No package %s available"%testpkg in output:
			logging.info("The package %s is not installed at all" %(testpkg))
		else: 
			raise error.TestFail("Test Failed - The package %s is failed to uninstall." % (testpkg))

