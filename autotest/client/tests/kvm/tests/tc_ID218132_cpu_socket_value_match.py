import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID218132_cpu_socket_value_match(test, params, env):
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		cmd='subscription-manager facts --list | grep "socket(s)"'
		(ret,output)=eu().runcmd(session,cmd,"match socket(s)")
		if ret == 0 and 'cpu.cpu_socket(s): 1' in output:
			if 'lscpu.socket(s): 1' in output:
				logging.info("Test Successful - It's successful checking cpu.cpu_socket(s) value match lscpu.cpu_socket(s) value in subscription-manager facts.") 
			else:
				logging.info("Test skipped - The system facts doesn't have the lscpu.socket(s) option")
		else:
			raise error.TestFail("Test Failed - Failed checking cpu.cpu_socket(s) value match lscpu.cpu_socket(s) value in subscription-manager facts.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when "+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
