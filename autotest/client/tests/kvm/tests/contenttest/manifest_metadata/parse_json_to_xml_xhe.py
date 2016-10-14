#!/usr/bin/python
import os
import sys
import json
import shutil
import logging
from optparse import OptionParser
from kobo.rpmlib import parse_nvra
from xml.dom import minidom

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
    print '    #python parse_format_json.py [json file] [output xml file]'
    print 'Modify Record: '
    print '    2012-03-21 Create xhe@redhat.com'
    print '    2012-06-21 Update xhe@redhat.com : generate xml file'
    print ''
    print '############################################'
    print '\n'

def usages():
    print '[Usage]:'
    print '    python parse_format_json.py /tmp/export.json '
    print '    python parse_format_json.py /tmp/export.json /home/output.xml'
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
	 if len(args) == 2:
             output_xml_file=args[1]
	 else:
	     output_xml_file='./manifest.xml'
except Exception,e:
     logging.error(str(e))
     print("Error - Missing .json file ,exit process.")

welcome_infor()
# Get json dir path,set it as output directory
print 'ready to create file output_xml_file : %s' %output_xml_file
print 'Ready to load json file%s' %target_json

try:
     #load target file
     data=json.load(open(target_json,'r'))
     print 'Data type is %s' %type(data)
except Exception,e:
     logging.error(str(e))
     print("Error - Load .json file failed when running json.load() function.")
try:
     # XML - create a Dom object
     impl=minidom.getDOMImplementation()
     dom=impl.createDocument(None,'rhel',None)
     root=dom.documentElement

     # Get Dict content 
     for oneDict in data:
         # Get items from Product ID lists
         if isinstance(oneDict.keys(),list):
             # Dict Key list['RHN Channels','Product ID' ,'Basearch','Name']
             items_len= len(oneDict)
             # Get product id keys and values

             product_id_key=oneDict.keys()[1]
             product_id_value= oneDict.values()[1]
     	     # Get product Name 
	     product_name=oneDict.keys()[3]
	     product_name_value=oneDict.values()[3]
		
	     # Get basearch values
             product_basearch=oneDict.values()[2]

	     # XML - create Elements tag = productid 
	     productid_item=dom.createElement('productid')
	     # XML - set tag attributes for tag productid 
	     productid_item.setAttribute('name',product_name_value)

	     if product_id_value:
	     	productid_item.setAttribute('value',str(product_id_value))
	     else:
	     	productid_item.setAttribute('value',product_name_value)
	     
	     # XML - add child item for root	    
	     root.appendChild(productid_item)

             if isinstance(product_basearch,list) == True:
                  #print '====  List Arch ====\n'
                  for val in product_basearch:
                     #print 'Dict len = %d' %len(val)
                     arch_value=val['Label']
                     node_name='%s_%s' %(product_id_value,arch_value)

		     # XML - create Element tag = arch
		     arch_item=dom.createElement('arch')
		     arch_item.setAttribute('value',arch_value)
		     
		     #XML - add child element arch_item for productid_item
		     productid_item.appendChild(arch_item)

                     # Delete Lable item from Dict
                     val.pop('Label')

                     # Get repoid list from clipping Dict
                     for repo_item in val.items():
                         repoid_name=repo_item[0]
 		        
		         # XML - create Element tag = repoid
		         repoid_item=dom.createElement('repoid')
		         repoid_item.setAttribute('value',repoid_name)
		     
		         # XML - add child ele for arch_item
		         arch_item.appendChild(repoid_item)

                         # Get repo items values from dict
                         if isinstance(repo_item[1],dict)==True:
                             infolist=repo_item[1].values()
		             for m in infolist:
		                if m:				    
		                    if '.rpm' in m[0]:
		                       # XML - create Element tag = packagename
		                       packagename_item=dom.createElement('packagename')
		            	       for p in m:
		                   	   rpm_dir = parse_nvra(p)
                            	   	   wline = "%s %s %s %s"%(rpm_dir['name'], rpm_dir['version'], rpm_dir['release'], rpm_dir['arch'])
		                   	   packagename_text=dom.createTextNode(wline)
		                   	   packagename_item.appendChild(packagename_text)
		                       repoid_item.appendChild(packagename_item)
		                    else:
                                       # XML - create Element tag = relativeurl
                                       relativeurl_item=dom.createElement('relativeurl')
		            	       for r in m:
                                           relativeurl_text=dom.createTextNode(r)
                                       	   relativeurl_item.appendChild(relativeurl_text)
                                       repoid_item.appendChild(relativeurl_item)

     #print root.toprettyxml()
     print 'write XML file %s' %output_xml_file
     f=file(output_xml_file,'w')
     dom.writexml(f,addindent=' '*4,newl='\n',encoding='utf-8')
     f.close()
except Exception,e:
     logging.error(str(e))
     print("Error - Parse json file failed after loading .")

print '* Successfully Finished!'
print '* Please check the output directory: %s\n\n' %(output_xml_file)

