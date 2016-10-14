import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190651_check_certificate_version_from_facts(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#check the certificate version from facts
		cmd="subscription-manager facts | grep system.certificate_version"
		(ret,output)=eu().runcmd(session,cmd,"check the certificate version from facts")

		if ret == 0 and "system.certificate_version: 3" in output:      
			logging.info("It's successful to check the certificate version from facts.")    
		else:
			raise error.TestFail("Test Failed - Failed to check the certificate version from facts.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the certificate version from facts:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
