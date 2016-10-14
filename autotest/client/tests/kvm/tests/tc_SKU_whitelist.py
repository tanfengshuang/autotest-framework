import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.skutest.whitelist import *

def run_tc_SKU_whitelist(test, params, env):
	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	username='stage_whitelist_0308'
	password='redhat'
	sku_list = ['MCT2731','MCT1744','MCT2746','MCT0422','MCT1650']
	orgname = "6763596"

	try:
		sku_whitelist_test(session, params, username, password, sku_list, orgname)
		#verify_subscription_pools(session, username, password, 'MCT1111')
		#verify_subscription_pools_is_null(session, username, password)
		#refresh_pools(orgname)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku whitelist testing:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
