import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID332568_run_wrong_command_option_given_in_the_Man_page_of_rhsm_debug(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		# check the man page header
		cmd='man rhsm-debug | egrep "Certificate Information Tool"'
		(ret,output)=eu().runcmd(session,cmd,"check the man page header")
		outputb = output.strip().split(" ")
		if ret == 0 and outputb[0] == outputb[len(outputb)-1] == "rhsm-debug(8)":
			logging.info("It's successful to check the man page header.") 
		else:
			raise error.TestFail("Test Failed - Failed to check the man page header.")
		
		# check the correct command system
		cmd = 'man rhsm-debug | egrep "The currently supported modules are" -A5'
		(ret,output)=eu().runcmd(session,cmd,"check the correct command system")
		if ret == 0 and "system" in output:
			logging.info("It's successful to check the correct command system.") 
		else:
			raise error.TestFail("Test Failed - Failed to check the correct command system.")
		
		# check --proxypassword is correctly displayed.
		cmd = 'man rhsm-debug | egrep "Gives the password to use to authenticate to the HTTP proxy" -B1'
		(ret,output)=eu().runcmd(session,cmd,"check the correct command system")
		if ret == 0 and "-\x08--\x08-p\x08pr\x08ro\x08ox\x08xy\x08yp\x08pa\x08as\x08ss\x08sw\x08wo\x08or\x08rd\x08d=\x08=P\x08PR\x08RO\x08OX\x08XY\x08YP\x08PA\x08AS\x08SS\x08SW\x08WO\x08OR\x08RD\x08D" in output:
			logging.info("It's successful to check --proxypassword is correctly displayed") 
		else:
			raise error.TestFail("Test Failed - Failed to check --proxypassword is correctly displayed")
		
		# check --sos is correctly displayed.
		cmd = 'man rhsm-debug | egrep "sos"'
		(ret,output)=eu().runcmd(session,cmd,"check --sos")
		if ret == 0 and "Excludes data files that are also  collected  by  the  sosreport" in output:
			logging.info("It's successful to check --sos") 
		else:
			raise error.TestFail("Test Failed - Failed to check --sos")

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check subscription-manager man page for new list options:"+str(e))
	finally:
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)
