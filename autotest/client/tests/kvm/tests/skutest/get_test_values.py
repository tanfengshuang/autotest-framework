#!/usr/bin/python

import os
import sys
import json
import shutil
import logging
from optparse import OptionParser
import codecs
import time

########### target test values ###################
#id 
#multiplier 
#attributes:product_family 
#attributes:sockets 
#attributes:description 
#attributes:option_code 
#attributes:support_type
#attributes:arch
#attributes:type
#attributes:name
#attributes:virt_limit
#attributes:support_level
#attributes:variant
#attributes:vcpus
#attributes:required_type
#attributes:management_enabled
#attributes:support_level
#attributes:enabled_consumer_type
#attributes:virt-only
################################

def get_local_time():
	timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
	return timestr

def create_dirs(dirpath):
	if os.path.isdir(dirpath) == True :
		logging.info( '\r\n* Delete the old directory : %s' % dirpath)
		shutil.rmtree(dirpath)
	logging.info( "* Create directory : %s" % dirpath)
	os.makedirs(dirpath)

def is_in_list(mylist, tgstr):
	for i in mylist:
		if i == tgstr:
			return True   
	return False

def getChild(sku, obj, depth):

	depth = depth + 1
	logging.info( '* Current layer depth = %d' % depth)
	if isinstance(obj, list):
        	logging.info( '* Target object is list')
        	objLst = len(obj)
        	if objLst:
			for i in obj:
			    getChild(i, depth)
        	else:
        	    logging.error( '*List is empty!' )

	if isinstance(obj, dict):
		logging.info( '* Target object is dict')
		mydict = {}
		keyNum = len(obj.keys())
		logging.info("There are %s atrributes got from Candlepin." % keyNum)
		logging.info("The atrributes got from Candlepin are %s." % obj.keys())

		for i in range(0, keyNum):
			Dkey = obj.values()[i]
			
			if obj.keys()[i] == 'id' or obj.keys()[i] == 'multiplier':
				mydict[obj.keys()[i]] = obj.values()[i]
				logging.info('Test data got from Candlepin: %s = %s\n' %(obj.keys()[i], Dkey))
			else:
				if obj.keys()[i]=='attributes':
					# attributes contains lists
					for one in obj.values()[i]:
						mydict[one.values()[0]] = one.values()[1]
						logging.info('Test data got from Candlepin: %s = %s\n' % (one.values()[0], one.values()[1]))
		return mydict
    
def get_test_values(sku, target_read_sku_dir):
	
	target_sku_files = os.listdir(target_read_sku_dir)     
	target_json_file_path = os.path.join(target_read_sku_dir, sku)
	
	#load target file of sku attributes
	logging.info( '\n* Ready to load file %s... ' % target_json_file_path)
	data = json.load(open(target_json_file_path, 'r'))
	#logging.info( '* Data type is %s' % type(data))

	#logging.info( '* Parse the json file %s ...' % target_json_file_path)
	mdict=getChild(sku, data, 0)
	'''
	if len(mdict) > 0:
		logging.info("It's successful to get %s attribute values." % sku)
	else:
		logging.error("Failed to get %s attribute values." % sku)
	'''
	#print mdict
	return mdict 

#get_test_values('MCT0915','/tmp/sku_download')
