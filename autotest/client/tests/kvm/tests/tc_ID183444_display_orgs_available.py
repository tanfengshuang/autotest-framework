'''
@author           :soliu@redhat.com
@date             :2013-03-12
'''

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID183444_display_orgs_available(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		samhostip=params.get("samhostip")

		#register a system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session, username, password, "")
		
		#check if the org ACME_Corporation2 exist on samserver
		orgname2='ACME_Corporation2'
		is_multi_orgs=eu().sam_remote_is_org_exist(samhostip, 'root', 'redhat',orgname2)

		#create another org if no multi-orgs env
		if not is_multi_orgs:
			eu().sam_remote_create_org(samhostip, 'root', 'redhat', orgname2)
	
		#check the orgs in client
		cmd_display_orgs="subscription-manager orgs --username=%s --password=%s" %(username, password)
		#step1:display the orgs available for a user
		(ret, output)=eu().runcmd(session, cmd_display_orgs, "display orgs")
		if ret == 0:
			if "Name:ACME_Corporation" and "Name:ACME_Corporation2"in output:
				logging.info("It is successful to display the multi-orgs avaiable for a user!")
			else:
				raise error.TestFail("Failed to display the multi-orgs available for a user!")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when display the multi-orgs available for a user"+str(e))
	finally:
                #delete the org ACME_Corporation2 on samserver
                eu().sam_remote_delete_org(samhostip, 'root', 'redhat', orgname2)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
