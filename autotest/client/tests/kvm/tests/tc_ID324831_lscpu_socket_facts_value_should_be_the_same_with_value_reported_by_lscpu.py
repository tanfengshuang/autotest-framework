import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID324831_lscpu_socket_facts_value_should_be_the_same_with_value_reported_by_lscpu(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	guest_name=params['guest_name']
	try:
		if "5" in guest_name:
			logging.info("There is no need to test this case on rhel5")
		else:
			# get lscpu.sockets fact value
			cmd = 'subscription-manager facts --list | grep "lscpu.socket(s)"'
			(ret,output) = eu().runcmd(session,cmd,"list lscpu.sockets facts on ppc64")
			if ret == 0:
				lscpu_sockets_fact1 = output.split("\n")[0].split(":")[1].strip()
				logging.info("It's successful to get lscpu.sockets fact value")
			else:
				raise error.TestFail("Test Failed - Failed to get lscpu.sockets fact value.")
		
			# get lscpu sockets value
			cmd = 'lscpu | grep Socket'
			(ret,output) = eu().runcmd(session,cmd,"get lscpu sockets value on ppc64")
			if ret == 0:
				lscpu_sockets_value = output.split(':')[1].strip()
				logging.info("It's successful to get lscpu sockets value")
			else:
				raise error.TestFail("Test Failed - Failed to get lscpu sockets value.")
			
			# compare the values
			if lscpu_sockets_fact1 == lscpu_sockets_value:
				logging.info("It's successful to check cpu_socket(s) facts value should be the same with value reported by lscpu on ppc64")
			else:
				raise error.TestFail("Test Failed - Failed to check cpu_socket(s) facts value should be the same with value reported by lscpu on ppc64.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check cpu_socket(s) facts value should be the same with value reported by lscpu on ppc64:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)



