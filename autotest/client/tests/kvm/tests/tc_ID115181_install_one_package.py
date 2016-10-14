import sys, os, subprocess, commands, random, re
import logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee

def run_tc_ID115181_install_one_package(test, params, env):

	session, vm = eu().init_session_vm(params, env)
	logging.info("=========== Begin of Running Test Case: %s ===========" % __name__)

	try:   
		#register to server
		username = ee().get_env(params)["username"]
		password = ee().get_env(params)["password"]
		eu().sub_register(session, username, password)
		
		#auto subscribe
		autosubprod = ee().get_env(params)["autosubprod"]
		eu().sub_autosubscribe(session, autosubprod)
		
		#get variables form ent_env
		repoid = ee().get_env(params)["productrepo"]
		pid = ee().get_env(params)["pid"]
		pkgtoinstall = ee().get_env(params)["pkgtoinstall"]
		
		#check repo exist
		if is_enabled_repo(session, repoid):
			#check package to be installed exist
			check_givenpkg_avail(session, repoid, pkgtoinstall)
			#install test-pkg
			install_givenpkg(session, pkgtoinstall)
		else:
			raise error.TestFail("Test Failed - The product repoid is not exist.")
		
		#check the cert file exist.
		certfile = pid + ".pem"
		check_cert_file(session, certfile)
		
		#check productid cert
		eu().sub_checkproductcert(session, pid)

		#uninstall test-pkg
		uninstall_givenpkg(session, pkgtoinstall)

	except Exception, e:
		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when doing install one package of subscribed product:" + str(e))
	finally:
                eu().sub_unregister(session)
		logging.info("=========== End of Running Test Case: %s ===========" % __name__)


def is_enabled_repo(session, repoid):
	cmd = "yum repolist"
	(ret, output) = eu().runcmd(session, cmd, "list enabled repos", timeout=20000)
	if ret == 0 and "repolist:(\s+)0" in output:
		raise error.TestFail("Test Failed - There is not enabled repo to list.")
	else:
		logging.info("It's successful to list enabled repos.")
	if repoid in output:
		return True
	else:
		return False

def check_givenpkg_avail(session, repoid, testpkg):
	cmd = "repoquery -a --repoid=%s | grep %s" % (repoid, testpkg)
	(ret, output) = eu().runcmd(session, cmd, "check package available", timeout=20000)
	if ret == 0 and testpkg in output:
		logging.info("The package %s exists." % (testpkg))
	else : 
		raise error.TestFail("Test Failed - The package %s does not exist." % (testpkg))

def install_givenpkg(session, testpkg):
	cmd = "yum install -y %s" % (testpkg)
	(ret, output) = eu().runcmd(session, cmd, "install selected package %s" % testpkg, timeout=20000)
	if ret == 0 and "Complete!" in output and "Error" not in output:
		logging.info("The package %s is installed successfully." % (testpkg))
	else: 
		raise error.TestFail("Test Failed - The package %s is failed to install." % (testpkg))

def uninstall_givenpkg(session, testpkg):
	cmd = "yum remove -y %s" % (testpkg)
	(ret, output) = eu().runcmd(session, cmd, "remove select package %s" % testpkg, timeout=20000)

	if ret == 0 and "Complete!" in output and "Removed" in output:
		logging.info("The package %s is uninstalled successfully." % (testpkg))
	else: 
		raise error.TestFail("Test Failed - The package %s is failed to uninstall." % (testpkg))
	
def check_cert_file(session, certfile):
	cmd = "ls -l /etc/pki/product/%s" %certfile
	(ret, output) = eu().runcmd(session, cmd, "check the product cert file exists")
	if ret == 0 :   
		logging.info("It's successful to check product cert file exists.")            
	else:
		raise error.TestFail("Test Failed - it's failed to check product cert file exists.")
