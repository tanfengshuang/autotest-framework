import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_SAMID129253_delete_exist_activationkey(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#create an activationkey
		eu().sam_create_activationkey(session, ee.keyname1, ee.default_env, ee.default_org)

		#delete an activationkey
		eu().sam_delete_activationkey(session, ee.keyname1, ee.default_org)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do delete an existed activationkey:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
