import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268795_rhsm_release_should_not_include_5u6(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		#register
		eu().sub_register(session, username, password)
		# autosubscribe
		auto_attach(session, autosubprod)
		# release list
		cmd = "subscription-manager release --list | grep 5.6"
		(ret,output)=eu().runcmd(session,cmd,"release list")
		if ret != 0:
			logging.info("It's successful to check the release list without 5.6")
		else:
			raise error.TestFail("Test Failed - Failed to check the release list without 5.6")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe with --force:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def auto_attach(session, autosubprod):
	cmd = "subscription-manager subscribe --auto"
	(ret,output)=eu().runcmd(session,cmd,"autosubscribe")
	if ret == 0 and autosubprod in output and "Status:Subscribed" in output:
		logging.info("It's successful to autosubscribe")
	else:
		raise error.TestFail("Test Failed - Failed to autosubscribe")
