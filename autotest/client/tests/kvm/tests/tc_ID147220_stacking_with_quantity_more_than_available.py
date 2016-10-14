import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID147220_stacking_with_quantity_more_than_available(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	rindex = 0

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)  
		   
		#list available entitlement pools
		productid = ee().get_env(params)["productid"]
		productidME = ee().get_env(params)["productidME"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available multi-entitlement pool with a stacking id
		length = len(availpoollist)
		for index in range(0, length):
			if availpoollist[index]["SKU"] == productidME:
				rindex = index
				break
		poolid = availpoollist[rindex]["PoolId"]
		quantity = int(availpoollist[rindex]["Quantity"]) + 1

		#subscribe to the pool with 0 quantities
		#quantity = int(ee().get_env(params)["quantity"]) + 1
		cmd="subscription-manager subscribe --pool=%s --quantity=%s"%(poolid, quantity)
		(ret,output)=eu().runcmd(session,cmd,"subscribe")

		#if "No free entitlements are available for the pool with id" in output:
		out1 = "No entitlements are available from the pool with id"
		out2 = "No subscriptions are available from the pool with id"
		if (out1 in output) or (out2) in output:
			logging.info("It's successful to check error message of stacking with more quantity than available.")
		else:
			raise error.TestFail("Test Failed - The information shown after stacking with more quantity than available.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do stack with more quantity than available:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

