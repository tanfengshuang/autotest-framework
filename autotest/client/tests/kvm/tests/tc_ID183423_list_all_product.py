"""******************************************

@author		: shihliu@redhat.com
@date		: 2013-03-11

******************************************"""

import sys, os, subprocess, commands, random
import logging
import time , datetime
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID183423_list_all_product(test, params, env):

	session,vm=eu().init_session_vm(params,env)
	logging.info("=========== Begin of Running Test Case: %s ==========="%__name__)

	try:   
		#register a system
		username=ee().get_env(params)["username"]
		password=ee().get_env(params)["password"]
		productid=ee().get_env(params)["productid"]
		eu().sub_register(session,username,password)

		#list all available entitlement pools
		cmd="subscription-manager list --available --all"
		(ret, output)=eu().runcmd(session, cmd, "listing available pools")
		
		if ret == 0:
			if "no available subscription pools to list" not in output.lower():
				if productid in output:
					logging.info("The right available pools are listed successfully.")
					list_enddate(output)
				else:
					raise error.TestFail("Not the right available pools are listed!")

			else:
				logging.info("There is no Available subscription pools to list!")

		else:
			raise error.TestFail("Test Failed - Failed to list all available pools.")
			sub_listallavailpools(session,productid)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do Lists all products:"+str(e))
		
	finally:
		eu().sub_unregister(session)
		logging.info("=========== End of Runnidng Test Case: %s ==========="%__name__)

def list_enddate(output):
	datalines = output.splitlines()
	segs = []
	timeline = ""
	for line in datalines:
		if "Ends:" in line:
			 tmpline = line
			 segs.append(tmpline)
	for aa in segs:
		endtimeitem = aa.split(":")[0].replace(' ','')
		endtimevalue = aa.split(":")[1].strip()
		if compare_time(endtimevalue) == 0:
			logging.info("It's correct to list this subscription.")	
		else :
			raise error.TestFail("The subscription shouldn't be list")

def compare_time(realenddate):
	systimebef = time.strftime('%y%m%d',time.localtime(time.time()))
	systemtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(systimebef,"%y%m%d")))
	realendtime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(realenddate,"%m/%d/%Y")))
	delday = (realendtime - systemtime).days
	
	if delday > 0:
		logging.info("The subscription's end time after the system time")
		return 0
	else:
		raise error.TestFail("The subscription's end time before the system time")
		
