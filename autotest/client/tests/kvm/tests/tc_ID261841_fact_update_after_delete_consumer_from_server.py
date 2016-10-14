import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID261841_fact_update_after_delete_consumer_from_server(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]

		if params.get("samhostip") != None:
			hostname=params.get("samhostname")
		else:
			hostname="subscription.rhn.stage.redhat.com"

		#eu().sub_register_with_orgkey(session, username, password, org_key)
		eu().sub_register(session, username, password)
		
		#record the consumer ID
		consumerid=eu().sub_get_consumerid(session)
		#Delete the consumer from server-side
		delete_consumer_server_side(session,username,password,hostname,consumerid)
		
		#update facts
		out="Consumer %s has been deleted"%consumerid
		cmd="subscription-manager facts --update"
		(ret,output)=eu().runcmd(session,cmd,"update facts")
		if ret != 0 and out in output:
			logging.info("It's successful to verify fact_update_after_delete_consumer_from_server")
		else:
			raise error.TestFail("Test Failed - Failed to verify fact_update_after_delete_consumer_from_server")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when fact_update_after_delete_consumer_from_server:"+str(e))
		
	finally:
		clean_after_delete_from_server(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def delete_consumer_server_side(session,username,password,hostname,consumerid):
	cmd="curl -k -u %s:%s --request DELETE https://%s:443/subscription/consumers/%s"%(username,password,hostname,consumerid)
	(ret,output)=eu().runcmd(session,cmd,"Delete the consumer from server-side")
	if ret == 0:
		logging.info("It's successful to Delete the consumer from server-side.")
	else:
		raise error.TestFail("Test Failed - Failed to Delete the consumer from server-side.")

def clean_after_delete_from_server(session):
	cmd="subscription-manager clean"
	(ret,output)=eu().runcmd(session,cmd,"clean_after_delete_from_server")
	if ret == 0 and "All local data removed" in output:
		logging.info("It's successful to clean_after_delete_from_server")
	else:
		raise error.TestFail("Test Failed - error happened when clean_after_delete_from_server")
