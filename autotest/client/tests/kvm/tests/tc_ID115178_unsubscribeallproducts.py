import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115178_unsubscribeallproducts(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
 		#[A] - prepare test env
 		
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#prepare a env auto subsribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)      

 		#[B] - run the test
		#unsubscribe all products
		cmd="subscription-manager unsubscribe --all"
		(ret,output)=eu().runcmd(session,cmd,"unsubscribe")
		
		expectout = "This machine has been unsubscribed from"
		#for rhel6.4 new output version
		expectoutnew64 = "subscription removed from this system."
		#for rhel5.10 new output version
		expectoutnew510 = "subscription removed at the server."
		if ret == 0 and (expectout in output or expectoutnew510 in output or expectoutnew64 in output):
			if len(os.listdir('/etc/pki/entitlement'))<=0:
				logging.info("It's successful to unsubscribe from all products.")
			else:
				raise error.TestFail("Test Failed - The information shown that it's failed to unsubscribe from all products.")
		else:
			raise error.TestFail("Test Failed - Failed to unsubscribe from all products.")
                
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do unsubscribe from all products:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
