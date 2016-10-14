import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262264_remove_hyphen_from_unregister(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		#register
		eu().sub_register(session, username, password)
		
		# unregister
		cmd = "subscription-manager unregister"
		(ret,output)=eu().runcmd(session,cmd,"unregister")
		if ret == 0 and 'System has been unregistered.' in output:
			logging.info("It's successful to check to remove hyphen from un-register")
		else:
				raise error.TestFail("Test Failed - Failed to check to remove hyphen from un-register")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe with --force:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
