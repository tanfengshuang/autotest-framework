"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID180671_subscribe_bogus_pool(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#register a system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#Subscribe to a bogus pool ID
		cmd="subscription-manager subscribe --pool=1234567890"
		(ret, output) = eu().runcmd(session, cmd, "Subscribe to a bogus pool ID 1234567890")

		#if ret != 0 and "Subscription pool 1234567890 does not exist" in output :
		if ret != 0 and "Pool with id 1234567890 could not be found" in output :
			logging.info("It's successful to check subscribe to a bogus pool ID")
		else:
			raise error.TestFail("Test Failed - Failed to check Subscribe to a bogus pool ID")

		#Check the entitlement cert
		cmd="ll /etc/pki/entitlement"
		(ret, output) = eu().runcmd(session, cmd, "Check the entitlement cert")

		if (ret == 0) and ("total 0" in output):
			logging.info("It's successful to Check the entitlement cert--no file")
		else:
			raise error.TestFail("Test Failed - Failed to Check the entitlement cert--has file")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check subscribe to a bogus pool ID:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Runnidng Test Case: %s ==========="%__name__)
