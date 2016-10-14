import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189618_collapsed_provided_products(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" %__name__)

	try:
		#get username and password
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
	
		#get env variables
		productid = ee().get_env(params)["productid"]
		autosubprod = ee().get_env(params)["autosubprod"]
	
		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)	

		cmd="subscription-manager list --consumed"
		(ret, output)=eu().runcmd(session, cmd, "list the consumed products")

		if ret == 0:
			consumed_list = eu().parse_listconsumed_output(output)
			
			if len(consumed_list) == 1 and consumed_list[0]["Provides"] != "":
				logging.info("It's successful to check collapsed provided products.")
			else:
				raise error.TestFail("Test Failed - Failed to check collapsed provided products.")
		else:
			raise error.TestFail("Test Failed - Failed to check collapsed provided products.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check collapsed provided products:"+str(e))

	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

