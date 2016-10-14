import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID311042_repo_support_proxysetting(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	
	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
		
		#auto subscribe to a pool
		autosubprod=ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session,autosubprod)

		cmd="subscription-manager repos --list --proxy=squid.redhat.com:3128"
		(ret,output)=eu().runcmd(session,cmd,"check the repo is list")
                
		if ret == 0 and output:
			logging.info("It's successful to check the repo proxy option is available." )
		else:
			raise error.TestFail("Test Failed - Fail to check the repo proxy option is available.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do enable a repo:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

