import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID189940_repos_cmd_default_to_list(test, params, env):
	
	session, vm = eu().init_session_vm(params, env)
	logging.info("========== Begin of Running Test Case %s ==========" %__name__)
	
	try:
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)

		#prepare a env auto subsribe to a pool
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		#run cmd with repos only
		cmd = "subscription-manager repos"
		(ret, output) = eu().runcmd(session, cmd, "running repos without option")
		reposres = sub_check_output(output)
		reposout = output.splitlines()
		reposout.sort()
		
		#run cmd with repos --list
		cmd = "subscription-manager repos --list"
		(ret, output) = eu().runcmd(session, cmd, "running repos with option: --list")
		reposlistres = sub_check_output(output)
		reposlistout = output.splitlines()
		reposlistout.sort()
		
		if reposres and reposlistres and (reposout == reposlistout):
			logging.info("It's successfull to check the default output of repos :the output of repos is the same as repos --list!")
		else:
			raise error.TestFail("Test Faild - Failed to check the default output of repos: the output of repos is not the same as repos --list!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the default output of repos cmd:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("========== End of Running Test Case: %s ==========" %__name__)
	
def sub_check_output(output):
	if ("Repo Id:" in output or "Repo ID" in output) and "Repo Name:" in output \
	  and ("Repo Url:" in output or "Repo URL" in output) and "Enabled:" in output :
		return True
	else:
		return False
