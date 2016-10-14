import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115193_check_stackable_ability_of_product(test, params, env):

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
		productidstack = ee().get_env(params)["productidstack"]
		availpoollist = eu().sub_listallavailpools(session,productid)

		#get an available entitlement pool with a stacking id
		length = len(availpoollist)
		for index in range(0, length):
			if availpoollist[index]["SKU"] == productidstack:
				rindex=index
				break
		poolid=availpoollist[rindex]["PoolId"]

		#subscribe to the pool
		eu().sub_subscribetopool(session,poolid)

		#check whether entitlement certificates generated and productid in them or not
		eu().sub_checkentitlementcerts(session,productid)

		#check whether the product is stackable
		cmd="for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i; done | grep -A1 '1.3.6.1.4.1.2312.9.4.17'"
		(ret,output)=eu().runcmd(session,cmd,"check product's stackable ability")

		if ret == 0 and "1.3.6.1.4.1.2312.9.4.17" in output:
			logging.info("It's successful to check the product's stackable ability.")
		else:
			raise error.TestFail("Test Failed - Failed to check the product's stackable ability.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do check product's stackable ability::"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

