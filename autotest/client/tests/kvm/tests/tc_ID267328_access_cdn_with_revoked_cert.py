import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID267328_access_cdn_with_revoked_cert(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		pkgtoinstall = ee().get_env(params)["pkgtoinstall"]
		#register to and auto-attach
		register_and_autosubscribe(session, username, password, autosubprod)
		# unregister
		eu().sub_unregister(session)
		#install a pkg
		cmd = "yum install -y %s" % (pkgtoinstall)
		(ret, output) = eu().runcmd(session, cmd, "install selected package %s" % pkgtoinstall, timeout=20000)
		if ret == 1 and "No package %s available."%pkgtoinstall in output:
			logging.info("It's successful to verify that system cannot access CDN contents through thumbslug with revoked cert")
		else:
			raise error.TestFail("Test Failed - failed to verify that system cannot access CDN contents through thumbslug with revoked cert")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when doing install one package of subscribed product:" + str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

def register_and_autosubscribe(session, username, password, autosubprod):
	cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
	(ret, output) = eu().runcmd(session, cmd, "register_and_autosubscribe", timeout=20000)
	if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
		logging.info("It's successful to register and auto-attach")
	else:
		raise error.TestFail("Test Failed - failed to register or auto-attach.")
