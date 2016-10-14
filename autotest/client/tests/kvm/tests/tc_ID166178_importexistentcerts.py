import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID166178_importexistentcerts(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)



	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
	 	#[A] - prepare test env
		#list available entitlement pools
		
		#auto-subscribe a subscription
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#check whether entitlement certificates generated and productid in them or not
		productid = ee().get_env(params)["productid"]
		eu().sub_checkentitlementcerts(session, productid)

		#[B] - run the test
		#generate entitlement certificate to import and remove entitlement certificate
		generate_and_remove_entcert(session)

		#import existing entitlement cert
		import_exist_entcert(session)

		#check whether entitlement certificates generated and productid in them or not
		eu().sub_checkentitlementcerts(session, productid)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do import existing entitlement certificate:"+str(e))
	finally:
		eu().sub_unregister(session)
		eu().runcmd(session,'rm -f /tmp/test.pem', "remove test cert")
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def generate_and_remove_entcert(session):
	cmd="cat /etc/pki/entitlement/* > /tmp/test.pem"
	(ret,output)=eu().runcmd(session,cmd,"generate entitlement cert")	
	if ret == 0:
		eu().runcmd(session,'rm -f /etc/pki/entitlement/*', "remove entitlement cert") 	
	else :
		raise error.TestFail("Test Failed - error happened when generate entitlement certs")

def import_exist_entcert(session):
	cmd=" subscription-manager import --certificate=/tmp/test.pem"
	(ret,output)=eu().runcmd(session,cmd,"import exist entitlement certificate") 

	if ret == 0 and "Successfully imported certificate" in output:
		logging.info("Import existing entitlement certificate successfully.")
	else:
		raise error.Testfail("Test Failed - Failed to import entitlement certificate.")

