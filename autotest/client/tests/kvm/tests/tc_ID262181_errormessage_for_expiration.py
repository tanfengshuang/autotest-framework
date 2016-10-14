import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262181_errormessage_for_expiration(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)

		#change current time to make identity cert expire 
		oldtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		newtime = "20550101" 
		cmd = "date -s '%s'" %(newtime)
		(ret,output)=eu().runcmd(session,cmd,"set system time to be the expiration time")


		cmd="subscription-manager identity"
		(ret,output)=eu().runcmd(session,cmd,"list system's identity")
		
		errormessage = "Your identity certificate has expired"
		if ret != 0 and errormessage in output:
			logging.info("It's successful to show friendly error message when identity cert expired")
		else:
			raise error.TestFail("Test Failed - Failed to show friendly error message when identity cert expired")
	
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do to show friendly error message when identity cert expired:"+str(e))
	finally:
		if oldtime != "":
			cmd="date -s '%s'"%(oldtime)
			(ret,output)=eu().runcmd(session,cmd,"set system time to be the normal time")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

