#!/usr/bin/python 
import os
import sys
import shutil
import logging
import commands,time
from autotest_lib.client.common_lib import error

# create dirs
def create_dirs(dirpath):
     if os.path.isdir(dirpath) != True:
     	logging.info("Create directory : %s" %dirpath)
     	os.makedirs(dirpath)

def get_reference_list():
	auto_client_path = os.environ['AUTODIR']
	reference_doc_path = os.path.join(auto_client_path, "tests/kvm/tests/skutest/Reference_standard.txt")
	#reference_doc_path = "/usr/local/staf/test/Entitlement/entitlement-autotest/autotest/client/tests/kvm/tests/skutest/Reference_standard.txt" 

        file = open(reference_doc_path)
        lists = eval(file.read())
	return lists

def get_sku_list_from_reference():
        lists = get_reference_list()
	sku_list = []

        for dict in lists:
                sku = dict['SKU']
                if sku not in sku_list:
                        sku_list.append(sku)

        return sku_list

def get_sku_pass_list_from_file():
        doc_path = "/tmp/sku_download/sku_download_pass.txt"

        file = open(doc_path)
        lists = eval(file.read())

        return lists

def get_stage_account_from_reference(sku):
	lists = get_reference_list()
	stage_account_list = []

	for dict in lists:
		if dict['SKU'] == sku:
			stage_account = dict['Username']
			return stage_account

def curl_attributes(username, password, prod_url, skuName, download_sku_path):
	cmdstr = 'curl -u %s:%s -k %s%s|python -mjson.tool>%s' %(username, password, prod_url, skuName, download_sku_path)
	logging.info(cmdstr)
	ret,output = commands.getstatusoutput(cmdstr)
	i = 0
	
	while i < 5 and ret != 0:
		time.sleep(10)
		ret,output = commands.getstatusoutput(cmdstr)
		i+=1

	logging.info(output)
	if ret != 0:
        	logging.error('Error: download failed!Exit')

def download_all_skus(session, params, prod_url,download_sku_dir,password):
	return_value=True
    	create_dirs(download_sku_dir)
	logging.info("++++++++++++++++++Begin to download attributes for the sku++++++++++++++++++")
	sku_param = params.get("sku")
	if sku_param == None:
        	sku_all_list = get_sku_list_from_reference()
        else:
        	sku_all_list = sku_param.split(',')

	#use sku_pass_list and sku_fail_list to judge which skus are downloaded successfully/failed
	sku_pass_list = []
	sku_fail_list = []
                
   	for sku in sku_all_list:
    		skuName=sku
    		dOutput='Download %s attributes...' %(skuName)
    		logging.info(dOutput)
    		download_sku_path='%s/%s' %(download_sku_dir,skuName)
    		if os.path.isfile(download_sku_path):
        		logging.info('Found  the old file %s' %download_sku_path)
        		logging.info('Remove the old file %s' %download_sku_path)
        		os.remove(download_sku_path)
	
		username = get_stage_account_from_reference(sku)
    		try:
            		curl_attributes(username, password, prod_url, skuName, download_sku_path)
			
			return_value = False
			
        		# No sku attributes data in CDN server.
        		if os.path.getsize(download_sku_path) <= 200:
            			skufile=file(download_sku_path,'r')
            		# read the downloaded sku file,search the failed string 
            			for i in skufile.readlines():
                	 		print i
                 			findStr='Product with UUID \'%s\' could not be found'  %skuName
                 			invalid_str='Invalid username or password'
                 			if i.find(findStr)>=0 or i.find(invalid_str)>=0:
                     				failedStr='%s' %i.replace('    ','')
                     				logging.info(failedStr)
                     				return_value=False
            			skufile.close()
        		else:
            			return_value=True 
    		except Exception,e:
        		logging.error(str(e))
        		logging.info('%s:DownLoad Error- ' %skuName)
        		return_value=False

    		if return_value:
			sku_pass_list.append(skuName)
        		logging.info('Download %s attributes --- PASS\n' % skuName) 
    		else:
        		#raise error.TestFail('"%s" Validate SKUs list availability --- FAIL'%skuName)
			sku_fail_list.append(skuName)
			logging.error('Download %s attributes --- FAIL\n' % skuName)
			if os.path.exists(download_sku_path) and os.path.isfile(download_sku_path):
	    			os.remove(download_sku_path)
	    			logging.info('clean %s' %download_sku_path)

    	logging.info('Please check download direcotry: %s\n' %download_sku_dir)

	#write the sku_pass_list to /tmp/sku_download
        sku_download_pass_path='%s/sku_download_pass.txt' % download_sku_dir
        if os.path.isfile(sku_download_pass_path):
                os.remove(sku_download_pass_path)
        f = file(sku_download_pass_path, 'w')
        str = "%s" % sku_pass_list
        f.write(str)
        f.close

	#print the failed skus
	if sku_fail_list == []:
		logging.info('It is successful to download all the skus!')
	else:
		raise error.TestFail('Failed to download the following skus: %s' % sku_fail_list)
	logging.info("Download pass list: %s" % sku_pass_list)
    	logging.info('++++++++++++++++++End to download the attributes for all the skus+++++++++++++++++++')
	
	
	

#download_all_skus('https://subscription.rhn.stage.redhat.com/subscription/products/','/tmp/sku_download','redhat')
