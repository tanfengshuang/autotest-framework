import commands,re 
#from autotest_lib.client.tests.kvm.tests.ent_utils import ent_utils as eu

# Usage:
# set "hostname = subscription.rhn.redhat.com" in /etc/rhsm/rhsm.conf
# python get_productid_from_production_cdn.py 

def register(stage_name, stage_passwd):
	register_cmd = "subscription-manager register --username=%s --password=%s" %(stage_name, stage_passwd)
	(ret, output) = commands.getstatusoutput(register_cmd)
	print register_cmd
	if ret == 0:
		print "Successed to register the system!"
	else:
		print "Failed to register the system!"

def unregister():
	unregister_cmd = "subscription-manager unregister" 
        (ret, output) = commands.getstatusoutput(unregister_cmd)
	if ret == 0:
                print "Successed to unregister the system!"
        else:
                print "Failed to unregister the system!"
	
def get_sku_pool_dict():

	list_available_all_cmd = "subscription-manager list --available --all"
	(ret, output) = commands.getstatusoutput(list_available_all_cmd)
	if ret == 0:
		if "no available subscription pools to list" not in output.lower():
			pool_list = parse_listavailable_output(output)
			sku_list = []
                        pool_dict_of_sku = {}
			#print pool_list
			#print "="*20
			#print type(pool_list)
		
			for prd in pool_list:
				sku_list.append(prd['SKU'])
			sku_list = set(sku_list)

			for sku in sku_list:
				for prd in pool_list:
					if prd['SKU'] == sku:
						if "PoolID" in prd.keys():
							pool_dict_of_sku[sku] = prd['PoolID']
						elif "PoolId" in prd.keys():
							pool_dict_of_sku[sku] = prd['PoolId']
			#print sku_list
			#print pool_dict_of_sku
			return (sku_list, pool_dict_of_sku)	 
		else:
			print "Sorry, there is no subscription pools to list in the stage account %s." %stage_name
	else:
		print "Failed to list available all."

def subscribe(sku):
	pool_dict_of_sku = get_sku_pool_dict()
	#get the pool of sku from pool_dict_of_sku
	pool = pool_dict_of_sku[1][sku]
	
	subscribe_cmd = "subscription-manager subscribe --pool=%s" %pool
	(ret, output) = commands.getstatusoutput(subscribe_cmd)
	if ret == 0:
                print "Successed to subscribe the system using SKU : %s!" %sku
        else:
                print "Failed to subscribe the system using SKU : %s!" %sku
def unsubscribe():
	unsubscribe_cmd = "subscription-manager unsubscribe --all"
	(ret, output) = commands.getstatusoutput(unsubscribe_cmd)
        if ret == 0:
                print "Successed to unsubscribe the system."
        else:
                print "Failed to unsubscribe the system." 
	
def get_productids_from_entitlement_cert_with_rct():
        #get product_id list from entitlement cert in cert-3.0
	serialnumlist = get_subscription_serialnumlist()

        cmd = 'rct cat-cert /etc/pki/entitlement/%s.pem | grep -v "Stacking ID:"|grep -v "Pool ID"|grep "ID:"' %(serialnumlist[0])
        (ret, output) = commands.getstatusoutput(cmd)
        pidlist = []
        if ret == 0:
                #print 'It is successful to get productid from entitlement cert.'
                datalines = output.splitlines()
                for line in datalines:
                        line = re.sub('ID: ',' ',line)
                        pidlist.append(line.split('.')[0].strip())
                pidlist = list(set(pidlist))
                print "Productids from entitlement cert are %s." %pidlist
        else:
                if 'rct: command not found' in output:
                        print "rct command not found, please use other tool to parse it!"
                else:
                        print "No productid from entitlement cert."

        return pidlist
	

def get_subscription_serialnumlist():
	cmd = "ls /etc/pki/entitlement/ | grep -v key.pem"
	(ret, output) = commands.getstatusoutput(cmd)
        if ret == 0:
                ent_certs = output.splitlines()
                serialnumlist = [line.replace('.pem',  '') for line in ent_certs]

    	return serialnumlist
	
def parse_listavailable_output(output):
	datalines = output.splitlines()
        data_list = []

        # split output into segmentations for each pool
        data_segs = []
        segs = []
        tmpline = ""

        for line in datalines:
        	if ("Product Name:" in line) or ("ProductName" in line) or ("Subscription Name" in line):
                	tmpline = line
            	elif line and ":" not in line:
                      	tmpline = tmpline + ' ' + line.strip()
               	elif line and ":" in line:
                      	segs.append(tmpline)
                      	tmpline = line
            	if ("Machine Type:" in line) or ("MachineType:" in line) or ("System Type:" in line) or ("SystemType:" in line):
                    	segs.append(tmpline)
                      	data_segs.append(segs)
                       	segs = []

  	for seg in data_segs:
            	data_dict = {}
             	for item in seg:
              		keyitem = item.split(":")[0].replace(' ','')
                    	valueitem = item.split(":")[1].strip()
                    	data_dict[keyitem] = valueitem
                  	data_list.append(data_dict)

 	return data_list
	

stage_name = "qa@redhat.com"
stage_passwd = "HWj8TE28Qi0eP2c"
try:
	register(stage_name, stage_passwd)
	sku_list = get_sku_pool_dict()[0]
	print "All subscriptions get from Prod Candlepin is: %s." %sku_list
	product_id_dict = {}
	for sku in sku_list:
		print "="*30
		subscribe(sku)
		product_id = get_productids_from_entitlement_cert_with_rct()
		unsubscribe()
		product_id_dict[sku] = product_id
	print "All productid get from production candlepin is: %s." %product_id_dict	
	
except Exception,e:
	print "error happen during test!"
finally:
	unregister()

