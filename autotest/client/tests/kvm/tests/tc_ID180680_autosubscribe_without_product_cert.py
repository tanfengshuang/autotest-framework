"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID180680_autosubscribe_without_product_cert(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#Move the product cert to other dir
		cmd="mv /etc/pki/product/*  /etc/pki/"
		(ret, output) = eu().runcmd(session, cmd, "Move the product cert to other dir")    
		
		if ret==0:
			logging.info(" It's successful to move the product cert.")
		else:
			raise error.TestFail("Test Failed - Failed to move the product cert to other dir.")
			
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#Check auto subscribe result
		autosubprod = ee().get_env(params)["autosubprod"]
		check_autosub_result(session, autosubprod)

		#Check the entitlement cert
		cmd="ll /etc/pki/entitlement"
		(ret, output) = eu().runcmd(session, cmd, "Check the entitlement cert")

		if (ret == 0) and ("total 0" in output):
			logging.info("It's successful to Check the entitlement cert--no file")
		else:
			raise error.TestFail("Test Failed - Failed to Check the entitlement cert--has file")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when to auto With no product certificates installed"+str(e))

	finally:
		move_back_cert(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


def check_autosub_result(session, autosubprod):
	cmd="subscription-manager subscribe --auto"
	(ret, output)=eu().runcmd(session, cmd, "check auto-subscribe result")
	if ret != 0:
		if "No Installed products on system. No need to attach subscriptions." in output:
			logging.info("It's successful to check no need to update subscription for RHEL5 system.")
		elif ("Product Name:" not in output) and (autosubprod not in output):
			logging.info("It's successful to check no need to update subscription for RHEL6 system.")
	else:
		raise error.TestFail("Test Failed - check no need to update subscription.")
		
def move_back_cert(session):
	#Move the product cert back to /etc/pki/product
	cmd="mv /etc/pki/*.pem  /etc/pki/product/"
	(ret, output) = eu().runcmd(session, cmd, "Move the product cert back to the right dir")    

	if ret==0:
		logging.info(" It's successful to move the product cert back.")
	else:
		raise error.TestFail("Test Failed - Failed to move the product cert back.")

