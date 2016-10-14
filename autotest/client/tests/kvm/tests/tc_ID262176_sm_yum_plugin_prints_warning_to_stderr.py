import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262176_sm_yum_plugin_prints_warning_to_stderr(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		#Send the output to stdout.log and stderr.log
		cmd="yum repolist > stdout.log 2> stderr.log"
		(ret,output)=eu().runcmd(session,cmd,"print warning")
		if ret == 0:
			logging.info("It's successful to redirect warning to stderr")
		else:
			raise error.TestFail("Test Failed - Failed to redirect warning to stderr")
		
		#check stdout
		cmd="cat stdout.log"
		(ret,output)=eu().runcmd(session,cmd,"print stdout")
		if ret==0 and "Loaded plugins:" in output and "repolist:" in output:
			logging.info("It's successful to print stdout")
		else:
			raise error.TestFail("Test Failed - failed to print stdout")
		
		#check stderr
		cmd="cat stderr.log"
		(ret,output)=eu().runcmd(session,cmd,"print stderr")
		if ret==0 and "This system is not registered to Red Hat Subscription Management. You can use subscription-manager to register." in output:
			logging.info("It's successful to print stderr")
		else:
			raise error.TestFail("Test Failed - failed to print stderr")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to verify sm_yum_plugin_prints_warning_to_stderr:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
