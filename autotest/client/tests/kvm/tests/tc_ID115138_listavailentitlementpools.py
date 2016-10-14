import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115138_listavailentitlementpools(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:   
		#list available entitlement pools
		productid=ee().get_env(params)["productid"]
		availpoollist = eu().sub_listavailpools(session,productid)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list available entitlement pools:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

