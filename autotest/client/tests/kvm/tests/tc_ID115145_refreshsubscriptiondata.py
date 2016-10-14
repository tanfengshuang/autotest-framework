import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115145_refreshsubscriptiondata(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
        #register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
		 		
 		#[A] - prepare a env auto subsribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

 		#[B] - run the test
		#get serialnumlist before remove local subscription data
		serialnumlist_pre = eu().get_subscription_serialnumlist(session)

		#rm the subscription data
		cmd="rm -f /etc/pki/entitlement/*"
		(ret,output)=eu().runcmd(session,cmd,"remove local entitlement cert")
		if ret == 0:
			logging.info("It's successful to remove all local subscription data.")
		else:
			raise error.TestFail("Test Failed - It's failed to remove all local subscription data.")

		#refresh subscription data from candlepin server
		cmd="subscription-manager refresh"
		(ret,output)=eu().runcmd(session,cmd,"refresh subscriptions data")
                
		if ret == 0 and "All local data refreshed" in output:
		#get serialnumlist after refresh subscription data from server
			serialnumlist_post = eu().get_subscription_serialnumlist(session)
			if len(serialnumlist_post) == len(serialnumlist_pre) and serialnumlist_post.sort() == serialnumlist_pre.sort():
				logging.info("It's successful to refresh all subscription data from server.")
			else:
				raise error.TestFail("Test Failed - It's failed to refresh all subscription data from server.") 
		else:
			raise error.TestFail("Test Failed - Failed to refresh all subscription data from server.")
                
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do refresh subscription data from server:"+str(e))
	finally:
                eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
