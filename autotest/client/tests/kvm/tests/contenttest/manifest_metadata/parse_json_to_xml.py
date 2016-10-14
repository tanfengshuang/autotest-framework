#!/usr/bin/python
import os
import re
import sys
import json
import logging
from optparse import OptionParser
from kobo.rpmlib import parse_nvra
from xml.dom import minidom

def welcome_infor():
	print '\n\n\n'
	print '####### Welcome Auto-Parse-Format-Json V 1.2 ######'
	print ''
	print 'Name: parse_json_to_xml.py'
	print 'Version: V1.2'
	print 'Create Data: 2012-07-23'
	print 'Project: Entitlement/ContentTest'
	print 'Description:'
	print '    For detailed usage, please refer to usages()'
	print 'Modify Record: '
	print '    2012-07-23 Create suli@redhat.com'
	print '    2012-07-23 Update suli@redhat.com : generate xml file'
	print '    2014-03-14 Update ftan@redhat.com : generate xml file for rhn and cdn'	
	print ''
	print '############################################'
	print '\n'

def usages():
	print '[Usage]:'
	print '    Parse manifest for RHN and CDN: '
	print '			python parse_json_to_xml.py /tmp/export.json  --> generate file rhn_manifest.xml and cdn_manifest.xml'
	print ''
	print '    Parse manifest for RHN: '
	print '			python parse_json_to_xml.py /tmp/export.json rhn  --> generate rhn xml rhel_manifest.xml'
	print '			python parse_json_to_xml.py /tmp/export.json /home/output.xml rhn'
	print ''
	print '    Parse manifest for CDN: '
	print '			python parse_json_to_xml.py /tmp/export.json cdn  --> generate cdn xml rhel_manifest.xml'
	print '			python parse_json_to_xml.py /tmp/export.json /home/output.xml cdn'
	print '\n'


def parse_json_to_xml():
	try:
		# Get json file path
		parser = OptionParser()
		(options, args) = parser.parse_args()

		if len(args) == 0:
			usages()
			exit(1)
		else:
			welcome_infor()

			target_json = args[0]
			if os.path.exists(target_json) == False:
				print "Json file %s doesn't exist, please check!\n\n" % target_json
				exit(1)

			if len(args) == 2:
				if re.match("cdn", args[1], re.I) != None:
					cdn_xml_file = './cdn_manifest.xml'
					parse_json_cdn(target_json, cdn_xml_file)
				elif re.match("rhn", args[1], re.I) != None:
					rhn_xml_file = './rhn_manifest.xml'
					parse_json_rhn(target_json, rhn_xml_file)
				else:
					usages()
					exit(1)
				
			elif len(args) == 3:
				if re.match("cdn", args[2], re.I) != None:
					cdn_xml_file = args[1]
					parse_json_cdn(target_json, cdn_xml_file)
				elif re.match("rhn", args[2], re.I) != None:
					rhn_xml_file = args[1]
					parse_json_rhn(target_json, rhn_xml_file)
				else:
					usages()
					exit(1)
			else:
				rhn_xml_file = './rhn_manifest.xml'
				cdn_xml_file = './cdn_manifest.xml'
				parse_json_cdn(target_json, cdn_xml_file)
				parse_json_rhn(target_json, rhn_xml_file)
	except Exception, e:
		logging.error(str(e))
		print("Error - Missing .json file, exit process.")
	
def load_json(target_json):
	# Get json dir path,set it as output directory
	print 'Ready to load json file %s' % target_json
	try:
		#load target file
		data_list = json.load(open(target_json, 'r'))
		print 'Data type is %s' % type(data_list)
		return data_list
	except Exception,e:
		logging.error(str(e))
		print("Error - Load .json file failed when running json.load() function.")
	
def parse_json_rhn(target_json, rhn_xml_file):
	data_list = load_json(target_json)
	try:
		# XML - create a Dom object
		impl = minidom.getDOMImplementation()
		dom = impl.createDocument(None, 'rhel', None)
		root = dom.documentElement
		
		# Get Dict content
		if isinstance(data_list,list) == False:
			data_list = [data_list]
	
		for data in data_list:
		# Dict Key list['cdn','Compose' ,'rhn']
			rhn_data = rhn_data = data["rhn"]["channels"]
		 
			if isinstance(rhn_data.keys(), list) == False:
				raise error.TestFail("Failed to get content from package manifest.")		
	
			# Prepare to analyze manifest of rhn part
			for key in rhn_data.keys():
				# XML - create Elements tag = repoid
				repoid_item = dom.createElement('repoid')
				repoid_item.setAttribute('value', str(key))
				# XML - add child Element for repoid_item
				root.appendChild(repoid_item)
	
				# XML - create Elements tag = packagename
				if isinstance(rhn_data[key], list) == True and len (rhn_data[key]) > 0:
					packagename_item=dom.createElement('packagename')
					for rpm in rhn_data[key]:
						rpm_fmt = parse_nvra(rpm)
						wline = "%s %s %s %s"%(rpm_fmt['name'], rpm_fmt['version'], rpm_fmt['release'], rpm_fmt['arch'])
						packagename_text = dom.createTextNode(wline)
						packagename_item.appendChild(packagename_text)
					# XML - add child Element for packagename_item
					repoid_item.appendChild(packagename_item)

		print 'write RHN XML file %s' % rhn_xml_file
		f = file(rhn_xml_file, 'w')
		dom.writexml(f, addindent = ' '*4, newl='\n', encoding = 'utf-8')
		f.close()
		     
	except Exception,e:
	     logging.error(str(e))
	     print("Error - Parse json file failed after loading .")
	
	print '* Finished to generate rhn xml file successfully!'
	print '* Please check the output directory: %s\n\n' % (rhn_xml_file)

