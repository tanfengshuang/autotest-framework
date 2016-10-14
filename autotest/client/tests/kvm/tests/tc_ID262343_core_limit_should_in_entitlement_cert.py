import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262343_core_limit_should_in_entitlement_cert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		#register and autosubscribe
		
		cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
		(ret,output)=eu().runcmd(session,cmd,"register and autosubscribe")
		if ret == 0 and 'The system has been registered with'in output and autosubprod in output and 'Status:Subscribed' in output:
			logging.info("It's successful to register and autosubscribe")
		else:
			raise error.TestFail("Test Failed - Failed to register and autosubscribe")
			
		# get the entitlement cert name
		
		cmd ="ls /etc/pki/entitlement | grep -v 'key'"
		(ret,output)=eu().runcmd(session,cmd,"get entitlement cert name")
		if ret == 0 and '.pem'in output:
			certname=output.strip()
			logging.info("It's successful to get the entitlement cert name %s"%certname)
		else:
			raise error.TestFail("Test Failed - Failed to get the entitlement cert name")
			
		# check core limit in entitlement cert
		
		#cmd = "cd /etc/pki/entitlement;rct cat-cert %s | grep 'Core Limit'"%certname
		cmd = "rct cat-cert /etc/pki/entitlement/%s | grep 'Core Limit'"%certname
		(ret,output)=eu().runcmd(session,cmd,"check core limit")
		if ret == 0 and 'Core Limit:'in output:
			logging.info("It's successful to check core limit in entitlement cert")
		else:
			raise error.TestFail("Test Failed - Failed to check core limit in entitlement cert")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe with --force:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

