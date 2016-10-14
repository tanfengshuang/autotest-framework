import sys, os, subprocess, commands, random, re, time
import logging
import smtplib
from email.mime.text import MIMEText
from autotest_lib.client.common_lib import error
from autotest_lib.client.bin import utils
from autotest_lib.client.virt import virt_test_utils, virt_utils
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
from autotest_lib.client.tests.kvm.tests.ent_prod import ent_prod as ep
from autotest_lib.client.tests.kvm.tests.ent_env import ent_env as ee
from autotest_lib.client.tests.kvm.tests.pexpect import *

def subscribe_product_by_pool(session, sku):
		
	availpoollist = eu().sub_listavailpools_of_sku(session, sku)

	#get an available entitlement pool to subscribe with random.sample
	availpool = random.sample(availpoollist, 1)[0]
	poolid = availpool["PoolId"]

	#subscribe to the pool
	eu().sub_subscribetopool(session, poolid)

def git_install(session, params, username, password, sku):
	"""install git on system"""

	logging.info("+++++++++++++++ Begin to Install git +++++++++++++++")

        # register and subscribe 
        eu().sub_register(session, username, password, "")
	autosubprod=ee().get_env(params)["autosubprod"]
	eu().sub_autosubscribe(session, autosubprod)
        eu().cnt_yum_clean_cache(session)

        cmd = "yum install -y git"
        (ret, output) = eu().runcmd(session, cmd, "yum install package git", timeout="18000")
        if ret == 0 and ("Complete!" in output or "Nothing to do" in output):
                logging.info("It's successful to yum install package git.")
	else:
		logging.error("Test Failed - Failed to install git package!")

	#unregister after install the git package
	eu().sub_unregister(session)

	logging.info("+++++++++++++++ End to Install git ++++++++++++++++++++")
	


def ruby_install(session,username, password, sku):
	"""install ruby on host"""

	logging.info("+++++++++++++++ Begin to Install Ruby +++++++++++++++")

	# register and subscribe 
	eu().sub_register(session, username, password, "")
	subscribe_product_by_pool(session, sku)
	eu().cnt_yum_clean_cache(session)

	# enable repo rhel-6-server-optional-rpms to install rubygems
	cmd = "yum-config-manager --enable rhel-6-server-optional-rpms"
	(ret, output) = eu().runcmd(session, cmd, "enable repo rhel-6-server-optional-rpms", timeout="18000")

	cmd = "yum install --skip-broken ruby*"
	(ret, output) = eu().runcmd(session, cmd, "yum install package ruby*", timeout="18000")
	if ret == 0 and ("Complete!" in output or "Nothing to do" in output):
		logging.info("It's successful to yum install package ruby*.")
	else:
		raise error.TestFail("Test Failed - Failed to yum install package ruby*.")

	cmd = "yum install --skip-broken rubygems"
	(ret, output)=eu().runcmd(session, cmd, "yum install package rubygems", timeout="18000")
	if ret == 0 and ("Complete!" in output or "Nothing to do" in output):
		logging.info("It's successful to yum install package rubygems.")
	else:
		raise error.TestFail("Test Failed - Failed to yum install package rubygems.")

	cmd = "gem install json"
	(ret, output) = eu().runcmd(session, cmd, "gem install json", timeout="18000")

	cmd = "gem install httparty"
	(ret, output) = eu().runcmd(session, cmd, "gem install json", timeout="18000")

	logging.info("+++++++++++++++ End to Install Ruby +++++++++++++++")


def get_none_whitelist(session, params):
	""" git clone code and get sku_list not in whitelist. """
	git_install(session, params, "stage_test_12", "redhat", "RH0103708")

	cmd = "git clone git://git.app.eng.bos.redhat.com/rcm/utility-scripts.git /root/whitelist"
	(ret, output) = eu().runcmd(session, cmd, "git clone whitelist code to /whitelist", timeout="18000")

	# get SKU beginning with MCT in whitelist
	cmd = "python /root/whitelist/engproduct-cli/engproduct-cli.py list-legacy-skus --server=stage | grep MCT"
	(ret, output) = eu().runcmd(session, cmd, "get whitelist beginning with MCT", timeout="18000")
	whitelist = output.splitlines()

	# get all good SKU beginning with MCT
	cmd = "python /root/whitelist/engproduct-cli/engproduct-cli.py get-all-skus --server=stage --type=PRL | grep MCT"
	(ret, output) = eu().runcmd(session, cmd, "get all good sku_list beginning with MCT", timeout="18000")
	all_sku_list = output.splitlines()

	non_whitelist = list(set(all_sku_list)-set(whitelist))

	return non_whitelist, whitelist
	

