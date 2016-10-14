import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115146_registerandautosubscribe(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		cmd="subscription-manager register --username=%s --password=%s --autosubscribe"%(username,password)
		(ret,output)=eu().runcmd(session,cmd,"register and auto-subscribe")

		productid=ee().get_env(params)["productid"]
		autosubprod=ee().get_env(params)["autosubprod"]
		if ret == 0:
			if ("The system has been registered with ID" in output) or ("The system has been registered with id" in output)\
                           and (autosubprod in output) and ("Subscribed" in output) and ("Not Subscribed" not in output):
                                #eu().sub_checkentitlementcerts(session,productid)                                
				if eu().sub_checkidcert(session): logging.info("It's successful to register.")
				else: raise error.TestFail("Test Failed - Failed to register.")
			else:
				raise error.TestFail("Test Failed - Failed to register and auto-subscribe correct product.")
		else:
			raise error.TestFail("Test Failed - Failed to register and auto-subscribe.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do register and auto-subscribe:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


