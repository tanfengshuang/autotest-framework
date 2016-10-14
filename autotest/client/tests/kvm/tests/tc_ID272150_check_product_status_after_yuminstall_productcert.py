import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests import pexpect

def run_tc_ID272150_check_product_status_after_yuminstall_productcert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#register to server
	#username=ee().get_env(params)["username"]
	#password = ee().get_env(params)["password"]
	username = "stage_test_13"
	password = "redhat"
	eu().sub_register(session,username,password)

	try:
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		cmd="subscription-manager list --installed"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")
		if ret == 0 and "Installed Product Status" in output:
			logging.info("It's successful to list the installed product on the server.")
		else:
			raise error.TestFail("Test Failed - Failed to list the installed product on the server.")
		
		cmd="yum install -q compat-locales-sap -y"
		(ret,output)=eu().runcmd(session,cmd,"install a product cert")
		
		cmd="subscription-manager list --installed"
		(ret,output)=eu().runcmd(session,cmd,"list installed product")
		if ret == 0 and "Not Subscribed" not in output:
			logging.info("It's successful to list the installed product on the server.")
		else:
			raise error.TestFail("Test Failed - Failed to list the installed product on the server.")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do auto-subscribe:"+str(e))
	finally:
		cmd = "yum erase compat-locales-sap -y"
		(ret,output)=eu().runcmd(session,cmd,"remove the added package")
		eu().sub_unregister(session)
		cmd = "rm -f /etc/pki/product/146.pem"
		(ret,output)=eu().runcmd(session,cmd,"remove the added product pki cert")
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

