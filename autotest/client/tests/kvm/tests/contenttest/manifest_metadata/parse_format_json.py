#!/usr/bin/python
import os
import sys
import json
import shutil
import logging
from optparse import OptionParser
from kobo.rpmlib import parse_nvra

def welcome_infor():
    print '\n\n\n'
    print '####### Welcome Auto-Parse-Format-Json V 0.1 ######'
    print ''
    print 'Name: parse_format_json.py'
    print 'Version: V0.1'
    print 'Create Data: 2012-03-21'
    print 'Project: Entitlement/ContentTest'
    print 'Description:'
    print '    Parse and format json to target form as follow:'
    print '${pid}_${arch}/    .......................>[type=Directory]'
    print '     |___${repoid}.txt  ..................>[type=File]'
    print '     |       |__${repourl}................>[type=String]'
    print '     |       |__${pkgname}................>[type=String]'
    print '     |___${repoid}.txt '
    print '     |       |__${repourl}' 
    print '     |       |__${pkgname} '
    print '     |___${repoid}.txt'
    print '             |__${repourl}' 
    print '             |__${pkgname}'
    print '    ./parse_format_json.py /usr/local/tmp/my.json'
    print 'Modify Record: '
    print '    2012-03-21 Create xhe@redhat.com'
    print ''
    print '############################################'
    print '\n'

def usages():
    print '[Usage]:'
    print '    python./parse_format_json.py /usr/local/tmp/my.json'
    print '\n'

def create_dirs(dirpath):
     if os.path.isdir(dirpath) == True:
          print '\r\n* Delete the old directory : %s' %dirpath
          shutil.rmtree(dirpath)
     print "* Create directory : %s" %dirpath
     os.makedirs(dirpath)

def writeFiles(filepath,ilist):
    print type(ilist)
    wt_file=open(filepath,'w')
    for info in ilist:
        #print 'info type is %s' %(type(info))
        for line in info:
            if "rpm" in line:
                rpm_dir = parse_nvra(line)
                wline = "%s %s %s %s\r\n"%(rpm_dir['name'], rpm_dir['version'], rpm_dir['release'], rpm_dir['arch'])   
            else:
                wline='%s\r\n' %line

            wt_file.writelines(wline)
    wt_file.close
    print '\r\n* Close file handle.'


try:
    # Get json file path
     parser=OptionParser()
     (options,args)=parser.parse_args()
     if len(args) == 0:
         print "* Exit! Missing json file."
         usages()
         exit(1)
     else:
         target_json=args[0]
         output_dir=args[1]         
except Exception,e:
     logging.error(str(e))
     print("Error - Missing .json file ,exit process.")

welcome_infor()
# Get json dir path,set it as output directory
print 'outputdir=%s' %output_dir
#target_json="/home/fedora16/myscripts/parsejsons/packagemanifest_format.json"
print 'Ready to load json file%s' %target_json

try:
     #load target file
     data=json.load(open(target_json,'r'))
     print 'Data type is %s' %type(data)
except Exception,e:
     logging.error(str(e))
     print("Error - Load .json file failed when running json.load() function.")
try:
     # Get Dict content 
     for oneDict in data:
         print '==============List Product ==================='
         # Get items from Product ID lists
         if isinstance(oneDict.keys(),list):
             ##old-- Get items['RHN Channels','Basearch','Product ID','Compose','Name']
             # Get items['RHN Channels','Product ID' ,'Basearch','Name']

             items_len= len(oneDict)
             # Get product id keys and values 
             product_id_key=oneDict.keys()[1]
             product_id_value= oneDict.values()[1]
             # Get basearch values
             product_basearch=oneDict.values()[2]
             print type(product_basearch)

             if isinstance(product_basearch,list) == True:
     
                  print '====  List Arch ====\n'
                  for val in product_basearch:
             #        print 'val type=%s' %type(val)
                     if isinstance(val,list):
                         print len(val)
                         print val 
                     elif isinstance(val,dict):
                         print 'Dict len = %d' %len(val)
                         arch_value=val['Label']
                         node_name='%s_%s' %(product_id_value,arch_value)
                         node_path=os.path.join(output_dir,node_name)
                         print node_path
                         create_dirs(node_path)
                         # Delete Lable item from Dict
                         val.pop('Label')

                         # Get repoid list from clipping Dict
                         for repo_item in val.items():
                             repoid_name=repo_item[0]
                             # print repoid_name
                             # Format txt file path
                             txt_file_path='%s/%s.txt' %(node_path,repoid_name)
                             print '\r\n* Write to file:%s' %txt_file_path
                             # Get repo items values from dict
                             if isinstance(repo_item[1],dict)==True:
                                 print type(repo_item[1].values())
                                 print repo_item[1].values()
                                 infolist=repo_item[1].values()
                                 writeFiles(txt_file_path,infolist) 
                             print '\n'

except Exception,e:
     logging.error(str(e))
     print("Error - Parse json file failed after loading .")

print '* Successfully Finished!'
print '* Please check the output directory: %s\n\n' %(output_dir)

