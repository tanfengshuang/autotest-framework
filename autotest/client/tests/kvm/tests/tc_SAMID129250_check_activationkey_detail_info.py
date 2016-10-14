import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129250_check_activationkey_detail_info(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
	        #create an activationkey
        	eu().sam_create_activationkey(session, ee.keyname1, ee.default_env, ee.default_org)

                #check activationkey detail info
		cmd="headpin -u admin -p admin activation_key info --name=%s --org=%s" %(ee.keyname1, ee.default_org)
		(ret,output)=eu().runcmd(session,cmd,"check activation_key detail info")

		if (ret == 0) and (ee.keyname1 in output):
			logging.info("It's successful to check activation_key %s detail info."%(ee.keyname1))
		else:
			raise error.TestFail("It's failed to check activation_key %s detail info."%(ee.keyname1))

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do check an activation_key detail info:"+str(e))
	finally:
		eu().sam_delete_activationkey(session, ee.keyname1, ee.default_org)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
