import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID267324_access_cdn_without_entitlement_cert(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		pkgtoinstall = ee().get_env(params)["pkgtoinstall"]
		#register to and auto-attach
		register_and_autosubscribe(session, username, password, autosubprod)
		# remove all cert files under /etc/pki/entitlement/
		remove_ent_cert(session)
		#install a pkg
		cmd = "yum install -y %s" % (pkgtoinstall)
		(ret, output) = eu().runcmd(session, cmd, "install selected package %s" % pkgtoinstall, timeout=20000)
		if ret == 1 and "No package %s available."%pkgtoinstall in output:
			logging.info("It's successful to verify that system without entitlement certificates cannot access CDN  contents through thumbslug")
		else:
			raise error.TestFail("Test Failed - failed to verify that system without entitlement certificates cannot access CDN  contents through thumbslug")
		
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

def remove_ent_cert(session):
	cmd = "rm -f /etc/pki/entitlement/*"
	(ret, output) = eu().runcmd(session, cmd, "remove all entitlement certs")
	if ret == 0:
		logging.info("It's successful to remove all entitlement certs")
	else:
		raise error.TestFail("Test Failed - failed to remove entitlement cert")

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
