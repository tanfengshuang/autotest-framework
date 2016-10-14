import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID324774_No_dmidecode_in_facts_list_on_ppc64(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		cmd = "subscription-manager facts --list | grep dmidecode"
		(ret,output) = eu().runcmd(session,cmd,"check No dmidecode in facts list on ppc64")
		if ret != 0 and 'python-simplejson' not in output:
			logging.info("It's successful to check No dmidecode in facts list on ppc64")
		else:
			raise error.TestFail("Test Failed - Failed to check No dmidecode in facts list on ppc64.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check No dmidecode in facts list on ppc64:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
