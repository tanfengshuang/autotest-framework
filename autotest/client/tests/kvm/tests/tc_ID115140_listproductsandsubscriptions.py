import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115140_listproductsandsubscriptions(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		#[A] - prepare test env
		#get env variables
		productid = ee().get_env(params)["productid"]
		autosubprod = ee().get_env(params)["autosubprod"]

		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)

		#check whether entitlement certificates generated and productid in them or not
		#eu().sub_checkentitlementcerts(session, productid)      

 		#[B] - run the test
		#list installed products
		installedproductname = ee().get_env(params)["installedproductname"]
		list_installed_products(session,installedproductname)

		#list consumed subscriptions
		installedproductname = ee().get_env(params)["installedproductname"]
		list_consumed_subscriptions(session,installedproductname)

        except Exception, e:
			logging.error(str(e))
			raise error.TestFail("Test Failed - error happened when do list products and subscriptions:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def list_installed_products(session,expectedproductname):
	if "," in expectedproductname:
		productnamelist =  expectedproductname.split(",")
	else:
		productnamelist = [expectedproductname]

	cmd="subscription-manager list --installed"
	(ret,output)=eu().runcmd(session,cmd,"list installed products")
	
	#This line for rhel6.4 new output version
	output_join = " ".join(x.strip() for x in output.split())
	
	if ret == 0:
		for productname in productnamelist:
			if (productname in output or productname in output_join):
				logging.info("It's successful to list installed product %s."%(productname))
				return True        	
			else:
				raise error.TestFail("Test Failed - The product %s is not installed." %(productname))
				return False
	else:
		raise error.TestFail("Test Failed - Failed to list installled products.")
		return False


def list_consumed_subscriptions(session,installedproductname):
	cmd="subscription-manager list --consumed"
	(ret,output)=eu().runcmd(session,cmd,"list consumed subscriptions")

	output_join = " ".join(x.strip() for x in output.split())
	if ret == 0 and ((installedproductname in output) or (installedproductname in output_join)):
		logging.info("It's successful to list all consumed subscriptions.")
		return True
	else:
		raise error.TestFail("Test Failed - Failed to list all consumed subscriptions.")
		return False
