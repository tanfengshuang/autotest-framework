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

def run_tc_ID178147_register_with_max_system_name(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		name249='qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert1234'
		name250='qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345qwert12345'

		#register use system name with max characters(249)
		cmd_register="subscription-manager register --username=%s --password='%s' --name=%s"%(username, password, name249)
		(ret,output)=eu().runcmd(session,cmd_register,"register with max system name")
		if ret==0 and 'The system has been registered with ID' in output:
			logging.info("It's successful to register with max system name")
		else:
			raise error.TestFail("Test Failed - error happened when register with max system name")

		#unregister when system has registered using system name with max characters(249)
		cmd_unregister="subscription-manager unregister"
		(ret,output)=eu().runcmd(session,cmd_unregister,"unregister when system has registered using system name with max characters(249)")
		if ret==0 and 'System has been unregistered' in output:
			logging.info("It's successful to unregister after system has registered using system name with max system name")
		else:
			raise error.TestFail("Test Failed - error happened when unregister system") 

		#clean client data
		cmd_clean="subscription-manager clean"
		(ret,output)=eu().runcmd(session,cmd_clean,"clean client data")
		if (ret==0) and ("All local data removed" in output):
			logging.info("It's successful to run subscription-manager clean")
		else:
			raise error.TestFail("Test Failed - error happened when run subscription-manager clean")

		#re-register with max characters(>=250)
		cmd_register="subscription-manager register --username=%s --password='%s' --name=%s"%(username, password,name250)
		(ret,output)=eu().runcmd(session,cmd_register,"register with max characters(>=250)")
		if (ret!=0) and ("Name of the unit must be shorter than 250 characters" in output):
			logging.info("It's successful to verify that registeration with max characters(>=250) should not succeed")
		else:
			raise error.TestFail("Test Failed - error happened when re-register with max characters(>=250)")
	except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when register with max system name:"+str(e))
	finally:
			eu().sub_unregister(session)
			logging.info("=========== End of Running Test Case: %s ==========="%__name__)

