import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID126353_listfactsinfo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:
		#register to server
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		eu().sub_register(session,username,password)
 		
 		#[A] - prepare test env
		#get env variables
		productid=ee().get_env(params)["productid"]
		autosubprod=ee().get_env(params)["autosubprod"]

		#[B] - run the test
		guest_name=params.get("guest_name")
		criteria=[]
		if "-6.2" in guest_name:
			criteria=["True","False"]
		elif "-5.8" in guest_name or "-6.3" in guest_name or "5.9" in guest_name or "6.4" in guest_name:
			criteria=["valid","invalid"]
		else:
			criteria=["valid","invalid"]
		
		#list facts before subscribe to a entitlement pool, "False" means entitlement_valid is invalid.
		listfactsinfo(session,criteria[1])

		#auto subscribe to a pool
		eu().sub_autosubscribe(session, autosubprod)

		#list facts after subscribe to a entitlement pool, "True" means entitlement_valid is valid.
		listfactsinfo(session,criteria[0])
		                 
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do list facts info:"+str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def listfactsinfo(session,entvalid):
	cmd="subscription-manager facts --list"
	(ret,output)=eu().runcmd(session,cmd,"list facts info")

	if ret==0 and "virt.host_type" in output and "virt.is_guest" in output and "system.entitlements_valid" in output:               
		host_type, is_guest, ent_valid = _parse_factsinfo(output)
		if host_type and is_guest and ent_valid:
			logging.info("It's successful to list facts info.")
		else: raise error.TestFail("Test Failed - List facts info are not correct.")
		if ent_valid != entvalid :
			raise error.TestFail("Test Failed - Facts of entitlement_valid is not correct.")
		else:
			logging.info("facts of entitlement_valid is correct.")
		if is_guest == "True" and (host_type == "kvm" or host_type == "ibm_systemz") :
			logging.info("facts of is_guest is true and host_type is %s"%host_type)
                elif is_guest=="False" and host_type != "kvm":
                        logging.info("facts of is_guest is false and host_type is not kvm")
		else:
			raise error.TestFail("Test Failed - Facts of is_guest and host_type are not correct.")

def _parse_factsinfo(output):
	#to get host_type, is_guest and entitlement_valid facts value for checking
	
	factslist=output.splitlines()
	for i in factslist:
		if "virt.host_type" in i:
			host_type = i[i.find(":")+1:].strip()
		elif "virt.is_guest" in i:
			is_guest = i[i.find(":")+1:].strip()
		elif "system.entitlements_valid" in i:
			ent_valid = i[i.find(":")+1:].strip()
			
	return host_type, is_guest, ent_valid

