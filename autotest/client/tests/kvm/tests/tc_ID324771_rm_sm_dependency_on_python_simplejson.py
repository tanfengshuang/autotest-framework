import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time

def run_tc_ID324771_rm_sm_dependency_on_python_simplejson(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	guest_name=params['guest_name']
	try:
		cmd = "rpm --query --requires python-rhsm --verbose | grep 'python-simplejson'"
		(ret,output) = eu().runcmd(session,cmd,"check dependency on python-simplejson")
		if ret != 0 and 'python-simplejson' not in output:
			logging.info("It's successful to check dependency on python-simplejson")
		elif ret == 0 and "5" in guest_name:
			logging.info("RHEL 7 features are being backported for 5.11 but this does not imply package dependencies will be the same.")
		else:
			raise error.TestFail("Test Failed - Failed to check dependency on python-simplejson.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when dependency on python-simplejson:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
