import sys, os, subprocess, commands, random
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID190010_release_cmd_default_to_show(test, params, env):
	
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
		
		#run cmd with release only
		cmd = "subscription-manager release"
		(ret, output) = eu().runcmd(session, cmd, "running release without option")
		releaseout = output
		
		#run cmd with release --show
		cmd = "subscription-manager release --show"
		(ret, output) = eu().runcmd(session, cmd, "running release with option: --show")
		releaseshowout = output
		
		if releaseout == releaseshowout :
			logging.info("It's successfull to check the default output of release: the output of release is the same as release --show!")
		else:
			raise error.TestFail("Test Faild - Failed to check the default output of repos: the output of release is not the same as release --show!")
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened to check the default output of release cmd:" + str(e))
	finally:
		eu().sub_unregister(session)
		logging.info("========== End of Running Test Case: %s ==========" %__name__)
