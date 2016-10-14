import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190817_check_unsubscribeall_output(test, params, env):
	
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" %__name__)
	
	try:
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		#prepare a env auto subsribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		#run cmd unsubscribe --all
		cmd = "subscription-manager unsubscribe --all"
		(ret, output) = eu().runcmd(session, cmd, "run cmd unsubscribe --all")
		expectoutput = "This machine has been unsubscribed from 1 subscriptions"
		expectoutputnew = "subscription removed from this system."
		expectoutput5101 = "subscription removed at the server."
		expectoutput5102 = "local certificate has been deleted."
		
		if 0 == ret and ((expectoutput5101 in output and expectoutput5102 in output) \
		  or (expectoutput in output or expectoutputnew in output)):
			firstresult = True
			print "True\n"
		else:
			firstresult = False
			print "False\n"
			
		#unsubscribe before subscribe
		cmd = "subscription-manager unsubscribe --all"
		(ret, output) = eu().runcmd(session, cmd, "run cmd unsubscribe --all again")
		
		expectoutput = "This machine has been unsubscribed from 0 subscriptions"
		expectoutputnew = "0 subscriptions removed from this system."
		expectoutput510 = "subscriptions removed at the server."
		
		if 0 == ret and (expectoutput510 in output or expectoutput in output or expectoutputnew in output):
			secondresult = True
			print "True\n"
		else:
			secondresult = False
			print "False\n"
		
		if firstresult and secondresult:
			logging.info("It is successful to run cmd subscription-manager unsubscribe --all and check the output!")
		else:
			raise error.TestFail("Test Faild - Failed to run cmd subscription-manager unsubscribe --all and check the output!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the default output of release cmd:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("========== End of Running Test Case: %s ==========" %__name__)
