import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID147219_stacking_with_zero_quantity(test, params, env):

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
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available multi-entitlement pool with a stacking id
		length = len(availpoollist)
		for index in range(0, length):
			if availpoollist[index]["SKU"] == productid:
				rindex=index
				break
		poolid=availpoollist[rindex]["PoolId"]

		#subscribe to the pool with 0 quantities
		cmd="subscription-manager subscribe --pool=%s --quantity=0"%(poolid)
		(ret,output)=eu().runcmd(session,cmd,"subscribe")

		if "Error: Quantity must be a positive integer" in output:
			logging.info("It's successful to check error message of stacking with zero quantity.")
		else:
			raise error.TestFail("Test Failed - The information shown after stacking with zero quantity.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do stack with zero quantity:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

