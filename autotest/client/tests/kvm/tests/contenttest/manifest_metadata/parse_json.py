#!/usr/bin/python
import os
import sys
import json
import urllib2
import difflib
import shutil
import time
import logging
from optparse import OptionParser

def welcome_infor():
    print '\n\n\n'
    print '####### Welcome Auto-Parse-Json V 0.1 ######'
    print ''
    print 'Name: parse_json.py'
    print 'Version: V0.1'
    print 'Create Data: 2012-02-07'
    print 'Project: Entitlement'   
    print 'Description:'
    print '    Parse the json file(git://git.app.eng.bos.redhat.com/rcm/rhn-definitions.git)'
    print '    and output the result.'
    print '[Usages]: parse_json.py [opt] [directory]'
    print '[opt]'
    print '  -n  get Name information set True,or False.Default [True]'
    print '  -i  get Product_ID information set True,or False.Default [True]'
    print '  -c  get RHN_Channels information set True,or False.Default [True]'
    print '  -s  get Content_Sets information set True,or False.Default [True]'
    print '  -l  get Label information set True,or False.Default [True]'
    print '  -r  get Repos information is True,or False.Default [True]'
    print '  -b  get Relative_URL information set True,or False.Default [True]'
    print '  -t  show All Tilte set True,or False.Default [False]'
    print '[directory]'
    print '  Output directory,the Default /tmp'
    print 'Simple Usage:'
    print '    ./parse_json ' 
    print 'Modify Record: '
    print '    2012-02-07 Create xhe@redhat.com'
    print ''
    print '############################################'
    print '\n'

def usage_print(key,value):
    print 'Get %s information: [ %s ]' %(key,value)

def ready_output_dir(odir):
    if os.path.isdir(odir) == True:
        print 'Delete directory:%s.' %(odir)
        shutil.rmtree(odir)
    print 'Create directory:%s.\n' %(odir)
    os.mkdir(odir)

def xhe_output(string,Bool,FHdr):
    if Bool == True:
        print string
        FHdr.write(string)

def format_one_str(string,tbool):
    if tbool==True:
        re='    %s:\n' %(string)
    else:
        re=''
    return re

def format_one_title(string,tbool):
    if tbool==True:
        re='%s:\n' %(string)
    else:
        re=''
    return re

def format_two_str(string1,string2,tbool):
    if tbool==True:
        re='    %s:%s\n' %(string1,string2)
    else:
        re='    %s\n' %(string2)
    return re

def format_two_title(string1,string2,tbool):
    if tbool==True:
        re='%s:%s\n' %(string1,string2)
    else:
        re='%s\n'  %(string2)
    return re

def format_bot_title(string1,string2,tbool):
    if tbool==True:
       re='        %s:%s\n' %(string1,string2)
    else:
       re='        %s\n' %(string2)
    return re
    
def debug_infor(string):
    cur_time=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    print '%s[ DEBUG ]: %s' %(cur_time,string)

def clean_dir(directory):
    if os.path.isdir(directory) == True:
        print 'Clean directory:%s.' %(directory)
        shutil.rmtree(directory)
parser=OptionParser(version='0.1')
parser.add_option("-n",dest="Name",default=True,
           help=" Get Name information set 'True',or 'False'.Default[True]")
parser.add_option("-i",dest="Product_ID",default=True,
           help=" Get Product_ID information set 'True',or 'False'.Default[True]")
parser.add_option("-c",dest="RHN_Channels",default=True,
           help=" Get RHN_Channels information set 'True',or 'False'.Default[True]")
parser.add_option("-s",dest="Content_Sets",default=True,
           help=" Get Content_Sets information set 'True',or 'False'.Default[True]")
parser.add_option("-l",dest="Label",default=True,
           help=" Get Label information set 'True',or 'False'.Default[True]")
parser.add_option("-r",dest="Repos",default=True,
           help=" Get Repos information set True,or False.Default[True]")
parser.add_option("-b",dest="Relative_URL",default=True,
           help=" Get Relative_URL information set 'True',or 'False'.Default[True]")
parser.add_option("-t",dest="Show_All_Title",default=False,
           help=" Show All Tilte set 'True',or False.Default[False]")
(options,args)=parser.parse_args()
if len(args)==0:
    output_dir='/tmp'
    print 'Output directory : /tmp'
else:
    output_dir=args[0]
    print 'Output directory : %s' %output_dir 
 
#print welcome infor
welcome_infor()

#print usage list
print "========== Print  Information========"
usage_print('Name',options.Name)
usage_print('Product_ID',options.Product_ID)
usage_print('RHN_Channels',options.RHN_Channels)
usage_print('Content_Sets',options.Content_Sets)
usage_print('Label',options.Label)
usage_print('Repos',options.Repos)
usage_print('Relative_URL',options.Relative_URL)
usage_print('Show_All_Title',options.Show_All_Title)
print '\n'

