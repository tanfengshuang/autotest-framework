import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID166522_logging_rhsmcertd_status(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		# config rhsmcertd in /etc/rhsm/rhsm.conf
		sub_set_certfrequency(session, 1)
		sub_set_healfrequency(session, 1)
		
			
		cmd3='service rhsmcertd restart'
		(ret3,output3)=eu().runcmd(session,cmd3,"restart rhsmcertd service")
			
		cmd4='tail -4 /var/log/rhsm/rhsmcertd.log'
		(ret4,output4)=eu().runcmd(session,cmd4,"restart rhsmcertd service")
			
		if ret4 == 0 and "healing check started: interval = 1" and "cert check started: interval = 1" and "certificates updated" in output4:
			logging.info("It's successful to logging rhsmcertd statements.")
		else:
			error.TestFail("Test Failed - Failed to logging rhsmcertd statements.")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do logging rhsmcertd statements :"+str(e))

	finally:
		sub_set_certfrequency(session, 240)
		sub_set_healfrequency(session, 1440)
		
		cmd='service rhsmcertd restart'
		eu().runcmd(session, cmd, "restart rhsmcertd")
		eu().sub_unregister(session)
		
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def sub_set_healfrequency(session, frtime):
	
	cmd = "subscription-manager config --rhsmcertd.healfrequency=%s" %frtime
	cmd510 = "subscription-manager config --rhsmcertd.autoattachinterval=%s" %frtime
	(ret, output) = eu().runcmd(session, cmd, "set healfrequency")

	if ret == 0:
		logging.info("It successful to set healfrequency")
	else:
		(ret, output) = eu().runcmd(session, cmd510, "set autoattachinterval")
		if ret == 0:
			logging.info("It successful to set autoattachinterval")
		else:
			logging.error("Test Failed - Failed to set healfrequency or autoattachinterval.")


def sub_set_certfrequency(session, frtime):
	
	cmd = "subscription-manager config --rhsmcertd.certfrequency=%s" %frtime
	cmd510 = "subscription-manager config --rhsmcertd.certcheckinterval=%s" %frtime
	(ret, output) = eu().runcmd(session, cmd, "set certfrequency")

	if ret == 0:
		logging.info("It successful to set healfrequency")
	else:
		(ret, output) = eu().runcmd(session, cmd510, "set certcheckinterval")
		if ret == 0:
			logging.info("It successful to set certfrequency")
		else:
			logging.error("Test Failed - Failed to set certfrequency or certcheckinterval.")
