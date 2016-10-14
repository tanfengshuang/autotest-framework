import sys, os, subprocess, commands, random, time, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID143330_configure_to_remove_redhatrepo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#[A] - prepare test env
        #register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		#auto subscribe to a pool
		autosubprod=ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)

		#[B] - run the test
		#list available repos
		cmd="subscription-manager repos --list"
		(ret,output)=eu().runcmd(session,cmd,"list available repos")
                
		productrepo=ee().get_env(params)["productrepo"]
		betarepo=ee().get_env(params)["betarepo"]
		if ret == 0 and productrepo in output and betarepo in output:
			logging.info("It's successful to list available repos.")
		else:
			raise error.TestFail("Test Failed - Failed to list available repos.")

		#check redhat.repo existed in repo dir
		is_redhatrepo_exist(session, True)

		#configure to remove redhat.repo
		configure_to_handle_redhatrepo(session, "off")
 		
		#do a list to make disable work at once
		cmd="subscription-manager repos --list"
		(ret,output)=eu().runcmd(session,cmd,"list available repos")
		if ret == 0 and "Repositories disabled by configuration." in output:
			logging.info("It's successful to verify no repo listed after configure to remove redhat.repo")
		else:
			raise error.TestFail("Test Failed - Failed to disable available repos")
		
		#check redhat.repo file be deleted
		is_redhatrepo_exist(session, False)
				
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list available repos:"+str(e))
	finally:
		eu().sub_unregister(session)
		configure_to_handle_redhatrepo(session, "on")
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


def configure_to_handle_redhatrepo(session, switch):
	#configure to remove/add redhat.repo
	if switch == "off":
		cmd="subscription-manager config --rhsm.manage_repos=0"
	else:
		cmd="subscription-manager config --rhsm.manage_repos=1"
	
	(ret,output)=eu().runcmd(session,cmd,"configure manage_repos")
	if ret == 0:
		logging.info("It's successful to configure option rhsm.manage_repos to %s." %switch)
	else:
		raise error.TestFail("Test Failed - Failed to configure option rhsm.manage_repos to %s." %switch)

	#restart rhsmcertd service and wait for one minute
	cmd="service rhsmcertd restart"
	(ret,output)=eu().runcmd(session,cmd,"restart rhsmcertd service")

	if output.count("OK") == 2 :
		logging.info("It's successful to restart rhsmcertd service.")
		logging.info("Waiting 240 seconds for rhsmcertd service to take effect...")
		time.sleep(240)
	else:
		raise error.TestFail("Test Failed - Failed to restart rhsmcertd service.")

def is_redhatrepo_exist(session, expectbool):
	#check redhat.repo file exist or not
	cmd="ls /etc/yum.repos.d/"
	(ret,output)=eu().runcmd(session,cmd,"check redhat.repo exist")

	if not expectbool :
		existed=output.count("bak")==output.count("redhat.repo")
	else:
		existed= not (output.count("bak")==output.count("redhat.repo"))
		
	if ret == 0 and existed:
		logging.info("It's successful to check redhat.repo file exist: %s." %expectbool)
	else:
		raise error.TestFail("Test Failed - Failed to delete redhat.repo file.")
