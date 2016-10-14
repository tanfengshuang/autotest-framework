import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190818_check_subscribetopool_output(test, params, env):
	
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" %__name__)
	
	try:
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)

		#list availalbe entitlement pools
		productid = ee().get_env(params)["productid"]
		availpoollist = eu().sub_listavailpools(session, productid)
		
		#get an available entitlement pool to subscribe with random.sample
		availpool = random.sample(availpoollist, 1)[0]
		if "SubscriptionName" in availpool:
			if "PoolId" in availpool:
				poolid = availpool["PoolId"]
				subscriptionname = availpool["SubscriptionName"]
			else:
				poolid = availpool["PoolID"]
				subscriptionname = availpool["SubscriptionName"]
		#subscribe the product with poolid
		cmd = "subscription-manager subscribe --pool=%s" %poolid
		(ret, output) = eu().runcmd(session, cmd, "subscribe with poolid")
		expectout = "Successfully consumed a subscription for: %s" %subscriptionname
		expectoutnew = "Successfully attached a subscription for: %s" %subscriptionname
		
		if 0 == ret and (expectout in output or expectoutnew in output) :
			logging.info("It's Successfull to verify the output of cmd subscription-manager subscribe --pool=<poolid>!")
		else:
			raise error.TestFail("Test Faild - Failed to verify the output of cmd subscription-manager subscribe --pool=<poolid>!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the output of cmd subscription-manager subscribe --pool=<poolid>:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("========== End of Running Test Case: %s ==========" %__name__)
