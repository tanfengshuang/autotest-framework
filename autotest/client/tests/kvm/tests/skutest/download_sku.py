#!/usr/bin/python 
import os
import sys
import shutil
import logging
import commands
from autotest_lib.client.common_lib import error

# create dirs
def create_dirs(dirpath):
     if os.path.isdir(dirpath) == True:
          logging.info ('Delete the old directory : %s' %dirpath)
          shutil.rmtree(dirpath)
     logging.info("Create directory : %s" %dirpath)
     os.makedirs(dirpath)

# get the valid sku in sku-list.conf
def get_file_valid_lines(tgfile,invalid_str):
    valid_lines=0
    try:
        f=open(tgfile,'r')
    except Exception,e:
        logging.error(str(e))
        logging.info('Opened file failed')
    for line in f.readlines():
        if line.find(invalid_str)>=0:
            continue
        else:
            valid_lines=valid_lines+1
    f.close()
    return  valid_lines
def usages():
    logging.info('[Usage]:python download_sku.py <sku_id> <product_url> <download_dir> <username> <password>')
    logging.info('  [ sku_id  ]   :     target sku id .')
    logging.info('  [ download_dir ]   : the download directory of sku attributes.one sku one file.')
    logging.info('  [ username     ]   : the username of download CDN server'  )
    logging.info('  [ password     ]   : the password of download CDN server')
    logging.info('  [ product_url  ]   : the product url from CDN '  )
    logging.info('[Example]:')
    logging.info('download_sku.py RH1213377 https://subscription.rhn.stage.redhat.com/subscription/products/ /tmp/dldsku stage_test_5 redhat')
    logging.info('\n')
def download_sku(sku_id,prod_url,download_sku_dir,username,password):
    return_value=True
    create_dirs(download_sku_dir)
    skuName=sku_id
    dOutput='Download %s attributes...' %(skuName)
    logging.info('**************** Start Step1: Validate SKUs list availability. ****************')
    logging.info(dOutput)
    download_sku_path='%s/%s' %(download_sku_dir,skuName)
    if os.path.isfile(download_sku_path):
        logging.info('Fount  the old file %s' %download_sku_path)
        logging.info('Remove the old file %s' %download_sku_path)
        os.remove(download_sku_path)

    cmdstr='curl -u %s:%s -k %s%s|python -mjson.tool>%s' %(username,password,prod_url,skuName,download_sku_path)
    logging.info(cmdstr)
    try:
        ret,output=commands.getstatusoutput(cmdstr)
	if ret == 0:
	    logging.info(output)
	else:
	    logging.info(output)
            logging.info('Error: download failed!Exit')
            #logging.info('* Validate SKUs list availability --- FAIL\n')
            raise error.TestFail('* Validate SKUs list availability --- FAIL\n')
            logging.info('**************** End Step1: Validate SKUs list availability. ****************')
            return_value=False
	    return return_value 

        skufilePath=os.path.join(download_sku_dir,skuName)
        # No sku attributes data in CDN server.
        if os.path.getsize(skufilePath) <=150:
            skufile=file(skufilePath,'r')
            # read the downloaded sku file,search the failed string 
            for i in skufile.readlines():
                 print i
                 findStr='Product with UUID \'%s\' could not be found'  %skuName
                 invalid_str='Invalid username or password.'
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
        logging.info('"%s" Validate SKUs list availability --- PASS' %skuName) 
    else:
        raise error.TestFail('"%s" Validate SKUs list availability --- FAIL'%skuName)
        if os.path.isfile(download_sku_path):
            os.remove(skufilePath)
            logging.info('clean %s' %skufilePath)
    logging.info('**************** End Step1: Validate SKUs list availability.')
    logging.info('Please check download direcotry: %s\n' %download_sku_dir)
    return return_value

#download_sku('RH1213377','https://subscription.rhn.stage.redhat.com/subscription/products/','/tmp/sku_download','stage_test_5','redhat')
