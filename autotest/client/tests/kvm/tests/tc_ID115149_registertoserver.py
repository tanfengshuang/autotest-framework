import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115149_registertoserver(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
	        #register to server
        	username=ee().get_env(params)["username"]
        	password=ee().get_env(params)["password"]
        	#eu().sub_register(session,username,password)

                cmd="subscription-manager register --username=%s --password='%s'"%(username, password)
                (ret, output)=eu().runcmd(session, cmd, "register")

                if ret == 0:
                        if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                                logging.info("It's successful to register.")
                        else:
                                raise error.TestFail("Test Failed - The information shown after registered is not correct.")
                else:
                        raise error.TestFail("Test Failed - Failed to register.")


	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do register to server:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