def create_account(sku, account_name):

	logging.info("+++++++++++++++ Begin to Create Account +++++++++++++++")

	# create stage_account.csv
	account_info = "%s,redhat,%s,100" % (account_name, sku)
	account_file_path = '/account_create/stage_account.csv'
	account_file = open(account_file_path,'w')
	account_file.write(account_info)
	account_file.close()

	# create stage account with sku
	cmd = "ruby /account_create/create_consumers.rb /account_create/stage_account.csv"
	(ret, output)=eu().runcmd(None, cmd, "create stage account with sku %s" % sku, timeout="18000")

	logging.info("+++++++++++++++ End to Create Account +++++++++++++++")


def send_mail(to_list, sub, content):
	"""will send mails to people in to_list when test is failed"""
	
	sender = "soliu@redhat.com"
	msg = MIMEText(content)
	msg['Subject'] = sub
	msg['From'] = sender
	msg['To'] = ";".join(to_list)

	try:
		s = smtplib.SMTP('localhost')
		s.sendmail(sender, to_list, msg.as_string())
		s.quit()
		return True
	except Exception, e:
		print str(e)
		return False

def add_sku_into_whitelist(session, sku):
	"""Add a sku into whitelist"""
	cmd = "python /root/whitelist/engproduct-cli/engproduct-cli.py add-legacy-sku --server=stage --sku=%s" % sku
	(ret, output)=eu().runcmd(session, cmd, "Add the SKU %s to whitelist" % sku)
	if ret == 0:
		logging.info("It is successful to add sku %s into whitelist." % sku)
		return True 
	else:
		logging.error("Test Failed - Failed to add sku %s into whitelist." % sku)
		return False


def remove_sku_from_whitelist(session, sku):
	"""Remove a sku from whitelist"""
	cmd = "python /root/whitelist/engproduct-cli/engproduct-cli.py remove-legacy-sku --server=stage --sku=%s" % sku
	(ret, output)=eu().runcmd(session, cmd, "Remove the SKU %s from whitelist." % sku, timeout="18000")
	if ret == 0:
		logging.info("It is successful to remove the sku %s from whitelist." % sku)
		return True
	else:
		logging.error("Test Failed - Failed to remove sku %s from whitelist." % sku)
		return False


def verify_sku_in_whitelist(sku):
	"""Verify sku is in whitelist now"""
	cmd = "python /root/whitelist/engproduct-cli/engproduct-cli.py list-legacy-skus --server=stage|grep %s" % sku
	(ret, output)=eu().runcmd(session, cmd, "Verify the SKU %s is in whitelist now." % sku, timeout="18000")
	if sku in output:
           	logging.info("It's successful to verify SKU %s in whitelist now!" % sku)
		return True
        else:
          	logging.error("Test Failed - Failed to verify SKU %s in whitelist now!" % sku)
		return False


def refresh_pools(org_name):
	""" Remote exec function via pexpect """
	curl_cmd = "curl -k -X PUT -u candlepin_admin"
	url = " http://rhsmruby.dist.stage.ext.phx2.redhat.com/clonepin/candlepin/owners/%s/subscriptions?auto_create_owner=true" %org_name
	cmd = curl_cmd + url
	logging.info("Refresh pools using the command: %s" %cmd)
        child = spawn(cmd, timeout=60)
	output = "Enter host password for user"
	correct_info = "updated"
        index = child.expect(output, correct_info)
        if index == 0:
         	child.sendline('candlepin_amdin')
		print child
        elif index == 1:
              	child.close()
                return child.exitstatus, child.before

