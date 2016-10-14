#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, time, random, re
#from get_https import *
#from read_table import *

from autotest_lib.client.tests.kvm.tests.skutest.download_sku import *
from autotest_lib.client.tests.kvm.tests.skutest.get_test_values import *
from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu
import logging


def subscription_register(session, username, password, subtype=""):
	
	#Check if the subscrpition manager is registered.
	cmd_identity = "subscription-manager identity"
        (ret, output)=eu().runcmd(session, cmd_identity, "identity")
	
	if subtype == "":
                cmd = "subscription-manager register --username=%s --password='%s'"%(username, password)
        else:
                cmd = "subscription-manager register --type=%s --username=%s --password='%s'"%(subtype, username, password)

     	if ret == 0:
     		logging.info("The system is registered to server now.")
		#If the subscription is registered, then need to unregister first.
              	cmd_unregister = "subscription-manager unregister"
             	(ret, output) = eu().runcmd(session, cmd_unregister, "unregister")
              	if ret == 0:
                	if ("System has been unregistered." in output) or ("System has been un-registered." in output):
                      		logging.info("It's successful to unregister.")
                     	else:
                        	logging.info("The system is failed to unregister, try to use '--force'!")
                             	cmd += " --force"
             	else:
                    	if "Network error" in output:
                       		logging.error("Network error, unable to unregister.")
                      	return False
      	else:
		if "Network error" in output:
			logging.error("Network error, unable to register to the stage candlepin.")
			return False
             	else:
			logging.info("The system is not registered to server now.")

	#Register the system.
	(ret, output) = eu().runcmd(session, cmd, "register")
	if ret == 0:
        	if ("The system has been registered with ID:" in output) or ("The system has been registered with id:" in output):
                	logging.info("It's successful to register.")
             	else:
               		logging.error("Test Failed - The information shown after registered is not correct.")
			return False
	else:
       		logging.error("Test Failed - Failed to register.")
		return False

	return True 

def subscription_subscribe(session, poolid):
	cmd = "subscription-manager subscribe --pool=%s"%(poolid)
	(ret, output) = eu().runcmd(session, cmd, "subscribe")

	if ret == 0:
        	#Note: the exact output should be as below:
               	#For 6.2: "Successfully subscribed the system to Pool"
             	#For 5.8: "Successfully consumed a subscription from the pool with id"
              	if "Successfully " in output:
                	logging.info("It's successful to subscribe.")
              	else:
                	logging.error("Test Failed - The information shown after subscribing is not correct.")
			return False
	else:
        	logging.error("Test Failed - Failed to subscribe.")
		return False

	return True

def compare_lists(r_str, t_str):
	r_list = r_str.split(',')
	t_list = t_str.split(',')
	if len(r_list) == len(t_list):
		for i in r_list:
			if i in t_list:
				pass
			else:
				return False
	else:
		return False

