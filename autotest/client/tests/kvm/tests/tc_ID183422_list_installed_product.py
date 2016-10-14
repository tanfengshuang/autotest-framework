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

def run_tc_ID183422_list_installed_product(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#auto subscribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#list installed products
		installedproductname = ee().get_env(params)["installedproductname"]
		cmd="subscription-manager list --installed"
		(ret,output)=eu().runcmd(session,cmd,"list installed products")

		if ret == 0 and installedproductname in output:
			logging.info("It's successful to list installed product %s."%(installedproductname))
			return True        	
		else:
			raise error.TestFail("Test Failed - The product %s is not installed." %(installedproductname))
			return False

	except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when do list installed products:"+str(e))

	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)