def refresh_pools_using_cmd(session, org_name):
	curl_cmd = "curl -k -X PUT -u candlepin_admin:candlepin_admin"
        url = " http://rhsmruby.dist.stage.ext.phx2.redhat.com/clonepin/candlepin/owners/%s/subscriptions?auto_create_owner=true" %org_name
        
	cmd = curl_cmd + url
        logging.info("Refresh pools using the command: %s" %cmd)
	(ret, output)=eu().runcmd(session, cmd, "Refresh pools.",timeout="18000")
	if ("created" in output) and ("updated" in output):
		logging.info("It is successful to refresh the subscription pools.")
		return True
	else:
		logging.error("Test Failed - Failed to refresh the subscription pools.")
		return False

def verify_subscription_pools(session, username, password, sku):
	'''verify skus in whitelist every 5 minutes and calculate the total time'''

	logging.info('++++++++++++++Begin to verify the subscription pools %s exist in the stage account every 5 minutes+++++++++++++++' % sku)
	
	max_time = 1800
	n = 0
	cmd = "subscription-manager list --available --all"
	while 1:
		(ret, output)=eu().runcmd(session, cmd, "Subscription pools verify.",timeout="18000")
		if sku in output:
			logging.info("It is successful to verify the subscription pools and the refresh time is %s" %n)
			break
		else:
			logging.info("Now we have waited %s secondes, but still need to wait another 5 minutes." % n)
			time.sleep(300)
			n = n+300

def verify_subscription_pools_not_exist(session, username, password, sku):
        '''verify skus in whitelist every 5 minutes and calculate the total time'''

        logging.info('++++++++++++++Begin to verify the subscription pools %s disappear in the stage account every 5 minutes+++++++++++++++' % sku)

        max_time = 1800
        n = 0
        cmd = "subscription-manager list --available --all"
        while 1:
                (ret, output)=eu().runcmd(session, cmd, "Subscription pools verify.",timeout="18000")
                if sku not in output:
                        logging.info("It is successful to verify the subscription pools and the refresh time is %s" % n)
                        break
                else:
                        logging.info("Now we have waited %s secondes, but still need to wait another 5 minutes." % n)
                        time.sleep(300)
                        n = n+300

def verify_subscription_pools_is_null(session, username, password):
        '''verify skus in whitelist every 5 minutes and calculate the total time'''

        logging.info('++++++++++++++Begin to verify the subscription pools is null every 5 minutes++++++++++++++')

        max_time = 1800
        n = 0
        cmd = "subscription-manager list --available --all"
        while 1:
                (ret, output)=eu().runcmd(session, cmd, "Subscription pools verify.", timeout="18000")
                if ("No Available subscription pools to list" in output) or ("No available subscription pools to list" in output):
                        logging.info("It is successful to verify the subscription pools is null and the refresh time is %s" %n)
                        break
                else:
                  	logging.info("Now we have waited %s seconds, still need to wait another 5 minutes." % n)
                      	time.sleep(300)
                        n = n+300	

def sku_list_whitelist(session, params, username, password, sku_list, orgname):
	'''This is the whitelist using more than one skus at one time'''
	logging.info('+++++++++++++++Begin to run the whitelist test using a sku list+++++++++++++++++++++++')
	
	# Step1: Make sure that the SKUs isn't available to subscription-manager
        eu().sub_register(session, username, password, "")
	
	testresult = True
	#testresult &= sku_one_by_one_whitelist(session, params, username, password, sku_list, orgname)

	cmd = "subscription-manager list --available --all"
	(ret, output)=eu().runcmd(session, cmd, "Make sure that SKUs isn't available to subscription-manager before adding to whitelist", timeout="18000")
	if ("No Available subscription pools to list" in output) or ("No available subscription pools to list" in output):
        	logging.info("It is successful to check the stage account is empty at the beginnig of whitelist test!" )
        else:
                logging.error("Test Failed - Failed to verify the account %s is empty at the beginning of whitelist test!" % username)
		testresult = False

	# Step2: Add skus to the whitelist
	list_length = len(sku_list)
	n = 0
	while n < list_length:
		testresult &= add_sku_into_whitelist(session, sku_list[n])
		n = n+1

	#wait an hour according to Dennis's suggestion
	time.sleep(3600)
   
	# Step3: Refresh subscription pools
        refresh_pools_using_cmd(None, orgname)

	# Step4: Verify that the skus exist in the stage_account
	
	#cmd = "subscription-manager list --available --all"
        #(ret, output)=eu().runcmd(session, cmd, "Make sure that the SKU is available to subscription-manager after adding to whitelist")
	n = 0
	while n < list_length:
		verify_subscription_pools(session, username, password, sku_list[n])
		n = n+1
	

	#Step5: Remove the skus in order to do the next test
	n = 0
        while n < list_length:
		testresult &= remove_sku_from_whitelist(session, sku_list[n])
                n = n+1

	#wait an hour according to Dennis's suggestion
	time.sleep(3600)

	#Step6: Refresh subscription pools
        refresh_pools_using_cmd(None, orgname)
	verify_subscription_pools_is_null(session, username, password)
	if testresult == True:
		return True
	else:
		return False	