def compare_test_values_with_reference_values(sku_type, refer_dict, test_dict):
	target_sku = test_dict['id']
	fail_list = []
	pass_list = []

	logging.info('Print test data comparison of sku attributes with reference standard ... \n')
	#define a dict that include the attributes need to test
	if sku_type == "95917_type":
		attribute_dict = {'SKU':'id','Product Hierarchy: Product Category':'ph_category','Product Hierarchy: Product Line':'ph_product_line','Product Hierarchy: Product Name':'ph_product_name','Product Name':'name','Product Family':'product_family','Virt Limit':'virt_limit','Variant':'variant','Socket(s)':'sockets','Support Type':'support_type','Multiplier':'multiplier','Unlimited Product':'unlimited_product','Cores':'cores','JON Management':'jon_management','VCPU':'vcpu','Virt-only':'virt_only','Management Enabled':'management_enabled','Enabled Consumer Types':'enabled_consumer_types','Support Level':'support_level','Required Consumer Type':'requires_consumer_type','Arch':'arch','RAM':'ram','Servers':'servers'}
	else:
		if sku_type == "2013_model_type":
			attribute_dict = {'SKU':'id','Product Hierarchy: Product Category':'ph_category','Product Hierarchy: Product Line':'ph_product_line','Product Hierarchy: Product Name':'ph_product_name','Product Name':'name','Product Family':'product_family','Virt Limit':'virt_limit','Variant':'variant','Socket(s)':'sockets','Support Type':'support_type','Multiplier':'multiplier','Unlimited Product':'unlimited_product','Cores':'cores','JON Management':'jon_management','VCPU':'vcpu','Virt-only':'virt_only','Management Enabled':'management_enabled','Enabled Consumer Types':'enabled_consumer_types','Support Level':'support_level','Required Consumer Type':'requires_consumer_type','Arch':'arch','RAM':'ram','Instance Based Virt Multiplier':'instance_multiplier','Cloud Access Enabled':'cloud_access_enabled','Stackable':'multi-entitlement','Host Limited':'host_limited','Stacking ID':'stacking_id','Multi Entitlement':'multi-entitlement','Derived SKU':'derived_sku'}

	for rkey in refer_dict.keys():
		nokey = 0
		rvalue = refer_dict[rkey]
		logging.info('        Expected data from Reference DOC is %s: %s' %(rkey, rvalue))

		tkey = attribute_dict[rkey]
		if test_dict.has_key(tkey):
			tvalue = test_dict[tkey]
		elif rkey == 'SKU':
			nokey = 1
		else:
			tvalue = 'n/a'
			tvalue = unicode(tvalue, 'utf-8')

		if nokey == 0:
			#process the tvalue get from test_dict
			if isinstance(tvalue, int):
				tvalue = unicode(tvalue)

			logging.info('        Test data from Candlepin is %s : %s' %(tkey,tvalue))
			if tkey == 'arch':
				if compare_lists(rvalue.lower(), tvalue.lower()) == False:
					logging.error('        %s Comparison is different!' %rkey)
					fail_list.append(rkey)
				else:
					logging.info('        %s Comparison is the same!' %rkey)
					pass_list.append(rkey)
			else:
				if isinstance(rvalue, int):
					rvalue = str(rvalue)

				if isinstance(tvalue, int):
					tvalue = str(tvalue)

				if rvalue.lower() != tvalue.lower():
					logging.error('        %s Comparison is different!' %rkey)
					fail_list.append(rkey)
				else:
					logging.info('        %s Comparison is the same!' %rkey)
					pass_list.append(rkey)
		else:
			logging.info('        Test data does not have this item : Test data Missing "%s"' %tkey)
			logging.info('        %s Comparison is different!' %rkey)
			fail_list.append(rkey)

		logging.info('\n')


	if len(fail_list) == 0:
		logging.info('        %s Attributes Test : --- PASS!' %(target_sku))
		return True
	else:
		logging.error('        %s Attributes Test : --- FAIL!' %(target_sku))
		logging.error('FAIL items:')
		for i in fail_list:
			logging.error('   %s' %i)
		return False

def sku_test(sku,\
	     sku_type,\
             prourl,\
             download_sku_file_dir,\
             account_username,\
             account_password,\
             refer_dict):

	# Download sku from Candlepin server
	logging.info('Ready to download target sku %s' %sku)
	ret = download_sku(sku, prourl, download_sku_file_dir, account_username, account_password)
	if ret == False:
		return 1

	# Parse test - get test values ...
	logging.info('Ready to get Test data from download sku...')
	test_dict = {}
	#test_dict=get_test_values(sku,download_sku_file_dir,sku,write_test_data_dir,is_wirte_data)	-- ftan
	test_dict = get_test_values(sku, download_sku_file_dir)
	logging.info('Get test data from candlepin for SKU %s: %s ' %(sku, test_dict))

	# Get Reference documentation table
	logging.info('Read Reference Standard data for SKU %s: %s ' %(sku, refer_dict))

	logging.info('Begin to compare sku attributes with reference doc-95917 ')
	# compare reference valuses to test valuses
	ret = compare_test_values_with_reference_values(sku_type, refer_dict, test_dict)
	return ret
	logging.info('End of comparing sku attributes with reference doc-95917')

def get_productids_from_entitlement_cert_with_openssl(session, serialnum):
	#get product_id list from entitlement cert in cert-1.0
	str = '1.3.6.1.4.1.2312.9.1.*.1:'
	cmd = 'openssl x509 -text -noout -in /etc/pki/entitlement/%s.pem | grep -E %s' %(serialnum, str)
	(ret, output) = eu().runcmd(session, cmd, "get product id from entitlement cert")
	pidlist = []
	if ret == 0:
		logging.info('It is successful to get productid from entitlement cert.')
		datalines = output.splitlines()
		for line in datalines:
			line = re.sub('1.3.6.1.4.1.2312.9.1.', '', line)
			pidlist.append(line.split('.')[0].strip())
		pidlist = list(set(pidlist))
		logging.info('Productids from entitlement cert are %s.\n' %pidlist)
	else:
		logging.info('No productid from entitlement cert.\n')

	return pidlist

def get_productids_from_entitlement_cert_with_rct(session, serialnum):
	#get product_id list from entitlement cert in cert-3.0
        cmd = 'rct cat-cert /etc/pki/entitlement/%s.pem | grep -v "Stacking ID:"|grep -v "Pool ID"|grep "ID:"' %(serialnum)
        (ret, output) = eu().runcmd(session, cmd, "get product id from entitlement cert")
        pidlist = []
        if ret == 0:
                logging.info('It is successful to get productid from entitlement cert.')
                datalines = output.splitlines()
                for line in datalines:
                        line = re.sub('ID: ',' ',line)
                        pidlist.append(line.split('.')[0].strip())
                pidlist = list(set(pidlist))
                logging.info('Productids from entitlement cert are %s.\n' %pidlist)
        else:
                if 'rct: command not found' in output:
			pidlist = get_productids_from_entitlement_cert_with_openssl(session, serialnum)
                else:
                        logging.info('No productid from entitlement cert.\n')

        return pidlist

