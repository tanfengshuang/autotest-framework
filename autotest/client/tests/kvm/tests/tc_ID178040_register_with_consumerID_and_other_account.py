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

def run_tc_ID178040_register_with_consumerID_and_other_account(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		#samip=ee().get_env(params)["samhostip"]
		samip=params.get("samhostip")
		#register first time
		eu().sub_register(session,username,password)
		#record consumerid
		consumerid=eu().sub_get_consumerid(session)
		#autosubscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#create a new account from SAM server
		cmd_create="headpin -u admin -p admin user create --username=test456 --password=123456 --email=test456@redhat.com;headpin -u admin -p admin user assign_role --username=test456 --role=Administrator"
		(ret, output) = eu().runcmd_remote(samip, "root", "redhat", cmd_create)
		if ret==0 and "Successfully created user" in output:
			logging.info("It's successful to create a new account in SAM server:username=test456 password=123456")
		else:
			raise error.TestFail("TestFailed - Failed to create a new account!")

		#clean client data
		cmd_clean="subscription-manager clean"
		(ret,output)=eu().runcmd(session,cmd_clean,"clean client data")
		if (ret==0) and ("All local data removed" in output):
			logging.info("It's successful to run subscription-manager clean")
		else:
			raise error.TestFail("Test Failed - error happened when run subscription-manager clean")

		#register with existing consumerid use new created account
		cmd_register="subscription-manager register --username=test456 --password=123456 --consumerid=%s"%consumerid
		(ret,output)=eu().runcmd(session,cmd_register,"register use different username and password")
		#if (ret!=0) and ("User test456 is not allowed to access api/systems/show" in output):
		#	logging.info("It's successful to verify that registeration with existing consumerid using different account should not succeed")
		if (ret!=0) and ('Invalid username or password' in output):
			logging.info("It's successful to verify that registeration with existing consumerid using different account should not succeed")
		else:
			raise error.TestFail("Test Failed - error happened when register with existing consumerid using different account")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when register with existing consumerid using different account:"+str(e))
	finally:
		#delete the new account from SAM server
		cmd_delete="headpin -u admin -p admin user delete --username=test456"
		(ret, output) = eu().runcmd_remote(samip, "root", "redhat", cmd_delete)
		if ret==0 and "Successfully deleted user [ test456 ]" in output:
			logging.info("It's successful to delete the username and password in SAM")
		else:
			raise error.TestFail("Test Failed - error happened when delete the username and password in SAM")
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
