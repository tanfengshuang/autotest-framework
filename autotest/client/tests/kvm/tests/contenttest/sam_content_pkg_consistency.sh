#! /bin/bash
##
# common functions and variables for content testing
# requirements:
#     username, password, SKU, PID relserver
# Usage:
#      bash sam_content_pkg_consistency.sh username password SKU PID relserver 
#      e.g.
#      bash sam_content_pkg_consistency.sh stage_test_12 redhat RH0103708 69 http://download.lab.bos.redhat.com/rel-eng/CloudForms/SubscriptionAssetManager/1.0/2012-04-12.2/logs/SubscriptionAssetManager-1.0-manifest.log
#
# common functions:
#     1. Register
#     2. Subscribe
#     3. Packages consistency validation
#     4. Unregister
# author: 
# date: 
##

function p_date() {
    date +"%F %T"
}

##
# echo with timestamp
# @string
##
function d_echo() {
    echo $(p_date)" $1"
}

##
# @error (optional)
##
function fail() {
    d_echo "********** FAIL $1 "
}

##
# check the system registered or not
##
function is_registered() {
    #d_echo "********** Verify registration status "
    cmd="subscription-manager identity"
    d_echo "$cmd"
    eval $cmd
    [ -f /etc/pki/consumer/cert.pem ] && return 0
    return 1
}

##
# Is product subscribed
# @product_id
##
function is_subscribed_prd() {
    local i
    local prd_id=$1
    result4=$(for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i;done | grep $prd_id)
    if [ $result4'X' != 'X' ] 
    then 
         d_echo "Subscribe to Entitlement Pool with Product $prd_id: --- PASS "  
    else 
         d_echo "Subscribe to Entitlement Pool with Product $prd_id: --- FAIL "
         unregister
    fi
}

##
# Register
# @username
# @passwd
##
function register() {
    d_echo "********** Step1. Register Start "
    local _username=$1
    local _pwd=$2
    local _type=$3
    if [ "${_type}" == "RHUI" ];then
        cmd="subscription-manager register --type=RHUI --username=$_username --password=$_pwd" 
    else
        cmd="subscription-manager register --username=$_username --password=$_pwd" 
    fi
    d_echo "$cmd"
    eval $cmd
    is_registered
    if [ $? -ne 0 ] 
    then 
       d_echo "Register The System to Server: --- FAIL " 
       unregister
       exit
    else
	d_echo "Register The System to Server: --- PASS "
    fi
    d_echo "********** Step1. Register End "
}

##
# list available subscriptions
##
function list_avail() {
    cmd="subscription-manager list --available"
    d_echo "$cmd"
    eval $cmd
}

##
# @PoolId
##
function subscribe() {
    local pool_id=$1
    cmd="subscription-manager subscribe --pool=$pool_id"
    d_echo "$cmd"
    eval $cmd
}

##
# Unregister system from a candlepin server
##
function unregister() {
    d_echo "********** Step4. Unregister Start "
    cmd="subscription-manager unregister"
    d_echo "$cmd"
    eval $cmd
    d_echo "********** Step4. Unregister End "
}

##
#@SKU
##
function subscribe_pool(){
    local sku
    sku=$1
    d_echo "********** Step2.1. Subscribe to a Pool Start "
    prd_id=$(echo $sku | grep '^ *' | awk -F"," '{print $1}')
    pool_id=""
    pool_id=$(grep --max-count=1 -A 1 $prd_id $tmp | awk -F":" '/PoolId/{print $2;}' | sed 's/^[ \t]*//;s/[ \t]*$//')
    if [ $pool_id'X' = 'X' ]
    then
        d_echo "no SKU=$prd_id available. To confirm, run subscription-manager list --available" && fail
    else
        d_echo "Subscribing to poolId $pool_id (PID=$prd_id)"
        cmd="subscription-manager subscribe --pool=$pool_id"
        d_echo "$cmd"
        eval $cmd
        is_subscribed_prd $prd_id
    fi
    d_echo "********** Step2.1. Subscirbe to a Pool End "
}