def sku_mapping_test(session, exp_prdids_list, serialnum):
	# verify sku mapping between MKT product and eng products
	#get productid list from entitlement cert
	logging.info('Productids from Reference DOC are %s.\n' %exp_prdids_list)
	totest_prdids_list = get_productids_from_entitlement_cert_with_rct(session, serialnum)
	# compare two productid list
	(list1, list2) = eu().cnt_get_two_arrays_diff(exp_prdids_list, totest_prdids_list)
	if len(list1) > 0 or len(list2) > 0:
		logging.error("The consistency test between expected Productids from Reference DOC %s and Productids from entitlement cert %s: --- FAILED.\n"%(exp_prdids_list, totest_prdids_list))
		#print the list1 productids
		logging.info("Below '%d' productids in expected Productids from Reference DOC could not be found in Productids from entitlement cert:" %len(list1))
		eu().cnt_print_list(list1)

		#print the list2 productids
		logging.info("Below '%d' productids in Productids from entitlement cert could not be found in expected Productids from Reference DOC:" %len(list2))
		eu().cnt_print_list(list2)

		return False
	else:
		logging.info("Verify consistency between expected Productids from Reference DOC %s and Productids from entitlement cert %s: --- PASS.\n"%(exp_prdids_list, totest_prdids_list))
		return True

def get_skus_from_reference_doc(path):
        file = open(path)
        lists = eval(file.read())
        sku_list = []
        for dict in lists:
                sku_list.append(dict['SKU'])

        sku_list.sort()
        sku_list = list(set(sku_list))

        length = len(sku_list)

        return sku_list

def sub_list_all_avail_pools_of_sku(session, sku):
        cmd = "subscription-manager list --available --all"
        (ret, output) = eu().runcmd(session, cmd, "listing all available pools")

        if ret == 0:
                if "no available subscription pools to list" not in output.lower():
                        if sku in output:
                                logging.info("The right available pools are listed successfully.")
                                pool_list = eu().parse_listavailable_output(output)
                                pool_list_of_sku = []
                                for prd in pool_list:
                                        if ("PoolId" in prd.keys() and prd["PoolId"] == sku) or ("PoolID" in prd.keys() and prd["PoolID"] == sku) or ("SKU" in prd.keys() and prd["SKU"] == sku):
                                                pool_list_of_sku.append(prd)
                                return pool_list_of_sku
                        else:
				logging.error("Not the right available pools are listed!")
				return None

                else:
                        logging.info("There is no Available subscription pools to list!")
                        return None
        else:
		logging.error("Test Failed - Failed to list available pools.")
		return None
                #raise error.TestFail("Test Failed - Failed to list available pools.")

def check_sku_RHUI_type(sku):
	auto_client_path = os.environ['AUTODIR']
        reference_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Reference_standard.txt")

	sku_type = ""
	refer_dict_lists = []
        refer_dict_lists = eval(open(reference_path).read())
        for i in refer_dict_lists:
                if i['SKU'] == sku:
                        if i['Required Consumer Type'] == "RHUI":
                                sku_type = "RHUI"
                        else:
                                sku_type = "none_RHUI_type"
        return sku_type

