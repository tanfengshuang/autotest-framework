import sys, os, subprocess, commands
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID331758_improve_unfriendly_message_of_instance_multiplier(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)
	try:
		#register the system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)

		# make sure the system is physical machine
		is_physical = check_physical_machine(session)
		print "is_physical: ", is_physical
		if is_physical == False:
			virt_to_phy(session)
		
		# list an instance-based subscription pool
		autosubprod = ee().get_env(params)["autosubprod"]
		cmd = 'subscription-manager list --available | egrep "Subscription Name:|Pool ID:|Suggested:"| grep "Red Hat Enterprise Linux High Touch Beta" -A2 | grep "Pool"'
		(ret,output)=eu().runcmd(session,cmd,"list an instance-based subscription and get it's pool")
		if ret == 0 and output != '':
			poolid = output.split(":")[1].strip()
			logging.info("It's successful to list an instance-based subscription and get it's pool.") 
		else:
			raise error.TestFail("Test Failed - Failed to list an instance-based subscription and get it's pool.")
		
		# attach an instance-based subscription with a quantity that is not an even multiple of the instance_multiplier
		cmd = "subscription-manager attach --pool=%s --quantity=1" %poolid
		(ret,output)=eu().runcmd(session,cmd,"attach an instance-based subscription")
		if ret != 0 and "must be attached using a quantity evenly divisible by 2" in output:
			logging.info("It's successful to check the error message of instance multiplier.") 
		else:
			raise error.TestFail("Test Failed - Failed to check the error message of instance multiplier.")
		
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the output of identity command when the machin is registered:"+str(e))
		
	finally:
		if is_physical == False:
			phy_to_virt(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)


def check_physical_machine(session):
	is_physical= True
	cmd = "subscription-manager facts --list | grep virt.is_guest:"
	(ret,output) = eu().runcmd(session,cmd,"check physical machine")
	if ret == 0 and output.split(':')[1].strip() == 'True':
		is_physical = False
	return is_physical

def virt_to_phy(session):
	cmd = "echo '{\"virt.is_guest\": \"False\"}' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
	(ret,output)=eu().runcmd(session,cmd,"virt_to_phy")
	if ret == 0 and "Successfully updated the system facts" in output:
		logging.info("It's successful to virt_to_phy.") 
	else:
		raise error.TestFail("Test Failed - Failed to virt_to_phy.")

def phy_to_virt(session):
	cmd = "echo '{\"virt.is_guest\": \"True\"}' > /etc/rhsm/facts/custom.facts; subscription-manager facts --update"
	(ret,output)=eu().runcmd(session,cmd,"phy_to_virt")
	if ret == 0 and "Successfully updated the system facts" in output:
		logging.info("It's successful to phy_to_virt.") 
	else:
		raise error.TestFail("Test Failed - Failed to phy_to_virt.")
	