def sku_one_by_one_whitelist(session, params, username, password, sku_list, orgname):
	''' This is the main function to do the sku test: sku attributes validation, and sku mapping between MKT and eng-products. '''

        logging.info("=============== Begin to Run Whitelist Test Case===============")

	testresult = True
	

	# install ruby
        #ruby_install(username, password, host_sku)

	# git clone code and get sku_list not in whitelist
	non_whitelist, whitelist = get_none_whitelist(session, params)

	# random fine SKU in non_whitelist
	#skus = random.sample(non_whitelist, 5)

	for sku in sku_list:
		# Step1: Verify that it is not currently on the whitelist
		if sku in whitelist:
			logging.error("Test Failed - Failed to verify SKU %s in non_whitelist now." % sku)
			testresult = False					
		
		# Step2: create an account with this sku using script
		#current_time = time.strftime('%Y%m%d%H%I%M%S',time. localtime(time.time()))
		#account_name = "stage_WL_test_%s" % (current_time)
		#create_account(sku, account_name)
		
		# Step3: Make sure that the SKU isn't available to subscription-manager
		eu().sub_register(session, username, password, "")

		cmd = "subscription-manager list --available --all"
		(ret, output)=eu().runcmd(session, cmd, "Make sure that SKU %s isn't available to subscription-manager before adding to whitelist" % sku, timeout="18000")

		if ("No Available subscription pools to list" in output) or ("No available subscription pools to list" in output):
			logging.info("It is successful to not list SKU %s in subscription-manager before adding it into whitelist" % sku)
		elif sku in output:
 			logging.error("Test Failed - Failed to list SKU %s in subscription-manager before adding it into whitelist" % sku)
			testresult = False
		else:
			logging.error("Test Failed - Failed to verify account %s is empty at the beginning of the whitelist test!" % username)
			testresult = False
	
		# Step4-1: Add this sku to the whitelist
		testresult &= add_sku_into_whitelist(session, sku)

		# waiting an hour for the suggestion of Dennis
		time.sleep(3600)
		
		# Step4-2:refresh subscription pools
		refresh_pools_using_cmd(None, orgname)

		# Step5: Verify that the sku is available for use in that account
		verify_subscription_pools(session, username, password, sku)
	
		# Step6: Remove the sku from whitelist for future testing
		testresult &= remove_sku_from_whitelist(session, sku)

		# waiting an hour for the suggestion of Dennis
		time.sleep(3600)

		#raise error.TestFail()
		refresh_pools_using_cmd(None, orgname)

		verify_subscription_pools_not_exist(session, username, password, sku)

	#return the test result

	if testresult == True:
		return True
	else:
		return False

		#sku_list_whitelist(session, username, password, sku_list, orgname)
	logging.info("+++++++++++++++ End to Run Whitelist Test +++++++++++++++")


def sku_whitelist_test(session, params, username, password, sku_list, orgname):
	"""the main function to do sku whitelist test"""
	testresult = True

	try:
		testresult &= sku_one_by_one_whitelist(session, params, username, password, sku_list, orgname)
		testresult &= sku_list_whitelist(session, params, username, password, sku_list, orgname)
		if not testresult:
			to_list = ['soliu@redhat.com','ftan@redhat.com']
			sub = "whitelist test failed"
			content = "FYI"
			send_mail(to_list, sub, content)
			raise error.TestFail("Test Failed - Failed to do sku whitelist testing!")
	except Exception, e:
                logging.error(str(e))
                raise error.TestFail("Test Failed - error happened when do sku whitelist testing:"+str(e))
	finally:
                logging.info("=========== End of Running Whitelist Test Case===========")

