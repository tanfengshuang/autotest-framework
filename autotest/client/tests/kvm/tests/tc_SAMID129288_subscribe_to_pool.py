import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129288_subscribe_to_pool(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register a system
		eu().sam_create_system(session, ee.systemname1, ee.default_org, ee.default_env)

		#list available subscriptions
		availpoollist = eu().sam_listavailpools(session, ee.systemname1, ee.default_org)

		#get an available entitlement pool to subscribe with random.sample
		availpool = random.sample(availpoollist, 1)[0]
		poolid = availpool["PoolId"]

		#subscribe to the pool
		eu().sam_subscribetopool(session, ee.systemname1, ee.default_org, poolid)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when subscribe to a pool:"+str(e))
	finally:
		eu().sam_unregister_system(session, ee.systemname1, ee.default_org)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