## 
# verify entitlement certificate
#@SKU
##
function verify_entitlement(){
     local sku
     sku=$1
     local i
     str="1.3.6.1.4.1.2312.9.1."
     d_echo "********** Step2.2. Verify SKU and PID in Entitlement Cert Start "
     prd_id=$(echo $sku | grep '^ *' | awk -F"," '{print $1}')
     #echo "prd_id" + $prd_id
     # Verify SKU in entitlement cert
     result1=$(for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i;done | grep $prd_id)
     if [ $result1'X' != 'X' ]	
     then 
         d_echo "Verify SKU $prd_id in entitlement cert: --- PASS "
     else
         d_echo "Verify SKU $prd_id in entitlement cert: --- FAIL "
         unregister
         exit
     fi

     #Verify productid in entitlement cert
     pidlist=$(echo $PID | awk -F',' '{for(i=1;i<=NF;i++) print $i}')    
     for pid in $pidlist;
     do
	     result2=$(for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i;done | grep --max-count=1 -A 1 ${str}${pid})
	     if [[ -n "$result2" ]] 
	     then 
	         d_echo "Verify PID $pid in entitlement cert: --- PASS "
	     else
	         d_echo "Verify PID $pid in entitlement cert: --- FAIL "
	         unregister
		 exit
	     fi
     done

     d_echo "********** Step2.2. Verify SKU and PID in Entitlement Cert End "
     cp /etc/pki/entitlement/* ./
}

##
# check whether the system need subscribe to a baseproduct
# @ sku
##
function check_and_subscribe_baseproduct(){
    local prdid
    prdid=$1
    d_echo "********** Step2.3. Check and Subscribe the Base Product Start "
    sku2=$(echo $prdid | awk -F"," '{print $2}')
    if [ $sku2'X' = 'X' ]
    then
        d_echo "no base product"
    else
        tmp=$(mktemp)
        list_avail | tee $tmp
        prd_id=$( echo $prdid | grep '^ *' | awk -F"," '{print $2}')
        pool_id=""
        pool_id=$(grep --max-count=1 -A 1 $prd_id $tmp | awk -F":" '/PoolId/{print $2;}' | sed 's/^[ \t]*//;s/[ \t]*$//')
        if [ $pool_id'X' = 'X' ]
        then
            d_echo "no SKU=$prd_id available. To confirm, run subscription-manager list --available" && fail
        else
            subscribe $pool_id
            is_subscribed_prd $prd_id
        fi
    fi
    d_echo "********** Step2.3 Check and Subscribe the Base Product End "
}


function yum_repolist(){
     cmd="yum repolist"
     d_echo "$cmd"
     eval $cmd
}

function yum_clean_cache(){
     cmd="yum clean all"
     d_echo "$cmd"
     eval $cmd
}

