import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID330287_man_page_entry_for_new_repo_override_module(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		# Check repo-override module and all of it options in man page
		cmd = "man subscription-manager | col -b | egrep 'REPO-OVERRIDE OPTIONS' -A30"
		(ret,output)=eu().runcmd(session,cmd,"check man page for repo-override")
		if ret == 0 and "REPO-OVERRIDE OPTIONS" in output and "--repo" in output and "--add=NAME:VALUE" in output and "--remove=NAME" in output and "--remove-all" in output and "--list" in output:
			logging.info("It's successful to check man page for repo-override.") 
		else:
			raise error.TestFail("Test Failed - Failed to check man page for repo-override.")
		
		# Check repo-override option in subscription-manager help
		cmd = "subscription-manager --help | grep repo-override"
		(ret,output)=eu().runcmd(session,cmd,"Check repo-override option in subscription-manager help")
		if ret == 0 and "Manage custom content repository settings" in output:
			logging.info("It's successful to Check repo-override option in subscription-manager help.") 
		else:
			raise error.TestFail("Test Failed - Failed to Check repo-override option in subscription-manager help.")
		
		# subscription-manager repo-override --help
		cmd = "subscription-manager repo-override --help"
		(ret,output)=eu().runcmd(session,cmd,"Check repo-override help")
		if ret == 0 and "Usage: subscription-manager repo-override [OPTIONS]" in output:
			logging.info("It's successful to Check repo-override help.") 
		else:
			raise error.TestFail("Test Failed - Failed to Check repo-override help.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the subscription type:"+str(e))
		
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
