"""
@author		: qianzhan@redhat.com
@date		: 2013-03-12
"""

import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID178111_register_with_auto_when_no_compatible_subscription(test, params, env):
	try:
		session,vm=eu().init_session_vm(params,env)
		logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		samip=params.get("samhostip")

		#change the system time
		cmd="date -s 20330101"
		(ret,output)=eu().runcmd(session,cmd,"set all subscriptions to be not compatible by changing client system time")
		if ret == 0:
			logging.info("It's successful to set all subscriptions to be not compatible by changing client system time.")
		else:
			raise error.TestFail("Test Failed - Failed to set all subscriptions to be no compatible by changing client system time.")
		
		(ret, output)=eu().runcmd_remote(samip, 'root', 'redhat', cmd)
		if ret == 0:
			logging.info("It's successful to set all subscriptions to be not compatible by changing server system time.")
		else:
			raise error.TestFail("Test Failed - Failed to set all subscriptions to be no compatible by changing server system time.")

		#register
		cmd_to_test="subscription-manager register --username=%s --password='%s' --auto-attach"%(username, password)
		(ret,output)=eu().runcmd(session,cmd_to_test,"register with auto subscribe option")
		if (ret!=0) and ("The system has been registered with ID" in output) and ("Not Subscribed" in output):
			logging.info("It's successful to verify registeration with auto subscribe option if there is no compatible subscription")
		else:
			raise error.TestFail("Test Failed -Failed to verify registeration with auto subscribe option if there is no compatible subscription")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when verify registeration with auto subscribe option if there is no compatible subscription:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		recover_sys_time(session, samip)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
		
def recover_sys_time(session, samip):
	cmd_recover="hwclock --hctosys"
	(ret,output)=eu().runcmd(session,cmd_recover,"recover the system time")
	if ret==0 :
		logging.info("It's successful to recover the client system time")
	else:
		raise error.TestFail("Test Failed -Failed to recover the client system time")
	(ret, output)=eu().runcmd_remote(samip, 'root','redhat', cmd_recover)
	if ret==0:
		logging.info("It's successful to recover the server system time")
	else:
		raise error.TestFail("Test Failed -Failed to recover the server system time")
	
