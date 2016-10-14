import sys, os, subprocess, commands, random, time
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID268182_autoheal_on_core_product(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	#prepare product cert
	cmd="rm -f /etc/pki/product/*.pem"
	(ret,output)=eu().runcmd(session,cmd,"remove current product cert")

	cmd="cp -rf \"/etc/pki/product/tmp/806.pem\" \"/etc/pki/product/\""
	(ret,output)=eu().runcmd(session,cmd,"copying specific product cert to cert dir")
	oldtime = ""
	rindex = 0

	try:   
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]	
		eu().sub_register(session,username,password)
		
		cmd = "subscription-manager attach --auto"
		(ret, output) = eu().runcmd(session, cmd, "auto attach")
		
		if ret == 0 and "Subscribed" in output and "Partially" not in output:
			logging.info("It's successful to auto attach for core subscription")
		else:
			raise error.TestFail("Test Failed - Failed to auto attach for core subscription")
		
		checkinstalled(session, "Subscribed")
		
		cmd = "subscription-manager remove --all"
		(ret, output) = eu().runcmd(session, cmd, "remove")
		
		eu().restart_rhsmcertd(session)
		
		time.sleep(180)
		
		checkinstalled(session, "Subscribed")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do heal for expiration:"+str(e))
	finally:
		cmd="rm -f /etc/pki/product/*.pem"
		(ret, output) = eu().runcmd(session,cmd,"remove current product cert")
		cmd="cp -rf \"/etc/pki/product/tmp/%s.pem\" \"/etc/pki/product/\""%ee.pidcc
		(ret,output)=eu().runcmd(session,cmd,"copying default product cert to cert dir")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
			
def checkinstalled(session, status):
	cmd = "subscription-manager list --installed"
	(ret, output) = eu().runcmd(session, cmd, "list system installed products")
	if ret ==0:
		if "Partially" in status and status in output:
			logging.info("It successful to check the system installed products")
		elif status in output and "Partially" not in output:
			logging.info("It successful to check the system installed products")
		else:
			raise error.TestFail("Test Failed - Failed to check the system installed products")
	else:
		raise error.TestFail("Test Failed - Failed to check the system installed products")
