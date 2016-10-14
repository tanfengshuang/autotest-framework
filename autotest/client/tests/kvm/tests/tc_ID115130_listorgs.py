import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115130_listorgs(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		#list orgs of a consumer.
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		cmd="subscription-manager orgs --username=%s --password=%s"%(username,password)
		(ret,output)=eu().runcmd(session,cmd,"list orgs")

		if ret == 0 and "OrgName" in output and "OrgKey" in output:
			logging.info("It's successful to list orgs info.")
                elif ret == 0 and "Name" in output and "Key" in output:
                        logging.info("It's successful to list orgs info.")
		else:
			raise error.TestFail("Test Failed - Failed to list orgs info.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list orgs info:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
