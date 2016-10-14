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

def run_tc_ID178051_register_with_invalid_username_and_password(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		invalidpassword=test
		cmd="subscription-manager register --username=%s --password='%s'"%(username,invalidpassword)
		(ret,output)=eu().runcmd(session,cmd,"register with invalid username and password")
		if ret != 0:
			if ("Invalid credentials" in output):
				logging.info("It's successful to verify that invalid password can not be used to register.")
			else:
				raise error.TestFail("Test Failed - The information shown after registeration with invalid username and password is not correct.")
		else:
			raise error.TestFail("Test Failed - Failed to verify registering with invalid username and password.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when verify registering with invalid username and password:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
