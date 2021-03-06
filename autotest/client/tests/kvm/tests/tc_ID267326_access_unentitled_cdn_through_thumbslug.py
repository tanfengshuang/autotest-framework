import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID267326_access_unentitled_cdn_through_thumbslug(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:  
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		autosubprod = ee().get_env(params)["autosubprod"]
		pkgtoinstall = ee().get_env(params)["pkgtoinstall"]
		
		#register to and auto-attach
		register_and_autosubscribe(session, username, password, autosubprod)
		
		# back up /etc/yum.repos.d/redhat.repo as /etc/yum.repos.d/redhat.repo.bak
		back_up_redhatrepo(session)
		
		# set all repos in /etc/yum.repos.d/redhat.repo to be disabled
		disable_all_repos(session)
		
		#install a pkg
		cmd = "yum install -y %s" % (pkgtoinstall)
		(ret, output) = eu().runcmd(session, cmd, "install selected package %s" % pkgtoinstall, timeout=20000)
		if ret == 1 and ("No package %s available."%pkgtoinstall) in output:
			logging.info("It's successful to verify that system cannot access unentitled CDN contents through thumbslug")
		else:
			raise error.TestFail("Test Failed - failed to verify that system cannot access unentitled CDN contents through thumbslug")
			
	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when doing install one package of subscribed product:" + str(e))
		
	finally:
		uninstall_givenpkg(session, pkgtoinstall)
		restore_redhat_repo(session)
		eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)

def register_and_autosubscribe(session, username, password, autosubprod):
	cmd = "subscription-manager register --username=%s --password=%s --auto-attach"%(username, password)
	(ret, output) = eu().runcmd(session, cmd, "register_and_autosubscribe", timeout=20000)
	if (ret == 0) and ("The system has been registered with ID:" in output) and (autosubprod in output) and ("Subscribed" in output):
		logging.info("It's successful to register and auto-attach")
	else:
		raise error.TestFail("Test Failed - failed to register or auto-attach.")

def back_up_redhatrepo(session):
	cmd = "yum repolist;cat /etc/yum.repos.d/redhat.repo > /etc/yum.repos.d/redhat.repo.bak"
	(ret, output) = eu().runcmd(session, cmd, "back up redhat.repo")
	if ret == 0:
		logging.info("It's successful to back up redhat.repo file")
	else:
		raise error.TestFail("Test Failed - failed to back up redhat.repo file")

def disable_all_repos(session):
	cmd = "sed -i 's/enabled = 1/enabled = 0/g' /etc/yum.repos.d/redhat.repo"
	(ret, output) = eu().runcmd(session, cmd, "disable_all_repos")
	if ret == 0:
		logging.info("It's successful to disable_all_repos")
	else:
		raise error.TestFail("Test Failed - failed to disable_all_repos")

def restore_redhat_repo(session):
	cmd = "rm -f /etc/yum.repos.d/redhat.repo;cat /etc/yum.repos.d/redhat.repo.bak > /etc/yum.repos.d/redhat.repo"
	(ret, output) = eu().runcmd(session, cmd, "restore_redhat_repo")
	if ret == 0:
		logging.info("It's successful to restore_redhat_repo")
	else:
		raise error.TestFail("Test Failed - failed to restore_redhat_repo")
		
def uninstall_givenpkg(session, testpkg):
	cmd = "rpm -qa | grep %s"%(testpkg)
	(ret, output) = eu().runcmd(session, cmd, "check package %s" % testpkg, timeout=20000)
	if ret ==1:
		logging.info("There is no need to remove package")
	else:
		cmd = "yum remove -y %s" % (testpkg)
		(ret, output) = eu().runcmd(session, cmd, "remove select package %s" % testpkg, timeout=20000)
		if ret == 0 and "Complete!" in output and "Removed" in output:
			logging.info("The package %s is uninstalled successfully." % (testpkg))
		elif ret == 0 and "No package %s available"%testpkg in output:
			logging.info("The package %s is not installed at all" %(testpkg))
		else: 
			raise error.TestFail("Test Failed - The package %s is failed to uninstall." % (testpkg))



