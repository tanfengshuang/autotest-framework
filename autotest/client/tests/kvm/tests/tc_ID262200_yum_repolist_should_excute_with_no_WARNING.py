import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262200_yum_repolist_should_excute_with_no_WARNING(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	autosubprod = ee().get_env(params)["autosubprod"]
	try:
		# register and autosubscribe
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		
		cmd = "subscription-manager register --username=%s --password=%s --autosubscribe"%(username, password)
		(ret,output)=eu().runcmd(session,cmd,"register and autosubscribe")
		if ret == 0 and "The system has been registered with ID" in output and "Status:Subscribed" in output and autosubprod in output:
			logging.info("It's successful to autosubscribe")
		else:
			raise error.TestFail("Test Failed - Failed to autosubscribe")
		# yum repolist
		cmd = "yum repolist | grep WARNING"
		(ret,output)=eu().runcmd(session,cmd,"yum repolist")
		if ret!=0:
			logging.info("It's successful to yum repolist without warning")
		else:
			raise error.TestFail("Test Failed - Failed to yum repolist without warning")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to yum_repolist_should_excute_with_no_WARNING:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
