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

def run_tc_ID180386_unsubscribe_using_cert_serialnumber(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]

		#register and auto subscribe
		eu().sub_register(session, username, password)
		eu().sub_autosubscribe(session, autosubprod)

		#list consumed
		cmd_list="subscription-manager list --consumed | grep Serial"
		(ret,output)=eu().runcmd(session,cmd_list,"list consumed subscription and record serial number")
		if ret == 0 and output!=None:
			serialnumber=output.strip().split(':')[1]
			logging.info("It's successful to list consumed subscription and record serial number.")
		else:
			raise error.TestFail("Test Failed - It's failed to list consumed subscription and record serial number.")
		
		#unsubscribe the consumed subscription via the serial number
		cmd_unsub="subscription-manager unsubscribe --serial=%s"%serialnumber
		(ret,output)=eu().runcmd(session,cmd_unsub,"unsubscribe the consumed subscription via the serial number")
		if ret == 0 and output!=None:
			logging.info("It's successful to run unsubscribe via the serial number.")
		else:
			raise error.TestFail("Test Failed - It's failed to unsubscribe the consumed subscription via the serial number.")

		#list consumed after unsubscribe the consumed subscription via the serial number
		cmd_list="subscription-manager list --consumed"
		(ret,output)=eu().runcmd(session,cmd_list,"list consumed subscription")
		if ret == 0 and "No consumed subscription pools to list" in output:
			logging.info("It's successful to list consumed subscription")
		else:
			raise error.TestFail("Test Failed - It's failed to list the consumed subscription.")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when ubscribe the consumed subscription via the serial number:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
