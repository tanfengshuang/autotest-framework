'''
author              :soliu@redhat.com
date                :2013-03-12
'''

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID183445_register_with_org(test, params, env):

	session,vm=eu().init_session_vm(params,env)

	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#unregister a system
		eu().sub_unregister(session)
		
		#set up the multi-orgs env
		samhostip=params.get("samhostip")
		orgname2='ACME_Corporation2'
		is_multi_orgs=eu().sam_remote_is_org_exist(samhostip, 'root', 'redhat',orgname2)
		if not is_multi_orgs:
                        eu().sam_remote_create_org(samhostip, 'root', 'redhat', orgname2)
		
		#register with specified an org
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		cmd_register_with_orgs="subscription-manager register --org=ACME_Corporation --username=%s --password=%s" %(username, password)
		#step1:display the orgs available for a user
		(ret, output)=eu().runcmd(session, cmd_register_with_orgs, "register with org option")
		if ret == 0:
			if "The system has been registered with ID" in output:
				logging.info("It is successful to register with org option!")
			else:
				raise error.TestFail("Failed to register with org option!")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when register with org option"+str(e))
	finally:
                #delete one created org in order to avoid impacting other case
		eu().sam_remote_delete_org(samhostip, 'root','redhat', orgname2)
		eu().sub_unregister(session)
                logging.info("=========== End of Running Test Case: %s ==========="%__name__)
