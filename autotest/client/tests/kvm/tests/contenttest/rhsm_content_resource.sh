#! /bin/bash
##
# common functions and variables for content testing
# requirements:
#     username, password, SKU, PID, content_level, repomanifest, relserver
# Usage:
#      bash rhsm_content_resource.sh username password SKU PID content_level relserver type
#      e.g.
#      bash rhsm_content_resource.sh stage_test_12 redhat RH0103708 69 level1,level2 beta RHUI
#
# common functions:
#     1. Register
#     2. Subscribe
#     3. Content Test (including level1, level2 and level3)
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
    echo 
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
    pool_id=$(grep --max-count=1 -A 1 $prd_id $tmp | awk -F":" '/Pool(.*)Id/{print $2;}' | sed 's/^[ \t]*//;s/[ \t]*$//')
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
    rm -f $tmp
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
#@arrayA @arrayB
##
function compare_array(){
    arrayA=$(echo $1)
    arrayB=$(echo $2)
    #find data in arrayA but not in arrayB
    diff_A2B=$(awk 'NR==1{for(i=1;i<=NF;i++) arrayB[$i]=1}NR==2{for(j=1;j<=NF;j++) {if(arrayB[$j]!=1) print $j}} ' <(echo $arrayB) <(echo $arrayA))

    #find data in arrayB but not in arrayA
    diff_B2A=$(awk 'NR==1{for(i=1;i<=NF;i++) arrayB[$i]=1}NR==2{for(j=1;j<=NF;j++) {if(arrayB[$j]!=1) print $j}} ' <(echo $arrayA) <(echo $arrayB))

}

