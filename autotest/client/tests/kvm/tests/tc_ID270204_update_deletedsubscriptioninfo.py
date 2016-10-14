import sys, os, subprocess, commands, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests import pexpect

def run_tc_ID270204_update_deletedsubscriptioninfo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		poolid = eu().sub_get_poolid(session)
		hostname = params.get("hostname")
		if "rhn" in hostname:
			cmd = "curl --stderr /dev/null --insecure --user %s:%s --request DELETE https://%s:443/subscription/subscriptions/%s" \
			%(username, password, hostname, poolid)
			isrhn = 1
		else:
			cmd = "curl --stderr /dev/null --insecure --user %s:%s --request DELETE https://%s:8443/candlepin/subscriptions/%s" \
			%(username, password, hostname, poolid)
			isrhn = 0
			
		(ret,output)=eu().runcmd(session,cmd,"see the status of product")
		if ret == 0:
			logging.info("It's successful to delete the subscription from server.")
		else:
			raise error.TestFail("Test Failed - Failed to delete the subscription from server.")
		
		cmd="service rhsmcertd restart"
		(ret,output)=eu().runcmd(session,cmd,"restart the rhsmcertd")

		time.sleep(90)
		
		cmd = "subscription-manager list --consumed"
		(ret,output)=eu().runcmd(session,cmd,"see the status of product")
		if ret == 0 and "invalid" in output:
			logging.info("It's successful to check the installed product on the server.")
		else:
			raise error.TestFail("Test Failed - Failed to check the installed product on the server.")
				
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto-subscribe:"+str(e))
	finally:
		eu().sub_unregister(session)
		cmd = "rm -f /etc/pki/product/146.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove the added product pki cert")
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

