import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
import datetime
import time
def run_tc_ID327120_consumer_folder_moved_to_consumer_old_after_deleting_the_consumer(test, params, env):
	
	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	prefix=ee().get_env(params)["prefix"]
	samhost=params.get("samhostname")

	try:
		# remove the consumer related files
		cmd = "rm -rf /etc/pki/consumer*"
		(ret,output) = eu().runcmd(session,cmd,"remove the consumer related files before testing")
		if ret == 0:
			logging.info("It's successful to remove the consumer related files before testing")
		else:
			raise error.TestFail("Test Failed - Failed to remove the consumer related files before testing.")
		
		# register the client
		eu().sub_register(session,username,password)
	
		# check the consumer folder
		cmd = "ls /etc/pki | grep 'consumer'"
		(ret,output) = eu().runcmd(session,cmd,"check the consumer folder after registration")
		if ret == 0 and 'consumer' in output and 'consumer.old' not in output:
			logging.info("It's successful to check the consumer folder after registration")
		else:
			raise error.TestFail("Test Failed - Failed to check the consumer folder after registration.")

		# get consumerid of the client
		consumerid = eu().sub_get_consumerid(session)
	
		# delete the consumer from server side.
		cmd = "curl -k -u %s:%s --request DELETE https://%s:443%s/consumers/%s"%(username, password, samhost, prefix, consumerid)
		(ret,output) = eu().runcmd(session,cmd,"check dependency on python-simplejson")
		#if ret == 0 and output == '':
		if ret == 0:
			logging.info("It's successful to delete the consumer from server side")
		else:
			raise error.TestFail("Test Failed - Failed to delete the consumer from server side.")
		
		# restart rhsmcert service
		eu().restart_rhsmcertd(session)
		
		# wait 2 mins
		time.sleep(125)
		
		# check if consumer.old exists
		cmd = "ls /etc/pki/consumer.old"
		(ret,output) = eu().runcmd(session,cmd,"check if consumer.old exists")
		if ret == 0 and output != '':
			logging.info("It's successful to check that consumer.old exists")
		else:
			raise error.TestFail("Test Failed - Failed to check that consumer.old exists.")
		
		# check if consumer folder exists
		cmd = "ls /etc/pki/consumer"
		(ret,output) = eu().runcmd(session,cmd,"check if consumer exists")
		if ret == 0 and output == '':
			logging.info("It's successful to check that empty consumer folder exists")
		elif ret != 0 and "ls: cannot access consumer: No such file or directory" in output:
			logging.info("It's successful to check that consumer folder does not exist")
		else:
			raise error.TestFail("Test Failed - Failed to check that consumer exists.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when check /etc/pki/consumer folder if moved to consumer.old after deleting the consumer:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
