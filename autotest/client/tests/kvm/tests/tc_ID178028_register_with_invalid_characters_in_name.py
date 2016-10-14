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

def run_tc_ID178028_register_with_invalid_characters_in_name(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		systemname='test+?test'
		cmd="subscription-manager register --username=%s --password='%s' --name=%s"%(username,password,systemname)
		(ret,output)=eu().runcmd(session,cmd,"register with invalid character in name")
		if ret != 0:
			if ("Problem creating unit" in output) or ("System name cannot contain most special characters." in output):
				logging.info("It's successful to verify that invalid systemname can not be used to register.")
			else:
				raise error.TestFail("Test Failed - The information shown after registered with invalid character in name is not correct.")
		else:
			raise error.TestFail("Test Failed - Failed to verify registering with invalid system name.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when verify registering with invalid system name:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


