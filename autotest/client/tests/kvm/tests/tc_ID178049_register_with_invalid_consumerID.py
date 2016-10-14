"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID178049_register_with_invalid_consumerID(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		#register first time
		eu().sub_register(session,username,password)
		#autosubscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#clean client data
		cmd_clean="subscription-manager clean"
		(ret,output)=eu().runcmd(session,cmd_clean,"clean client data")
		if (ret==0) and ("All local data removed" in output):
			logging.info("It's successful to run subscription-manager clean")
		else:
			raise error.TestFail("Test Failed - error happened when run subscription-manager clean")

		#register with invalid consumerid
		cmd_register="subscription-manager register --username=%s --password='%s' --consumerid=1234567890"%(username, password)
		(ret,output)=eu().runcmd(session,cmd_register,"register with invalid consumerid")
		if (ret!=0) and ("Consumer with id 1234567890 could not be found" in output):
			logging.info("It's successful to verify that registeration with invalid consumerid should not succeed")
		else:
			raise error.TestFail("Test Failed - error happened when register with invalid consumerid")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when register with invalid consumerid:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