##
#@pid
##
function verify_arch(){
     local pid
     pid=$1
     str="1.3.6.1.4.1.2312.9.1.${pid}.3"
     d_echo "********** Step2.3. Verify Supported Architecture in Entitlement Cert Start "
     
     # Verify arch in entitlement cert
     result=$(openssl x509 -text -noout -in $(ls ./*.pem | grep -v key.pem) | grep $str -A 2 )
     if [ $(echo $result | tr -cd ":" | wc -c) -ne 1 ];
     then
	result=$(openssl x509 -text -noout -in $(ls ./*.pem | grep -v key.pem) | grep $str -A 1 )
     fi
     testarch=$(echo $result | sed -e "s/^.*:.*\.//" -e "s/^ //" -e "s/ $//")
     archlist=$(echo $testarch | awk -F',' '{for(i=1;i<=NF;i++) print $i}')
    
     index=0
     #declare one empty array
     declare -a cert_arch=()
     for arch in $archlist;
     do
	if [[ ${arch} == x86 ]]
    	then
		cert_arch[$index]='i386'
	elif [[ ${arch} == ppc  && $CurrentRelVer == *6* ]]
        then
		cert_arch[$index]='ppc64'
	elif [[  ${arch} == ppc64  && $CurrentRelVer == *5* ]]
	then
		cert_arch[$index]='ppc'
	elif [[  ${arch} == s390 ]]
	then
		cert_arch[$index]='s390x'
	elif [[ ${arch} == ia64 && $CurrentRelVer == *6* ]]
	then
		continue;
	else
		cert_arch[$index]=${arch}
	
    	fi
	index=$(($index+1))
     done
     d_echo "Supported arch in entitlement cert are $(echo ${cert_arch[*]})."
          
     exp_arch=$(echo $(ls -d /tmp/contenttest/${pid}_* | sed -e "s/^.*${pid}_//"))
     #just a workaround now, will be modified after redesign.
     if [[ $pid == 132 ||  $pid == 92 || $pid == 146 ]]
     then
	exp_arch=$(echo $exp_arch | sed -e "s/i386 //") 
     fi
     d_echo "Expected supported arch are $exp_arch"
     #compare two group of arch
     compare_array "${cert_arch[*]}" "$exp_arch"     

     if [[ $diff_A2B || $diff_B2A ]]
     then
	echo "arch in entitlement cert but not expected support: $diff_A2B"
	echo "arch expected support but not in entitlement cert: $diff_B2A"
       	d_echo "Verify supported arch ${cert_arch[*]} in entitlement cert: --- FAIL "
     else
       	d_echo "Verify supported arch ${cert_arch[*]} in entitlement cert: --- PASS "
     fi

     d_echo "********** Step2.3. Verify Supported Architecture in Entitlement Cert End "
     #clear array
     unset cert_arch
}

##
##
function verify_repomanifest(){
    d_echo "********** Step3. level1-1 Verify Consumed Reposlist According To Subscription Start "
    d_echo "Get Consumed Repolist "
    consumedrepolist=$(mktemp)
    yum repolist all | sed -n '/repo id/{:a;n;/repolist:/q;p;ba}' | awk -F' ' '{print $1}' > $consumedrepolist
    cat /tmp/contenttest/product_blacklist.xml | sed -n "/<$CurrentRelVer-$CurrentArch>/{:a;n;/<\/$CurrentRelVer-$CurrentArch>/q;p;ba}" > blacklist
 
    if [ $(cat blacklist | wc -l ) -gt 0 ];then
        while read line
        do
           grep $line $consumedrepolist > /dev/null
	   if [ $? -eq 0 ];then
	      sed -i "/$line/d" $consumedrepolist
           fi  
        done < blacklist
    fi
    rm -f blacklist
    cat $consumedrepolist
    consumedrepo=$(cat $consumedrepolist)
    rm -f $consumedrepolist

     d_echo "Display Given Repo manifest"
     #get repo manifest, when several products bundled in one subscription, we need test all repos.
     repomf=$(mktemp)
     pidlist=$(echo $PID | awk -F',' '{for(i=1;i<=NF;i++) print $i}')
     for pid in $pidlist;
     do
                ls /tmp/contenttest/$pid"_"$CurrentArch/ | grep "\.txt" | sed -e "s/\.txt.*$//" >> $repomf
     done
     cat $repomf
     mfrepo=$(cat $repomf)
     rm -f $repomf

     d_echo "Compare Consumed Repolist with Given Repo manifest"
     compare_array "$consumedrepo" "$mfrepo"

     if [[ $diff_A2B || $diff_B2A ]]
     then
         echo $diff_A2B | awk '{for(i=1;i<=NF;i++){print $i}}'
	 echo "Above $(echo $diff_A2B | awk '{print NF}') repos in entitlement cert but not in repo manifest!"
         echo $diff_B2A | awk '{for(i=1;i<=NF;i++){print $i}}'
         echo "Above $(echo $diff_B2A | awk '{print NF}') repos in repo manifest but not in entitlement cert!"	 
         d_echo  "Verify Consumed Reposlist: --- FAIL "
         unregister
         exit
     fi

     d_echo "Verify Consumed Reposlist: --- PASS "
     d_echo "********** Step3. level1-1 Verify consumed reposlist according to subscription End "   
}

##
# check whether the system need subscribe to a baseproduct
# @ sku
##
function check_and_subscribe_baseproduct(){
    local prdid
    prdid=$1
    d_echo "********** Step2.4. Check and Subscribe the Base Product Start "
    sku2=$(echo $prdid | awk -F"," '{print $2}')
    if [ $sku2'X' = 'X' ]
    then
        d_echo "no base product"
    else
        tmp=$(mktemp)
        list_avail | tee $tmp
        prd_id=$( echo $prdid | grep '^ *' | awk -F"," '{print $2}')
        pool_id=""
        pool_id=$(grep --max-count=1 -A 1 $prd_id $tmp | awk -F":" '/Pool(.*)Id/{print $2;}' | sed 's/^[ \t]*//;s/[ \t]*$//')
        if [ $pool_id'X' = 'X' ]
        then
            d_echo "no SKU=$prd_id available. To confirm, run subscription-manager list --available" && fail
        else
            subscribe $pool_id
            is_subscribed_prd $prd_id
        fi
    fi
    d_echo "********** Step2.4. Check and Subscribe the Base Product End "
    rm -f $tmp
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
# verify two "magic listing files"
# @PkgUrl
##
function verify_listing_files(){
    d_echo "********** Step3. Level1-2 Verify Listing Files Start "
    url=$1
    rellistingurl=$(echo $url | sed "s/$CurrentRelVer.*$/listing/")
    d_echo "Get Release Version listing file from $rellistingurl "
    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $rellistingurl"
    d_echo "$cmd"
    rellisting=$($cmd)
    rellisting=$(echo $rellisting)
    echo "Release Version listing file contains $rellisting"

    if [[ $url == *rcm-qa* ]]
    then
	    reldirurl=$(echo $url | sed -e "s/https/http/" -e "s/$CurrentRelVer.*$//" )
	    d_echo "Get Release Version Sibling Directories from $reldirurl"
	    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $reldirurl > /tmp/reldirs"
    else
            reldirurl=$(echo $url | sed  -e "s/$CurrentRelVer.*$//" )
            d_echo "Get Release Version Sibling Directories from $reldirurl"
            cmd="curl --cert /tmp/contenttest/debug_cert/rcm-debug-20130208.crt --key /tmp/contenttest/debug_cert/rcm-debug-20130208.key -k $reldirurl > /tmp/reldirs"
    fi
    d_echo "$cmd"  
    eval $cmd
    reldirs=$(sed -e '/Parent/d' -e '/\.old/d' /tmp/reldirs | grep DIR | awk '{print $5}' | awk -F '"' '{print $2}' | sed 's/\///' )
 
    #handle releasing directory according to bug 785989
    if [[ $CurrentRelVer == *5* ]]
    then
        reldirs=$(echo $reldirs | sed "s/^.*5.7/5.7/")
    elif [[ $CurrentRelVer == *6* ]]
    then
        reldirs=$(echo $reldirs | sed "s/^.*6.1/6.1/")
    else
        reldirs=$reldirs
    fi
    echo "Release Version sibling dirs are $reldirs"

    d_echo "Compare Release Version listing file and Release Version Sibling Directories."
    if [[ "$reldirs" = "$rellisting" ]]
    then
        d_echo "Verify Release Listing File: --- PASS "
    else
        d_echo "Verify Release Listing File: --- FAIL "
    fi

    archlistingurl=$(echo $url | sed "s/$CurrentArch.*$/listing/")
    d_echo "Get Arch listing file from $archlistingurl"
    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $archlistingurl"
    d_echo "$cmd"
    archlisting=$($cmd)
    echo "Arch listing file contains $archlisting"

    if [[ $url == *rcm-qa* ]]
    then
	    archdirurl=$(echo $url | sed -e "s/https/http/" -e "s/$CurrentArch.*$//")
	    d_echo "Get Arch Sibling Directories from $archdirurl"
	    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $archdirurl > /tmp/archdirs"
    else
            archdirurl=$(echo $url | sed -e "s/$CurrentArch.*$//")
            d_echo "Get Arch Sibling Directories from $archdirurl"
            cmd="curl --cert /tmp/contenttest/debug_cert/rcm-debug-20130208.crt --key /tmp/contenttest/debug_cert/rcm-debug-20130208.key -k $archdirurl > /tmp/archdirs"	
    fi
    d_echo "$cmd"
    eval $cmd
    archdirs=$(sed -e '/Parent/d' /tmp/archdirs | grep DIR | awk '{print $5}' | awk -F '"' '{print $2}' | sed 's/\///'| sort )
    echo "Arch sibling dirs are $archdirs"
    
    d_echo "Compare Arch listing file and Arch Sibling Directories."
    if [[ "$archdirs" = "$archlisting" ]]
    then
        d_echo "Verify Arch Listing File: --- PASS "
    else
        d_echo "Verify Arch Listing File: --- FAIL "
    fi	
    d_echo "********** Step3. Level1-2 Verify Listing Files End "
    rm -f /tmp/reldirs
    rm -f /tmp/archdirs
}

##
# @ repoid
# @ PkgUrl
# @ PkgManifest
##
function verify_package_consistency(){
    d_echo "********** Step3. Level1-3 Verify Package Consistency For Repo $1 Start "   
    repoid=$1	
    PkgUrl=$2
    pkgmf=$3
    #----------------------------------------------------------------------------------------
    d_echo "Get Available Pkglist Name from repo metadata"

    if [[ $repoid == *source* || $repoid == *src*  ]]
    then
         cmd="repoquery --show-dupes --all --repoid=$repoid --archlist=src --qf "%{name}-%{arch}" | sort -u "
     else
         cmd="repoquery --show-dupes --all --repoid=$repoid --qf "%{name}-%{arch}" | sort -u "
    fi
    d_echo "$cmd"
    pkgname=$(eval $cmd)
    pkglistlen=$(echo $pkgname | awk '{print NF}')
    echo "Repo metadata contains $pkglistlen package names!!!"

    d_echo "Get packages' name from packages manifest"
    pkgmanifest=$(cat $pkgmf | sed "s/[\r\n]//g" | awk -F' ' '{if(NF>3){print $1"-"$4 }}' | sort -u )
    pkgmflen=$(echo $pkgmanifest | awk '{print NF}')
    echo "Packages manifest contains $pkgmflen packages!!"

    d_echo "Compare rpms packages listed in repo metadata with that in packages manifest."
    #if [ $pkglistlen -ne $pkgmflen ]
    #then
    #	echo "Length of rpm packages between package manifest and repo metadata are different!!!"
    #	d_echo "Verify Package Consistency Between Package Manifest and Repo Metadata for Repo $1: --- FAIL "
    #else
    #show all different packages 
    #compare_array "$pkgname" "$pkgmanifest"

    arrayA=$(echo "$pkgname")
    arrayB=$(echo "$pkgmanifest")
    #find data in arrayA but not in arrayB
    diff_B2A=$(awk 'NR==1{for(i=1;i<=NF;i++) arrayB[$i]=1}NR==2{for(j=1;j<=NF;j++) {if(arrayB[$j]!=1) print $j}} ' <(echo $arrayA) <(echo $arrayB))

    #check result 
    if [[ $diff_B2A ]]
    then
        echo $diff_B2A | awk '{for(i=1;i<=NF;i++){print $i}}'
        echo "Above $(echo $diff_B2A | awk '{print NF}') pkgs in package manifest could not find in repo metadata!" 
	echo "*******************************************************"
        #echo $diff_A2B | awk '{for(i=1;i<=NF;i++){print $i}}'
	#echo "Above $(echo $diff_A2B | awk '{print NF}') pkgs in repo metadata could not find in package manifest!" 
        #echo "*******************************************************"
	d_echo "Verify Package Consistency Between Package Manifest and Repo Metadata for Repo $1: --- FAIL "
    else
        echo "No Package Different Between Listed in Repo Metadata and that in Packages Manifest!"
        d_echo "Verify Package Consistency Between Package Manifest and Repo Metadata for Repo $1: --- PASS "
    fi
    #fi
   
    #----------------------------------------------------------------------------------------
    #(2)compare the packages listed in repodata to those in packages directory
    d_echo "Get Available Pkglist Name from repo metadata"

    if [[ $repoid == *source* || $repoid == *src*  ]]
    then
         cmd="repoquery --show-dupes --all --repoid=$repoid --archlist=src --qf "%{name}-%{version}-%{release}.%{arch}.rpm" "
     else
         cmd="repoquery --show-dupes --all --repoid=$repoid --qf "%{name}-%{version}-%{release}.%{arch}.rpm" "
    fi
    d_echo "$cmd"
    pkglist=$(eval $cmd)

    d_echo "Check Pkg List in repo metadata."
    pkglistlen=$(echo $pkglist | awk '{print NF}')
    echo "Repo metadata list $pkglistlen packages!!!"

    d_echo "Get Available rpms Pkgs from Packages Content Directory."
    pkgtmp=$(mktemp)
    cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k $PkgUrl > $pkgtmp"
    d_echo "$cmd"
    eval $cmd
    pkgcontent=$(grep "rpm" $pkgtmp |cut -d"]" -f 2|cut -d"=" -f 2|cut -d">" -f 1 | sed -e "s/^\"//" -e "s/\"$//")
    rm -f $pkgtmp

    d_echo "Check rpms Pkgs in Packages Content Directory."
    rpmpkglen=$(echo $pkgcontent | awk '{print NF}')
    echo "Packages Content Directory contain $rpmpkglen packages!!!"

    d_echo "Compare Rpms Pkgs Listed in Repo Metadata with that in Packages Content Directory."
    #if [ $pkglistlen -ne $rpmpkglen ]
    #then
    #    echo "Length of rpm packages between package content directory and repo metadata are different!!!"
    #    d_echo "Verify Package Consistency Between Packages Content Directory and Repo Metadata for Repo $1: --- FAIL "
    #else
    #show all different packages
    compare_array "$pkglist" "$pkgcontent"
    if [[ $diff_A2B || $diff_B2A ]]
    then
        echo $diff_A2B | awk '{for(i=1;i<=NF;i++){print $i}}'
	echo "Above $(echo $diff_A2B | awk '{print NF}') pkgs could not find in Packages Content Directory!"
	echo "*******************************************************"
        echo $diff_B2A | awk '{for(i=1;i<=NF;i++){print $i}}'
	echo "Above $(echo $diff_B2A | awk '{print NF}') pkgs could not find in Repo Metadata!"
        echo "*******************************************************"
	d_echo "Verify Package Consistency Between Packages Content Directory and Repo Metadata for Repo $1: --- FAIL "
    else
       	echo "No Package Different Between Listed in Repo Metadata and that in Packages Content Directory!"
        	d_echo "Verify Package Consistency Between Packages Content Directory and Repo Metadata for Repo $1: --- PASS "
    fi
    #fi

    #-------------------------ls /tmp/content---------------------------------------------------------------    
    d_echo "********** Step3. Level1-3 Verify Packages Consistency For Repo $1 End "

}

##
# @repoid
# @pid
##
function verify_productcert_installation(){
    d_echo "********** Step3. Level2-1 Install One Package From Repo $1 Start "

    d_echo "Random Get one Package to Be Installed"
    repoid=$1
    file=$(mktemp)

    if [[ $repoid == *source* || $repoid == *src*  ]]
    then
        cmd="repoquery --pkgnarrow=available --all --repoid=$repoid --archlist=src --qf "%{name}-%{version}-%{release}.src"  > $file "  
    else
    	cmd="repoquery --pkgnarrow=available --all --repoid=$repoid --qf "%{name}" | sort -u > $file "
    fi	
    #get available packages to install
    d_echo "$cmd"
    eval $cmd
    
    total=$(awk 'END{print NR}' $file)
    if [[ $total -ne 0 ]]
    then
    	rnum=$(($RANDOM%$total))
        rnum=$(($rnum+1))
    	pkgname=$(sed -n "$rnum p" $file)
        if [[ $repoid == *source* || $repoid == *src*  ]]
        then
            d_echo "Download The Selected source Package $pkgname "
            cmd="yumdownloader --source $pkgname"
            d_echo "$cmd"
            eval $cmd | tee tmp
            ls $pkgname*
            right=$?
            grep "Trying other mirror" tmp
            wrong=$?
        else
     	    d_echo "Install The Selected Package $pkgname "
     	    cmd="yum -y install $pkgname"
     	    d_echo "$cmd"
     	    eval $cmd|tee tmp
     	    grep -E "Complete\!|Nothing to do" tmp
     	    right=$?
     	    grep "Error:" tmp
     	    wrong=$?
        fi

     	if [ $right -eq 0 ] && [ $wrong -ne 0 ]
     	then
        	 d_echo "Install Package $pkgname: --- PASS "
                 #verify product cert has been installed /etc/pki/product/ for product package repo.
		 if [[  $repoid != *source* && $repoid != *src* && $repoid != *optional* && $repoid != *supplementary* && $repoid != *debug* ]]; then
			verify_productId $pid
		 fi
     	else
        	 d_echo "Install Package $pkgname: --- FAIL "
     	fi

    else
        d_echo "There is no package to install"
    fi

    d_echo "********** Step3. Level2-1 Install One Package From Repo $1 End "
    
    rm -f $file
    rm -f tmp
}

##
#@ pid
##
function verify_productId(){
     d_echo "********** Step3. Level2-2 Verify PID in Product Cert Start "
     local i
     str="1.3.6.1.4.1.2312.9.1."
     ls  /etc/pki/product/$pid.pem
     if [ $? -ne 0 ];
     then
         d_echo "Verify PID $pid in product cert: --- FAIL "
     else
         result3=$(openssl x509 -text -noout -in /etc/pki/product/$pid.pem | grep ${str}${pid})
         if [[ -n "$result3" ]]  
         then
	     d_echo "Verify PID $pid in product cert: --- PASS "
         else
             d_echo "Verify PID $pid in product cert: --- FAIL " 
         fi
     fi
     d_echo "********** Step3. Level2-2 Verify PID in Product Cert End "
}

##
# @repoid
##
function verify_packages_full_installation(){
     d_echo "********** Step3. Level3 Install All Available Packages From Repo $1 Start "

     REPOID=$1
     file=$(mktemp)
     d_echo "Get All Rpms Packages to Install"
     if [[ $REPOID == *source* || $REPOID == *src*  ]]
     then
	cmd="repoquery --all --repoid=$REPOID --archlist=src --qf "%{name}-%{version}-%{release}.src" > $file "
     else
	cmd="repoquery --all --repoid=$REPOID --qf "%{name}" | sort -u > $file"
     fi

     d_echo "$cmd"
     eval $cmd
     total=$(awk 'END{print NR}' $file)
     #the number of packages to be installed per iteration
     step=20
     i=1
     while [ $i -le $total ]
     do
	if [[ $REPOID == *source* || $REPOID == *src*  ]]
	then
	         d_echo "[$(date "+%F %T")]  #$i yumdownloader --source $(sed -n $i,$((i+step))p $file)#"	
		 yumdownloader --source $(sed -n $i,$((i+step))p $file)
                 
	else
		 d_echo "[$(date "+%F %T")]  #$i yum install -y --skip-broken $(sed -n $i,$((i+step))p $file)#"
    		 yum install -y --skip-broken $(sed -n $i,$((i+step))p $file) | grep -v "already installed and latest version"
	fi

    	 i=$((i+step))
     done

     rm -f $file
     d_echo "********** Step3. Level3 Install All Available Packages For Repo $1 End "
}

##
# verify treeinfo path on cdn
# @pkgurl, @current_arch, @SKU
##
function verify_treeinfo()
{
     d_echo "********** Step3. Level1-4 Verify Treeinfo File " 
     #get _os_url
     local _pkgurl=$1
     local _cur_arch=$2
     local prdid=$3
     _os_url=$(echo $_pkgurl | sed "s/$_cur_arch.*$/$_cur_arch\/os/" )

     # get treeinfo file path
     treeinfo_file="${_os_url}/treeinfo"
     d_echo "treeinfo_file= $treeinfo_file"
     sku2=$(echo $prdid | awk -F"," '{print $2}')
     if [ $sku2'X' = 'X' ]
     then
	cmd="curl --cert $(ls ./*.pem | grep -v key.pem) --key $(ls ./*.pem | grep key.pem) -k ${treeinfo_file}"
     else
	cert=$(ls /etc/pki/entitlement/* | grep -v key.pem | grep -v $(ls ./*.pem | grep -v key.pem))
	key=$(ls /etc/pki/entitlement/* | grep key.pem | grep -v $(ls ./*.pem | grep key.pem))
	cmd="curl --cert  $cert --key $key -k ${treeinfo_file}"
     fi
     d_echo "$cmd"

     if eval $cmd | grep "The requested URL" | grep "not found on this server">/dev/null;
     then
          d_echo "Missing: $treeinfo_file"
          d_echo "Verify treeinfo: --- FAIL "     
     else
          if eval $cmd | grep "\[general\]" >/dev/null;
          then
              d_echo "Verify treeinfo: --- PASS "
          else
              d_echo "Missing: $treeinfo_file"
              d_echo "Verify treeinfo: --- FAIL "
          fi
     fi
     d_echo "********** Step3. Level1-4 Verify Treeinfo File End " 
}

##
#  content test
# @ repomanifest
# @ currentrelserver
# @ currentarch
# @ content_level: level1, level2 or level3, or level1,level2
# @ relserver: dist or beta
##
function content_test()
{ 
     register $User $PWD $type
     tmp=$(mktemp)
     list_avail | tee $tmp
     subscribe_pool $SKU
     verify_entitlement $SKU 
  
     #verify repo manifest 
     if [[ $content_level == *level1* ]]
     then
	    verify_repomanifest
     fi
     check_and_subscribe_baseproduct $SKU
    
     d_echo "Content validation for each product of the subscription Start" 
     pidlist=$(echo $PID | awk -F',' '{for(i=1;i<=NF;i++) print $i}')
     for pid in $pidlist;
     do
	#verify arch attribute from entitlement cert #
	if [[ $content_level == *level1* ]]
	then
		verify_arch $pid
	fi
	
	d_echo "Get testrepo for PID $pid"
	testrepo=$(mktemp)
     	if [[ $relserver == *beta* ]]
     	then
        	ls /tmp/contenttest/$pid"_"$CurrentArch/ | grep "\.txt" | sed -e "s/\.txt.*$//" | grep "beta" > $testrepo    
     	else
		ls /tmp/contenttest/$pid"_"$CurrentArch/ | grep "\.txt" | sed -e "s/\.txt.*$//" | grep -v  "beta"  > $testrepo
     	fi
     
	testrepolen=$(cat $testrepo | wc -l)
     	if [[  $testrepolen -eq 0  ]] 
     	then
        	echo "There is no Content Set to test for PID $pid."
		rm -f $testrepo
	 	unregister
	 	exit
     	fi

        #clean yum cache
 	yum_clean_cache
     	#enable all test repos for $pid
     	enable_all_testrepos $testrepo

     	d_echo "Content validation for each effective repo for PID $pid Start"     
     	checklisting=0
     	checktreeinfo=0
    	while read line
     	do
		#get repoid and PkgUrl parameters
		repoid=$line
		urlline=$(($(grep -n "^\[$repoid\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+2))
        	pkgurl=$(sed -n "$urlline p" /etc/yum.repos.d/redhat.repo | awk -F"=" '{print $2}')
		if [[ $pkgurl == *SRPMS* ]]
		then
                                  
        		PkgUrl=$(echo $pkgurl | sed -e "s/\$releasever/$CurrentRelVer/" -e "s/\$basearch/$CurrentArch/" -e "s/$/\//")
		else
			PkgUrl=$(echo $pkgurl | sed -e "s/\$releasever/$CurrentRelVer/" -e "s/\$basearch/$CurrentArch/" -e "s/$/\/Packages\//" )
		fi
		pkgmf=/tmp/contenttest/$pid"_"$CurrentArch/$repoid.txt		

		case $content_level in
        		level1)
                        	if [[ $checklisting == *0* ]]
				then
					verify_listing_files $PkgUrl
					checklisting=1
				fi

        			if [ ${checktreeinfo} -eq 0 ];then
        		    		# verify treeinfo        
        		    		verify_treeinfo $PkgUrl $CurrentArch $SKU
                            		checktreeinfo=1
        			fi
				
				verify_package_consistency $repoid $PkgUrl $pkgmf
				;;
         		level2)
				verify_productcert_installation $repoid $pid
				;;
         		level3)
				verify_packages_full_installation $repoid
				;;
         		level1,level2)
                        	if [[ $checklisting == *0* ]]
                        	then
                                	verify_listing_files $PkgUrl
                                	checklisting=1
                        	fi
 
        			if [ ${checktreeinfo} -eq 0 ];then
        		    		# verify treeinfo        
        		    		verify_treeinfo $PkgUrl $CurrentArch $SKU
                            		checktreeinfo=1
        			fi

                		verify_package_consistency $repoid $PkgUrl $pkgmf

                		verify_productcert_installation $repoid $pid
				;;
	 		level1,level3)
                        	if [[ $checklisting == *0* ]]
                        	then
                                	verify_listing_files $PkgUrl
                                	checklisting=1
                        	fi

         			if [ ${checktreeinfo} -eq 0 ];then
        		    		# verify treeinfo        
        		    		verify_treeinfo $PkgUrl $CurrentArch $SKU
                            		checktreeinfo=1
        			fi

	              		verify_package_consistency $repoid $PkgUrl $pkgmf

				verify_packages_full_installation $repoid
				;;
	 		level2,level3)
                		verify_productcert_installation $repoid $pid

                		verify_packages_full_installation $repoid
				;;
	 		level1,level2,level3)
                        	if [[ $checklisting == *0* ]]
                        	then
                              		verify_listing_files $PkgUrl
                              		checklisting=1
                        	fi

        			if [ ${checktreeinfo} -eq 0 ];then
        		    		# verify treeinfo        
        		    		verify_treeinfo $PkgUrl $CurrentArch $SKU
                            		checktreeinfo=1
        			fi
			
                		verify_package_consistency $repoid $PkgUrl $pkgmf
                
                		verify_productcert_installation $repoid $pid

                		verify_packages_full_installation $repoid
				;;
			* )
				d_echo "please kindly give me a correct 'level' to test."
		esac

    	done < $testrepo
	d_echo "Content validation for each effective repo of PID $pid End"	
    done          
    d_echo "Content validation for each product of the subscription End"
           
     unregister
     is_registered && fail

     echo "*******************************************************"
     echo "*******************************************************"
     echo "*******************************************************"
     echo "*******************************************************"
     rm -f $tmp
     rm -f $testrepo
}
     
     #Main
     echo "*******************************************************"
     echo "********** Content Test Preparation "
     echo "*******************************************************"
     User=$1
     PWD=$2
     SKU=$3
     PID=$4
     content_level=$5
     relserver=$6
     type=$7 

     #clean up
     subscription-manager unregister
     subscription-manager clean
     rm -f *.pem
     #delete rhn debuginfo repo to remove affect
     rm -f $(ls /etc/yum.repos.d/* | grep -v  "redhat.repo")

     #get current release version
     __CurrentRelVer=$(python -c "import yum; yb = yum.YumBase(); print(yb.conf.yumvar)['releasever']")  
     echo  $__CurrentRelVer|grep 'Loaded plugins:'
     if [ $? -eq 0 ];then
         _CurrentRelVer=`echo ${__CurrentRelVer}|sed -e "s/\n/ /"`
         CurrentRelVer=${_CurrentRelVer##* }
     fi
     echo "Current Release Version is $CurrentRelVer"
     
     #get current base architecture
     __CurrentArch=$(python -c "import yum; yb = yum.YumBase(); print(yb.conf.yumvar)['basearch']")
     echo  $__CurrentArch |grep 'Loaded plugins:'
     if [ $? -eq 0 ];then
         _CurrentArch=`echo ${__CurrentArch}|sed -e "s/\n/ /"`
         CurrentArch=${_CurrentArch##* }
     fi
     echo "Current Achitecture is $CurrentArch"

     echo "*******************************************************"
     echo "********** Content Test Start "
     echo "*******************************************************"
     content_test $CurrentRelVer $CurrentArch $content_level $relserver 
     echo "*******************************************************"
     echo "********** Content Test End "
     echo "*******************************************************"
     rm -f *.pem
     exit