def parse_json_cdn(target_json, cdn_xml_file):
	data_list = load_json(target_json)
	try:
		# XML - create a Dom object
		impl = minidom.getDOMImplementation()
		dom = impl.createDocument(None, 'rhel', None)
		root = dom.documentElement
		
		# Get Dict content
		if isinstance(data_list,list) == False:
			data_list = [data_list]
	
		for data in data_list:
		# Dict Key list['cdn','Compose' ,'rhn']
			cdn_data = data["cdn"]["products"]
		 
			if isinstance(cdn_data.keys(), list) == False:
				raise error.TestFail("Failed to get content from package manifest.")		
	
			# Prepare to analyze manifest of cdn part
			# Get items from Product ID lists
			for key in cdn_data.keys():
				oneDict = cdn_data[key]
				product_id_value = oneDict["Product ID"]
				product_name_value = oneDict["Name"]
				platform_value = oneDict["Platform"]
				if oneDict["Platform Version"] != None and "Platform Version" in oneDict.keys():
					platform_version_value = oneDict["Platform Version"]
				product_version_value = oneDict["Product Version"]
				repo_paths_value = oneDict["Repo Paths"]
				
				# XML - create Elements tag = productid 
				productid_item = dom.createElement('productid')
				# XML - set tag attributes for tag productid 
				if product_id_value:
					productid_item.setAttribute('value', str(product_id_value))
				else:
					productid_item.setAttribute('value', product_name_value)
	
				productid_item.setAttribute('name', product_name_value)
				productid_item.setAttribute('platform', platform_value)
				if oneDict["Platform Version"] != None and "Platform Version" in oneDict.keys():
					productid_item.setAttribute('platform_version', platform_version_value)
				productid_item.setAttribute('product_version', product_version_value)
				
				# XML - add child item for root	    
				root.appendChild(productid_item)
		
				if isinstance(repo_paths_value.keys(),list) == True:
					# Json parse: add all repo_data in different arch lists
					basearch_list = []
					basearch_dict = {}
					for key in repo_paths_value.keys():
						basearch_value = repo_paths_value[key]["basearch"]
						
						if basearch_value not in basearch_list:
							basearch_dict[basearch_value] = []
							basearch_list.append(basearch_value)
	
						repo_paths_value[key]["relativeurl"] = key
						basearch_dict[basearch_value].append(repo_paths_value[key])
	
	
					for basearch_value in basearch_list:
						# XML - create Element tag = arch
						arch_item = dom.createElement('arch')
						arch_item.setAttribute('value', basearch_value)
	
						#XML - add child element arch_item for productid_item
						productid_item.appendChild(arch_item)
	
						for repo_dict in basearch_dict[basearch_value]:
							# XML - create Element tag = repoid
							repoid_item = dom.createElement('repoid')
							repoid_name = repo_dict["Label"]
							repoid_item.setAttribute('value', repoid_name)	
							if "releasever" in repo_dict.keys():
								releasever = repo_dict['releasever']
								repoid_item.setAttribute('releasever', releasever)	
							# XML - add child Element for arch_item
							arch_item.appendChild(repoid_item)
	
							# XML - create Element tag = relativeurl
							relativeurl_item = dom.createElement('relativeurl')
							relativeurl = repo_dict["relativeurl"]
							relativeurl_text = dom.createTextNode(relativeurl)
							relativeurl_item.appendChild(relativeurl_text)
							# XML - add child Element for relativeurl_item
							repoid_item.appendChild(relativeurl_item)
		
							# Json parse: parse each rpm with format %{name} %{version} %{release} %{arch}
							if isinstance(repo_dict["RPMs"], list) == True and len (repo_dict["RPMs"]) > 0:
								# XML - create Element tag = packagename
								packagename_item = dom.createElement('packagename')
								for rpm_pkg in repo_dict["RPMs"]:
									rpm_fmt = parse_nvra(rpm_pkg)
									wline = "%s %s %s %s"%(rpm_fmt['name'], rpm_fmt['version'], rpm_fmt['release'], rpm_fmt['arch'])								
									packagename_text = dom.createTextNode(wline)
									packagename_item.appendChild(packagename_text)
	
								# XML - add child Element for packagename_item
								repoid_item.appendChild(packagename_item)
	
		print 'write CDN XML file %s' % cdn_xml_file
		f = file(cdn_xml_file, 'w')
		dom.writexml(f, addindent = ' '*4, newl='\n', encoding = 'utf-8')
		f.close()
		     
	except Exception,e:
	     logging.error(str(e))
	     print("Error - Parse json file failed after loading .")
	
	print '* Finished to generate cdn xml file successfully!'
	print '* Please check the output directory: %s\n\n' % (cdn_xml_file)


if __name__ == '__main__':
	parse_json_to_xml()	





