import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests import pexpect

def run_tc_ID262340_yum_repo_have_vars(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#register to server
	username=ee().get_env(params)["username"]
	password = ee().get_env(params)["password"]

	eu().sub_register(session,username,password)

	try:
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		cmd="yum repolist"
		(ret,output)=eu().runcmd(session,cmd,"refresh repo file")
		
		cmd="cat /etc/yum.repos.d/redhat.repo | grep ui_repoid_vars"
		(ret,output)=eu().runcmd(session,cmd,"find ui_repoid_vars")
		if ret == 0:
			logging.info("It's successful to check the ui_repoid_vars in the repofile .")
		else:
			raise error.TestFail("Test Failed - Failed to check the ui_repoid_vars in the repofile.")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto-subscribe:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

