import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests import pexpect

def run_tc_ID261909_check_addedproduct_status(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		consumeid = eu().sub_get_consumerid(session)
		hostname = params.get("hostname")
		if "rhn" in hostname:
			cmd = "curl -k -u %s:%s --request GET https://%s:443/subscription/consumers/%s/compliance | python -m simplejson/tool | grep status" \
			%(username, password, hostname, consumeid)
			isrhn = 1
		else:
			cmd = "curl -k -u %s:%s --request GET https://%s:8443/candlepin/consumers/%s/compliance | python -m simplejson/tool | grep status" \
			%(username, password, hostname, consumeid)
			isrhn = 0
			
		(ret,output)=eu().runcmd(session,cmd,"see the status of product")
		if ret == 0 and "valid" in output:
			logging.info("It's successful to check the installed product on the server.")
		else:
			raise error.TestFail("Test Failed - Failed to check the installed product on the server.")

		productpkilocal = "/etc/pki/product/"
		productpkiserver = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/productpki/146.pem"
		eu().copyfiles(vm, productpkiserver, productpkilocal, cmddesc="copying productpem to the dir: %s" %productpkilocal)
		
		cmd="subscription-manager list --installed"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")
		if ret == 0 and "Installed Product Status" in output:
			logging.info("It's successful to list the installed product on the server.")
		else:
			raise error.TestFail("Test Failed - Failed to list the installed product on the server.")
		
		if isrhn:
			cmd = "curl -k -u %s:%s --request GET https://%s:443/subscription/consumers/%s/compliance | python -m simplejson/tool | grep status" \
			%(username, password, hostname, consumeid)
		else:
			cmd = "curl -k -u %s:%s --request GET https://%s:8443/candlepin/consumers/%s/compliance | python -m simplejson/tool | grep status" \
			%(username, password, hostname, consumeid)
			
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

