import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID262287_option_description_of_org_clarification(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
 
	try:
		clarifiction_org(session, 'register')
		clarifiction_org(session, 'environments')
		clarifiction_org(session, 'service-level')
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to autosubscribe with --force:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def clarifiction_org(session, str_to_org):
	if str_to_org == 'register':
		cmd = "subscription-manager %s --help | grep ORG -A1"%str_to_org
		(ret,output)=eu().runcmd(session,cmd,"org clarification")
		normal=output_normal(output)
		if ret == 0 and normal == "--org=ORG_KEY register with one of multiple organizations for the user, using organization key":
			logging.info("It's successful to check the org option decription for register")
		else:
			raise error.TestFail("Test Failed - error happened to check the org option decription for register")
			
	elif str_to_org == 'environments':
		cmd = "subscription-manager %s --help | grep ORG -A1"%str_to_org
		(ret,output)=eu().runcmd(session,cmd,"org clarification")
		normal=output_normal(output)
		if ret == 0 and normal=="--org=ORG_KEY specify organization for environment list, using organization key":
			logging.info("It's successful to check the org option decription for environments")
		else:
			raise error.TestFail("Test Failed - error happened to check the org option decription for environments")
			
	elif str_to_org == 'service-level':
		cmd = "subscription-manager %s --help | grep ORG -A1"%str_to_org
		(ret,output)=eu().runcmd(session,cmd,"org clarification")
		normal=output_normal(output)
		if ret == 0 and normal=="--org=ORG_KEY specify an organization when listing available service levels using the organization key":
			logging.info("It's successful to check the org option decription for service-level")
		else:
			raise error.TestFail("Test Failed - error happened to check the org option decription for service-level")
			
	else:
		raise error.TestFailed("Test Failed - error happened to check the org option decription!")
def output_normal(output):
	output=output.strip().split()
	normal=''
	for e in output:
		normal=normal + e + ' '
	normal=normal.strip()
	return normal
