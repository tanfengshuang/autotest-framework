import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262128_pool_id_should_exist_in_list_consumed(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]

		eu().sub_register(session, username, password)
		
		#List the available pool and record the pool id
		cmd1="subscription-manager list --available"
		pool_id_avail=list_and_record_pool_id(session, cmd1)
		
		#subscribe with pool id
		eu().sub_subscribetopool(session, pool_id_avail)
		
		#List the consumed and record the pool id
		cmd2="subscription-manager list --consumed"
		pool_id_consumed=list_and_record_pool_id(session, cmd2)
		
		#compare the pool id
		if pool_id_avail == pool_id_consumed:
			logging.info("It's successful to check pool_id_should_exist_in_list_consumed")
		else:
			raise error.TestFail("Test Failed - Failed to check pool_id_should_exist_in_list_consumed")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check pool_id_should_exist_in_list_consumed:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def list_and_record_pool_id(session, command):
	cmd = "%s | grep 'Pool ID:' | head -1"%command
	(ret,output)=eu().runcmd(session,cmd,"get pool id")
	if ret == 0 and output != None:
		logging.info("It's successful to get pool id with command %s"%command)
		poolid=output.split(":")[1].strip()
		return poolid
	else:
		raise error.TestFail("Test Failed - Failed to get pool id")