def sku_test_common(session, params, sku, consumer_type=''):
	''' This is the main function to do the sku test: sku attributes validation, and sku mapping between MKT and eng-products. '''
	logging.info("+++++++++++++++'%s' - Begin to Run SKU Test +++++++++++++++" % sku)
	runcasein = params.get('runcasein')
  	guestname = params.get('guest_name')
	category = params.get('category')
	ppc_s390_flag = 0

	try:
		# sku testing
		kvm_test_dir = os.path.join(os.environ['AUTODIR'], 'tests/kvm/tests')
		sku_script_path = os.path.join(kvm_test_dir, 'skutest')
		reference_path = os.path.join(sku_script_path, 'Reference_standard.txt')
		regression_attribute_result_path = os.path.join(sku_script_path, "Regression_attribute_result.txt")
		regression_mapping_result_path = os.path.join(sku_script_path, "Regression_mapping_result.txt")


		hostname = params.get('hostname')
		stage_passwd = 'redhat'
		product_download_url = 'https://%s/subscription/products/' %hostname


		# Get Reference documentation table
		refer_dict_lists = []
		refer_dict_lists = eval(open(reference_path).read())
		refer_dict = {}
		for i in refer_dict_lists:
			if i['SKU'] == sku:
				if i.has_key('Multi Entitlement'):
					sku_type = "2013_model_type"
				else:
					sku_type = "95917_type"
				stage_name = i['Username']
				logging.info("Get the sku %s mathed Account: %s" %(sku, stage_name))
				#get eng_product attributes for mappint test
				eng_products = i['Eng Productid(s)']
				logging.info("Get the sku %s mathed eng_products: %s" %(sku, eng_products))
				#get other refer attributes
				del_key = 'Username'
				print '* Pop item %s for %s' %(del_key, i['SKU'])
				i.pop(del_key)
				del_key = 'Eng Productid(s)'
				print '* Pop item %s for %s' %(del_key, i['SKU'])
				i.pop(del_key)
				refer_dict = i
				break
			else:
				continue

		if len(refer_dict.keys()) == 0:
			raise error.TestFail("Test Failed - Faild to get reference data for SKU %s.\n"%sku)

		if "attributes" in category:
			#only verify SKU attributes
			download_sku_file_dir = os.path.join(sku_script_path, 'sku_download')
			write_test_data_dir = os.path.join(sku_script_path, 'output_test_data')

			if sku_test(sku, sku_type, product_download_url, download_sku_file_dir, stage_name, stage_passwd, refer_dict):
				logging.info("It's successful to do sku attributes testing.\n" )
			else:
				raise error.TestFail("Test Failed - Faild to do sku attributes testing.\n")

		elif "mapping" in category or "sku_attribute_test" in category:
			ppc_s390_flag = 1
			test_result = True
 			test_result_pool = True
			#verify mapping of SKU: MKT <-> eng products
			test_result &= subscription_register(session, stage_name, stage_passwd, consumer_type)
			if not test_result:
				return (test_result, test_result_pool)

			availpoollist = sub_list_all_avail_pools_of_sku(session, sku)

			if "sku_attribute_test" in category:
				if (availpoollist == None) or (len(availpoollist) > 0):
					logging.error("Test Failed - Faild to do mapping for SKU %s due to no available pools for the subscription.\n" % sku)
					test_result = False
					test_result_pool = False
					return (test_result,test_result_pool)

			#get an available entitlement pool to subscribe with random.sample
			availpool = random.sample(availpoollist, 1)[0]
			
			poolid = ""
			if "PoolId" in availpool.keys():
				poolid = availpool["PoolId"]
				
			elif "PoolID" in availpool.keys():
				poolid = availpool["PoolID"]
				
			else:
				logging.error("Failed to get pool id value from the available entitlement pool.\n")
				#raise error.TestFail("Test Failed - Faild to get pool id value from the available entitlement pool.\n")			

			#subscribe to the pool
			test_result &= subscription_subscribe(session, poolid)
			if not test_result:
				return (test_result, test_result_pool)

			#get serialnumlist after subscription
			serialnum = eu().get_subscription_serialnumlist(session)

			#check whether entitlement certificates generated and productid in them or not
			eu().cnt_verify_sku_in_entitlement_cert(session, serialnum[0], sku)

			exp_pidlist = []
			if eng_products != 'n/a':
				_exp_pidlist = eng_products.split(',')
				for e in _exp_pidlist:
					exp_pidlist.append(e.strip())

			if "mapping" in category:
				if sku_mapping_test(session, exp_pidlist, serialnum[0]):
                                	logging.info("It's successful to verify mapping between SKU %s and Eng-Productids %s.\n"%(sku, eng_products))
                        	else:
                                	raise error.TestFail("Test Failed - Faild to verify mapping between SKU %s and Eng Productid(s) %s.\n" %(sku, eng_products))
			elif "sku_attribute_test" in category:
					if sku_mapping_test(session, exp_pidlist, serialnum[0]):
						logging.info("It's successful to do mapping test for SKU %s.\n"% sku)
					else:
						logging.error("Test Failed - Failed to do mapping test for SKU %s due to Eng Productid(s) not match.\n" % sku)
						test_result = False
					return (test_result,test_result_pool)
	except Exception, e:
		if "attributes" in category:
			file_attribute = open(regression_attribute_result_path, "a")
                        file_attribute.write("tc_SKU_" + sku + " ")
                        file_attribute.close
		elif "mapping" in category:
			file_attribute = open(regression_mapping_result_path, "a")
                        file_attribute.write("tc_SKU_" + sku + " ")
                        file_attribute.close

		logging.error(str(e))
		raise error.TestFail("Test Failed - error happened when do sku testing:"+str(e))
	finally:
		#if runcasein == 'guest' or ppc_s390_flag == 1:
		#	eu().sub_unregister(session)
		logging.info("+++++++++++++++'%s'- End to Run SKU Test +++++++++++++++\n" % sku)

