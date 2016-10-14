import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID126355_registerwithproxy(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        try:
			if params.get("samhostip"):
				logging.info("skip sam proxy testing")
			else:
				username=ee().get_env(params)["username"]
				password=ee().get_env(params)["password"]
				cmd="subscription-manager register --username=%s --password=%s --proxy=%s"%(username,password,ee.proxy)
				(ret,output)=eu().runcmd(session,cmd,"register with proxy")

				if ret == 0:
					if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
						logging.info("It's successful to register.")
					else:
						raise error.TestFail("Test Failed - The information shown after registered is not correct.")
				else:
					raise error.TestFail("Test Failed - Failed to register with proxy.")
        except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do reigster with a proxy:"+str(e))
        finally:
                eu().sub_unregister(session)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
