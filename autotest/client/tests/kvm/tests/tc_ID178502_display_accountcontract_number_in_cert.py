"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID178502_display_accountcontract_number_in_cert(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]

		#register and auto subscribe
		eu().sub_register(session, username, password)
		eu().sub_autosubscribe(session, autosubprod)

		#record the entitlement cert
		cmd="ls /etc/pki/entitlement/*.pem | grep -v key.pem"
		(ret,certname0)=eu().runcmd(session,cmd,"get the entitlement cert name")
		if (ret==0) and (certname0 != None):
			logging.info("It's successful to get the entitlement cert name")
			certname=certname0.strip('\n')
		else:
			raise error.TestFail("Test Failed - Failed to get the entitlement cert name")

		#list consumed subscription, record the account number, and display the account number in entitlement cert
		display_number(session,certname,"Account")

		#list consumed subscription, record the contract number, and display the contract number in entitlement cert
		display_number(session,certname,"Contract")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when display the contract/account number in entitlement cert"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def display_number(session,certname,numbername):
	#list consumed subscription, record the account number
	cmd="subscription-manager list --consumed | grep %s"%numbername
	(ret,output)=eu().runcmd(session,cmd,"list consumed subscription and record %s"%numbername)
	number = output.split(':')[1]
	if ret == 0 and number!="":
		logging.info("It's successful to list consumed subscription and record %s."%numbername)
	else:
		raise error.TestFail("Test Failed - It's failed to list consumed subscription and record %s."%numbername)

	#display the number in entitlement cert
	cmd="rct cat-cert %s | grep %s"%(certname,number)
	(ret,output1)=eu().runcmd(session,cmd,"check and display the %s number in %s"%(numbername,certname))
	if ret ==0:
		if numbername in output1:
                        logging.info("It's successful to display %s number in %s."%(numbername,certname))
                else:
                        logging.info("%s is not set in %s"%(numbername, certname))
	else:
		raise error.TestFail("Test Failed - It's failed to display %s number in %s."%(numbername,certname))
