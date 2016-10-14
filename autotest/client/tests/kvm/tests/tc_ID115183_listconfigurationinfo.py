import sys, os, subprocess, commands, random 
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115183_listconfigurationinfo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#list configuration info for the system
	        cmd="subscription-manager config --list"
		(ret,output)=eu().runcmd(session,cmd,"list configuration info")

		if (ret == 0) and ("server" in output) and ("rhsm" in output) and ("rhsmcertd" in output):
	      		if is_configuration_item_correct(session,output):
                		logging.info("It's successful to list configuration info for the system.")
                	else: raise error.TestFail("Test Failed - List configuration info are not correct.")
		else: 
			raise error.TestFail("Failed to List configuration info.")  

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list configuration info:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def is_configuration_item_correct(session,output):
	flag = False
	cmd="cat /etc/rhsm/rhsm.conf | grep '^hostname'"
	(ret_hn, output_hn)=eu().runcmd(session,cmd,"check hostname configuration")

        cmd="cat /etc/rhsm/rhsm.conf | grep '^baseurl'"
        (ret_bu, output_bu)=eu().runcmd(session,cmd,"check baseurl configuration")
        if ret_hn == 0 and output_hn.split("=")[1].strip() in output and \
	   ret_bu == 0 and output_bu.split("=")[1].strip() in output:
                flag = True

	return flag