#initalization root_nodes keys
root_node1='Name'
root_node2='Product ID'
root_node3='RHN Channels'
root_node4='Content Sets'
primary_node1='Label'
primary_node2='Repos'
bot_node='Relative URL'

# The sign variable
get_name_infor=options.Name 
get_id_infor=options.Product_ID
get_channel_infor=options.RHN_Channels
get_content_infor=options.Content_Sets
get_repos_infor=options.Repos
get_label_infor=options.Label
get_url_infor=options.Relative_URL
show_all_title=options.Show_All_Title

#Default 
#target_json='/home/fedora16/myscripts/workdir/product-baseline.json'
download_git='git://git.app.eng.bos.redhat.com/rcm/rhn-definitions.git'
rhn_name='rhn-definitions'
json_dir='cdn'
json_name='product-baseline.json'
#time_stamp=time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
#print time_stamp
#output_name='output%s' %(time_stamp)
#print output_name


#Get work directory
workdir=os.getcwd()
print workdir
#Get relation path
rhn_dir=os.path.join(workdir,rhn_name)
json_full_dir=os.path.join(rhn_dir,json_dir)
json_full_path=os.path.join(json_full_dir,json_name)
cd_wdir_cmd='cd %s' %(workdir)

#Format clone_cmd
clone_cmd='git clone %s' %(download_git)

#Run system command line
os.system(cd_wdir_cmd)

#Clean downlaod git directory
ready_output_dir(rhn_dir)

#Download git directory
os.system(clone_cmd)

target_json=json_full_path
#print target_json

#output_dir=os.path.join(workdir,output_name)

try:
    #load json file
    data=json.load(open(target_json,'r'))
except Exception,e:
     logging.error(str(e))
     debug_infor("Error - Load .json file failed when running json.load() function.")

#ready ouput directory
#ready_output_dir(output_dir)

#loop read json data structure
try:
    for val in data:
        # format root node information 
        root1_str=format_two_title(root_node1,val[root_node1],show_all_title)
        root2_str=format_two_title(root_node2,val[root_node2],show_all_title)
        root3_str=format_one_title(root_node3,show_all_title)
        list_rhn=val[root_node3]
    
        #open target file,ready to write
        filename='%s/%s.txt' %(output_dir,val[root_node2])
        debug_infor('Write Data to %s' %(filename))
        f=open(filename,"w")
    
        #target output
        xhe_output(root1_str,get_name_infor,f)
        xhe_output(root2_str,get_id_infor,f)   
        xhe_output(root3_str,get_channel_infor,f)
        for one in list_rhn:
            #channel list
            #debug_infor('----------Debug:get one type:%s' %(type(one)))
            #debug_infor('    %s' %(one))
            oneStr=format_one_str(one,show_all_title)
            xhe_output(oneStr,get_channel_infor,f)
    
        #target content title
        root4_title_str=format_one_title(root_node4,show_all_title)
        xhe_output(root4_title_str,get_content_infor,f)
      
        #loop read sub node data structure 
        for pri in val[root_node4]:
            #get items list,every obj is list.
            #debug_infor('Get pri.items type:%s' %(type(pri.items())))
            for lt in  pri.items():
                 #get everylist obj is tuple
                 #debug_infor('Get lt type:%s' %(type(lt)))
                 for everyTup in lt:
                     #debug_infor('Get everyTup type:%s' %(type(everyTup)))
                     ret=isinstance(everyTup,list)
                     if ret == True:
                         #everyTup is list type
                         for bot in everyTup:
                             #URL list infor(bot type is dict)
                             #debug_infor('        %s:%s'  %(bot_node,bot.values()))
                             xhe_output(format_bot_title(bot_node,bot.values(),show_all_title),get_url_infor,f)
                             #debug_infor('get bot type:%s' %(type(bot)))
                     else:
                         if everyTup == primary_node1:
                             pass
                         elif everyTup == primary_node2:
                             #Repos title
                             xhe_output(format_one_str(everyTup,show_all_title),get_repos_infor,f)
                         else:
                             #Label title and infor 
                             xhe_output(format_two_str(primary_node1,everyTup,show_all_title),get_label_infor,f)
         
        #print '\n'
        #closed every file after end write 
        f.close()
except Exception,e:
    logging.error(str(e))
    debug_infor("Error - parse the json structure.")
finally:
    logging.info("End of running parse_json.py")
    clean_dir(rhn_dir)
    print '========================'
    print '* Successfully Finished!'
    print '* Please check the output directory: %s\n\n' %(output_dir)
