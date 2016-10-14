import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115187_updatefactsinfo(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

        #register to server
	username=ee().get_env(params)["username"]
	password=ee().get_env(params)["password"]
	eu().sub_register(session,username,password)

	try:
		#[A] - prepare test env
		#list current facts info of the system
		org_cpusocket = get_current_facts_info(session)
		selectlist = ['1', '2', '3', '4', '5', '6', '7', '8']
		if org_cpusocket in selectlist:
			selectlist.remove(org_cpusocket)
		modified_cpusockets = random.sample(selectlist, 1)[0]

		#[B] - run the test
		#update facts info of the system
		update_current_facts_info(session,org_cpusocket,modified_cpusockets)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do update the system facts:"+str(e))
	finally:
		eu().runcmd(session,'rm -f /etc/rhsm/facts/custom.facts', "")
		eu().runcmd(session,'subscription-manager facts --update', "")

		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ==========="%__name__)

def get_current_facts_info(session):
	if session != None:
		cmd="cat /var/lib/rhsm/facts/facts.json |sed -e 's/[{}]/''/g' | awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]}'|grep '\"cpu.cpu_socket(s)\"'|tr -cd 0-9 && echo"
		(ret,output)=eu().runcmd(session,cmd,"get current facts")	
		logging.info("current cpu_socket facts of the system: %s"%output)
		if ret == 0: 
			 return output[-2]
		else: raise error.TestFail("Test Failed - Failed to get current facts of cpu_socket.")
	else:
		cmd="cat /var/lib/rhsm/facts/facts.json |sed -e 's/[{}]/''/g' | awk -v k=\"text\" '{n=split($0,a,\",\"); for (i=1; i<=n; i++) print a[i]}'|grep '\"cpu.cpu_socket(s)\"'|tr -cd 0-9"
		(ret,output)=eu().runcmd(session,cmd,"get current facts")
		logging.info("current cpu_socket facts of the system: %s"%output)
		if ret == 0: 
			 return output
		else: raise error.TestFail("Test Failed - Failed to get current facts of cpu_socket.")

def update_current_facts_info(session,org_cpusocket, modified_cpusockets):

	#generate custom facts
        cmd="""echo '{"cpu.cpu_socket(s)":%s}' > /etc/rhsm/facts/custom.facts""" %modified_cpusockets
        (ret,output)=eu().runcmd(session,cmd,"generate custom facts")

	#update facts of cpu.cpu_sockets
        cmd="subscription-manager facts --update"
        (ret,output)=eu().runcmd(session,cmd,"update custom facts")

        if ret == 0 and "Successfully updated the system facts" in output:
        	if is_current_facts_updated(session,org_cpusocket, modified_cpusockets):
                	logging.info("It's successful to update the system facts.")
		else:
                	raise error.TestFail("Test Failed - Failed to update the system facts.")
	else:
		raise error.TestFail("Test Failed - Failed to update the system facts.")

def is_current_facts_updated(session,orgvalue, modifiedvalue):
	flag = False
	currentvalue = get_current_facts_info(session)
	if currentvalue == modifiedvalue and currentvalue !=orgvalue:
		flag = True
	return flag