##
# enable all test repos
# @ testrepo
##
function enable_all_testrepos(){
    testrepo=$1

    yum_repolist
    #enable repos to test
    while read repo
    do
	line=$(grep -n "\[$repo\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')
        sed -i "$(($line+3)) s/0/1/" /etc/yum.repos.d/redhat.repo
    done < $testrepo

    d_echo  "Display All Enabled Repos "
    yum_repolist
}

##
# @ repoid
# @ PkgUrl
# @ PkgManifest
##
function verify_content(){
    d_echo "********** Step3. Level1-3 Verify Rpms Package For Repo $1 Start "   
    repoid=$1	
    PkgUrl=$2

    d_echo "Get Available Pkglist Name from repo metadata" 
    pkglist=$(mktemp)
    
    if [[ $repoid == *source* || $repoid == *src*  ]]
    then
	 cmd="repoquery --show-dupes --all --repoid=$repoid --archlist=src --qf "%{name}-%{version}-%{release}.%{arch}.rpm" > $pkglist"	
     else
	 cmd="repoquery --show-dupes --all --repoid=$repoid --qf "%{name}-%{version}-%{release}.%{arch}.rpm" > $pkglist"
    fi
    d_echo "$cmd"
    eval $cmd

    d_echo "Check Pkg List in repo metadata."
    pkglistlen=$(cat $pkglist | wc -l)   
    echo "Repo metadata list $pkglistlen packages!!!"

    #----------------------------------------------------------------------------------------
    #**NOTE**:
    #update code here to get the pkg list from the package manifest if it's available in cdn website,
    #here just use the previous 'pkglist' as test data temporarily
    #pkgmanifest=$3

    #(1)compare the packages got by repoquery to those listed in package manifest
    d_echo "Compare rpms packages listed in repo metadata with that in packages manifest (skip due to lack of Packages manifest.)"
    #pkginvalid1=$(mktemp)
    #while read line
    #do
    #      grep $line $pkglist > /dev/null
    #      if [ $? -ne 0 ];
    #      then
    #            echo $line >> $pkginvalid1
    #      fi
    #done < $pkgmanifest
    #cat $pkginvalid1
    #d_echo "Above $(cat $pkginvalid1 | wc -l) pkgs listed in rpms list could not be found in package manifest!" 
    #rm -f $pkginvalid1

    #(2)compare the packages listed in repodata to those in packages directory
    d_echo "Get Available rpms Pkgs from Packages Content Directory."
    pkgcontent=$(mktemp)
    pkgtmp=$(mktemp)
    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $PkgUrl > $pkgtmp"
    d_echo "$cmd"
    eval $cmd    
    grep "rpm" $pkgtmp |cut -d"]" -f 2|cut -d"=" -f 2|cut -d">" -f 1 | sed -e "s/^\"//" -e "s/\"$//" > $pkgcontent
    rm -f $pkgtmp
    
    d_echo "Check rpms Pkgs in Packages Content Directory."
    rpmpkglen=$(cat $pkgcontent | wc -l)
    echo "Packages Content Directory contain $rpmpkglen packages!!!"

    d_echo "Compare Rpms Pkgs Listed in Repo Metadata with that in Packages Content Directory."
    pkginvalid2=$(mktemp)
    while read line
    do
          grep $line $pkglist > /dev/null
          if [ $? -ne 0 ];
          then
                echo $line >> $pkginvalid2
          fi
    done < $pkgcontent

    pkginvalid3=$(mktemp) 
    while read line
    do
          grep $line $pkgcontent > /dev/null
          if [ $? -ne 0 ];
          then
                echo $line >> $pkginvalid3
          fi
    done < $pkglist

    pkginvl2len=$(cat $pkginvalid2 | wc -l)
    pkginvl3len=$(cat $pkginvalid3 | wc -l)
    if [[ $pkginvl2len -ne 0  || $pkginvl3len -ne 0 ]]
    then
	cat $pkginvalid2
	echo "Above $(cat $pkginvalid2 | wc -l) pkgs could not find in repo metadata!"
        echo "**************************************************"
        cat $pkginvalid3 
        echo "Above $(cat $pkginvalid3 | wc -l) pkgs could not find in Packages Content Directory!"
        echo "**************************************************"
        d_echo "Verify Package Consistence for Repo $1: --- FAIL "
    else
	echo "No Package Different Between Listed in Repo Metadata and that in Packages Content Directory!"
	d_echo "Verify Package Consistence for Repo $1: --- PASS "
    fi
    rm -f $pkginvalid2
    rm -f $pkginvalid3

    #----------------------------------------------------------------------------------------    
    d_echo "********** Step3. Level1-3 Verify Rpms Packages For Repo $1 End "
    rm -f $pkgcontent
    rm -f $pkglist
}



##
#  content test
# @ repomanifest
# @ currentrelserver
# @ currentarch
# @ relserver: dist or beta
##
function content_test()
{ 
     register $User $PWD $type
     tmp=$(mktemp)
     list_avail | tee $tmp
     subscribe_pool $SKU
     verify_entitlement $SKU 

     #get test repos
     testrepo=$(mktemp)
     if [[ $relserver == *beta* ]]
     then
        grep "beta" $repomanifest > $testrepo    
     else
	grep -v  "beta" $repomanifest > $testrepo
     fi
     
     testrepolen=$(cat $testrepo | wc -l)
     if [[  $testrepolen -eq 0  ]] 
     then
         echo "There is no Content Set to test."
	 unregister
	 exit
     fi
     
     yum_clean_cache
     yum_repolist
     #enable all test repos
     enable_all_testrepos $testrepo

     pkglist=$(mktemp)
     #Get packages from each effective repo start     
     while read line
     do
	#get repoid and PkgUrl parameters
	repoid=$line
	urlline=$(($(grep -n "^\[$repoid\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+2))
        pkgurl=$(sed -n "$urlline p" /etc/yum.repos.d/redhat.repo | awk -F"=" '{print $2}')
	if [[ $pkgurl == *SRPMS* ]]
	then
        	PkgUrl=$(echo $pkgurl | sed -e "s/\$releasever/$CurrentRelServer/" -e "s/\$basearch/$CurrentArch/" -e "s/$/\//")
	else
		PkgUrl=$(echo $pkgurl | sed -e "s/\$releasever/$CurrentRelServer/" -e "s/\$basearch/$CurrentArch/" -e "s/$/\/Packages\//" )
	fi
	#Get packages name list from the repo
        if [[ $repoid == *source* || $repoid == *src*  ]]
        then
        	cmd="repoquery --show-dupes --all --repoid=$repoid --archlist=src --qf "%{name}-%{version}-%{release}.%{arch}" >> $pkglist"
        else
        	cmd="repoquery --show-dupes --all --repoid=$repoid --qf "%{name}-%{version}-%{release}.%{arch}" >> $pkglist"
        fi
        d_echo "$cmd"
        eval $cmd

    done < $testrepo
    #Get packages from each effective repo end
    pkglistlen=$(cat $pkglist | wc -l)
    d_echo "Effective repos contains $pkglistlen packages."

    #Get packages from manifest of puddle logs
    package_mf=$(mktemp)
    cmd="curl -k $puddlelog_url | grep -v 'manifest log' | sed '/^[[:space:]]*$/d' > $package_mf"
    d_echo "$cmd"
    eval $cmd
    rpmpkglen=$(cat $package_mf | wc -l)
    d_echo "Packages manifest contains $rpmpkglen packages."

    # compare pkglist from repos and packages manifest from puddle
    d_echo "Packages Consistency Validation"
    pkginvalid=$(mktemp)
    if [  $pkglistlen -eq $rpmpkglen  ]
    then
	    while read line
	    do
        	grep $line $package_mf > /dev/null
          	if [ $? -ne 0 ];
          	then
                	echo $line >> $pkginvalid
          	fi
            done < $pkglist

	    invalidlen=$(cat $pkginvalid | wc -l)
            if [ $invalidlen -ne 0 ]
            then
		cat $pkginvalid
		d_echo "Above $invalidlen packages are mismatched."
		d_echo "Validate Package Consistency: --- FAIL "	
	    else
		d_echo "Validate Package Consistency: --- PASS "
	    fi
    else
	    d_echo "Number of two files are inconsistent."
	    d_echo "Validate Package Consistency: --- FAIL "
    fi

     unregister
     is_registered && fail

     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     rm -f $tmp
     rm -f $testrepo
     rm -f $pkglist
     rm -f $package_mf
     rm -f $pkginvalid

}
     
     #Main
     d_echo "**************************************************"
     d_echo "********** Content Test Preparation "
     d_echo "**************************************************"
     User=$1
     PWD=$2
     SKU=$3
     PID=$4
     puddlelog_url=$5

     #clean up
     subscription-manager unregister
     subscription-manager clean
     rm -f *.pem
     #delete rhn debuginfo repo to remove affect
     rm -f $(ls /etc/yum.repos.d/* | grep -v  "redhat.repo")

     #get current release server and current architecture
     CurrentRelServer=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'releasever' | awk -F":" '{print $2}' | sed  -e "s/^ '//" -e "s/'}$//" -e "s/',$//")    
     relversion=$(echo $CurrentRelServer | grep -Eo '^[0-9]')
     echo "Current Release Version is $CurrentRelServer"

     CurrentArch=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'basearch' | awk -F":" '{print $2}' | sed -e "s/'//" -e "s/',//" -e "s/^ //" -e "s/$ //")
     repomanifest=$(mktemp)
     echo "Current Achitecture is $CurrentArch"
     repomanifest=$(mktemp)
     if [[ $CurrentArch == *ppc* ]]
     then
	grep "rhel\-$relversion" /tmp/contenttest/sam.txt | grep "power" | sed -e "s/^ *//" -e "s/ *$//" > $repomanifest
     else
	grep "rhel\-$relversion" /tmp/contenttest/sam.txt | grep -v "power" | sed -e "s/^ *//" -e "s/ *$//" > $repomanifest
     fi
 
     cat $repomanifest
         
     d_echo "**************************************************"
     d_echo "********** Content Test Start "
     d_echo "**************************************************"
     content_test $repomanifest $puddlelog_url
     d_echo "**************************************************"
     d_echo "********** Content Test End "
     d_echo "**************************************************"
     rm -f $repomanifest
     rm -f *.pem
     exit

