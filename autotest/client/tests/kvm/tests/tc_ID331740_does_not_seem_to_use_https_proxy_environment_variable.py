import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
def run_tc_ID331740_does_not_seem_to_use_https_proxy_environment_variable(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" % __name__)

	try:
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		if username=="admin" and password=="admin":
			logging.info("sam not test proxy")
		else:
			# check the the rhsm conf file for proxy before register with proxy
			check_proxy_rhsm(session)
	
			# register with specified proxy
			cmd = "https_proxy=squid.corp.redhat.com:3128 subscription-manager register --username=%s --password='%s'" %(username, password)
			(ret,output)=eu().runcmd(session,cmd,"register with proxy")
			if ret == 0 and "The system has been registered with ID" in output:
				logging.info("It's successful to register with proxy")
			else:
				raise error.TestFail("Test Failed - Failed to register with proxy.")

			# check the the rhsm conf file for proxy after register with proxy
			check_proxy_rhsm(session)
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check register with a user account without any orgs access via GUI:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("========== End of Running Test Case: %s ==========" % __name__)

def check_proxy_rhsm(session):
	cmd = "cat /etc/rhsm/rhsm.conf | egrep 'proxy_hostname|proxy_port'"
	(ret,output)=eu().runcmd(session,cmd,"check_proxy_rhsm")
	o1=output.split("\n")[0].split("=")[1]
	o2=output.split("\n")[1].split("=")[1]
	if ret == 0 and o1 == '' and o2 == '':
		logging.info("It's successful to check that Environment variable not written into conf file")
	else:
		raise error.TestFail("Test Failed - Failed to check that Environment variable not written into conf file.")
