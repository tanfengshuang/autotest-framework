import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID270211_rhsm_man_page_indicate_registration_using_activationkey(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		cmd = 'man subscription-manager | grep "activationkey" -B13'
		(ret,output)=eu().runcmd(session,cmd,"registration needs org with activationkey")
		if ret == 0 and 'subscription-manager register --org="IT Dept" --activationkey=1234abcd' in output:
			logging.info("It's successful to check registration needs org with activationkey")
		else:
				raise error.TestFail("Test Failed - Failed to check registration needs org with activationkey")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to registration needs org with activationkey:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
