import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115176_unregisterfromserver(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		#unregister from server
                cmd="subscription-manager unregister"
		(ret,output)=eu().runcmd(session,cmd,"unregister")

		if ret == 0:
                	if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                        	logging.info("It's successful to unregister.")
                	else:
                        	raise error.TestFail("Test Failed - The information shown after unregistered is not correct.")
		else:
                	raise error.TestFail("Test Failed - Failed to unregister.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto-subscribe:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

