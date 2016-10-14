#! /bin/bash
##
# common functions and variables for content testing
# requirements:
#     username, password, SKU, PID, content_level, repomanifest, relserver
# Usage:
#      bash rhsm_content_resource.sh username password SKU PID content_level  relserver
#      e.g.
#      bash rhsm_content_resource.sh stage_test_12 redhat RH0103708 69 level1,level2  beta
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
    cmd="subscription-manager register --username=$_username --password=$_pwd" 
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
#@ repomanifest
##
function verify_repomanifest(){
    d_echo "********** Step3. level1-1 Verify Consumed Reposlist According To Subscription Start "
    repomf=$1
    
    d_echo "Get Consumed Repolist "
    consumedrepolist=$(mktemp)
    yum repolist all | sed -n '/repo id/{:a;n;/repolist:/q;p;ba}' | awk -F' ' '{print $1}' > $consumedrepolist
    cat $consumedrepolist
   
    d_echo "Display Given Repo manifest"
    cat $repomf

    d_echo "Compare Consumed Repolist with Given Repo manifest"
    invalid_repos=$(mktemp)
    while read repo
    do
	grep $repo $repomf >> /dev/null
	if [ $? -ne 0 ]
        then
             echo "$repo is invalid in consumed repolist." >> $invalid_repos
        fi
    done < $consumedrepolist

    invlaid_len=$(cat $invalid_repos | wc -l)
    if [ $invlaid_len -ne 0 ]
    then
         cat $invalid_repos
         d_echo  "Verify Consumed Reposlist: --- FAIL "
         rm -f $consumedrepolist
	 rm -f $invalid_repos
         unregister
         exit
    fi
    rm -f $invalid_repos 

    missing_repos=$(mktemp)
    while read repo
    do
        grep $repo $consumedrepolist >> /dev/null
        if [ $? -ne 0 ]
        then
             d_echo "$repo is missing in consumed repolist." >> $missing_repos
        fi
    done < $repomf

    missing_len=$(cat $missing_repos | wc -l)
    if [ $missing_len -ne 0 ]
    then
         cat $missing_repos
         d_echo  "Verify Consumed Reposlist: --- FAIL "
         rm -f $consumedrepolist
         rm -f $missing_repos
         unregister
         exit
    fi
    rm -f $missing_repos

    d_echo "Verify Consumed Reposlist: --- PASS "
    d_echo "********** Step3. level1-1 Verify consumed reposlist according to subscription End "
    rm -f $consumedrepolist
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
# enable all repos
##
function enable_allrepo(){
    yum_repolist
    
    for line in $(grep -n "^\[rhel\-" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')
    do
        sed -i "$(($line+3)) s/0/1/" /etc/yum.repos.d/redhat.repo
    done

    d_echo  "Display All Enabled Repos "
    yum_repolist
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
    rellistingurl=$(echo $url | sed "s/$CurrentRelServer.*$/listing/")
    d_echo "Get Release Version listing file from $rellistingurl "
    cmd="curl --cert $(ls *.pem | grep -v key.pem) --key $(ls *.pem | grep key.pem) -k $rellistingurl"
    d_echo "$cmd"
    rellisting=$($cmd)
    rellisting=$(echo $rellisting)
    echo "Release Version listing file contains $rellisting"

    reldirurl=$(echo $url | sed -e "s/https/http/" -e "s/$CurrentRelServer.*$//" )
    d_echo "Get Release Version Sibling Directories from $reldirurl"
    cmd="curl --cert $(ls *.pem | grep -v key.pem) --key $(ls *.pem | grep key.pem) -k $reldirurl > /tmp/reldirs"
    d_echo "$cmd"
    eval $cmd
    reldirs=$(sed -e '/Parent/d' -e '/\.old/d' /tmp/reldirs | grep DIR | awk '{print $5}' | awk -F '"' '{print $2}' | sed 's/\///' )
 
    #handle releasing directory according to bug 785989
    if [[ $CurrentRelServer == *5* ]]
    then
        reldirs=$(echo $reldirs | sed "s/^.*5.7/5.7/")
    elif [[ $CurrentRelServer == *6* ]]
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
    cmd="curl --cert $(ls *.pem | grep -v key.pem) --key $(ls *.pem | grep key.pem) -k $archlistingurl"
    d_echo "$cmd"
    archlisting=$($cmd)
    echo "Arch listing file contains $archlisting"

    archdirurl=$(echo $url | sed -e "s/https/http/" -e "s/$CurrentArch.*$//")
    d_echo "Get Arch Sibling Directories from $archdirurl"
    cmd="curl --cert $(ls *.pem | grep -v key.pem) --key $(ls *.pem | grep key.pem) -k $archdirurl > /tmp/archdirs"
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
    cmd="curl --cert $(ls *.pem | grep -v key.pem) --key $(ls *.pem | grep key.pem) -k $PkgUrl > $pkgtmp"
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
# @repoid
##
function install_package(){
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
            grep "No Match" tmp
            wrong=$?
        else
     	    d_echo "Install The Selected Package $pkgname "
     	    cmd="yum -y install $pkgname"
     	    d_echo "$cmd"
     	    eval $cmd|tee tmp
     	    grep "Complete\!" tmp
     	    right=$?
     	    grep "Error:" tmp
     	    wrong=$?
        fi

     	if [ $right -eq 0 ] && [ $wrong -ne 0 ]
     	then
        	 d_echo "Install Package $pkgname: --- PASS "
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
function install_all_available_pkgs(){
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
#  content test
# @ repomanifest
# @ currentrelserver
# @ currentarch
# @ content_level: level1, level2 or level3, or level1,level2
# @ relserver: dist or beta
##
function content_test()
{ 
     register $User $PWD
     tmp=$(mktemp)
     list_avail | tee $tmp
     subscribe_pool $SKU
     verify_entitlement $SKU  
     #verify repo manifest 
     if [[ $content_level == *level1* ]]
     then
	    verify_repomanifest $repomanifest
     fi
     
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
     
     check_and_subscribe_baseproduct $SKU
     yum_clean_cache
     yum_repolist
     #enable all test repos
     enable_all_testrepos $testrepo

     #content verify for each effective repo start     
     checklisting=0
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
	

	case $content_level in
        	level1)
                        if [[ $checklisting == *0* ]]
			then
				verify_listing_files $PkgUrl
				checklisting=1
			fi

                        pkgmanifest=$repoid'_packages.txt'
			verify_content $repoid $PkgUrl $pkgmanifest
			;;
         	level2)
			install_package $repoid
			#verify_productId $PID
			;;
         	level3)
			install_all_available_pkgs $repoid
			;;
         	level1,level2)
                        if [[ $checklisting == *0* ]]
                        then
                                verify_listing_files $PkgUrl
                                checklisting=1
                        fi

                	verify_content $repoid $PkgUrl

                	install_package $repoid
                	#verify_productId $PID
			;;
	 	level1,level3)
                        if [[ $checklisting == *0* ]]
                        then
                                verify_listing_files $PkgUrl
                                checklisting=1
                        fi

                	verify_content $repoid $PkgUrl

			install_all_available_pkgs $repoid
			;;
	 	level2,level3)
                	install_package $repoid
                	#verify_productId $PID

                	install_all_available_pkgs $repoid
			;;
	 	level1,level2,level3)
                        if [[ $checklisting == *0* ]]
                        then
                                verify_listing_files $PkgUrl
                                checklisting=1
                        fi

                	verify_content $repoid $PkgUrl
                
                	install_package $repoid
                	#verify_productId $PID

                	install_all_available_pkgs $repoid
			;;
		* )
			d_echo "please kindly give me a correct 'level' to test."
	esac

    done < $testrepo

    if [[ $content_level == *level2* ]]
    then
	pidlist=$(echo $PID | awk -F',' '{for(i=1;i<=NF;i++) print $i}')
     	for pid in $pidlist;
     	do
		verify_productId $pid
     	done          
    fi
    #content verify for each effective repo end
           
     unregister
     is_registered && fail

     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     rm -f $tmp
     rm -f $testrepo

}
     
     #Main
     d_echo "**************************************************"
     d_echo "********** Content Test Preparation "
     d_echo "**************************************************"
     User=$1
     PWD=$2
     SKU=$3
     PID=$4
     content_level=$5
     relserver=$6

     #clean up
     subscription-manager unregister
     subscription-manager clean
     rm -f *.pem
     #delete rhn debuginfo repo to remove affect
     rm -f $(ls /etc/yum.repos.d/* | grep -v  "redhat.repo")

     #get original repo manifest
     orgrepomanifest=$(mktemp)
     pidlist=$(echo $PID | awk -F',' '{for(i=1;i<=NF;i++) print $i}')
     for pid in $pidlist;
     do
                cat /tmp/contenttest/$pid.txt >> $orgrepomanifest
     done

     #get current release server and current architecture
     CurrentRelServer=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'releasever' | awk -F":" '{print $2}' | sed  -e "s/^ '//" -e "s/'}$//" -e "s/',$//")      
     relversion=$(echo $CurrentRelServer | grep -Eo '^[0-9]')
     echo "Current Release Version is $CurrentRelServer"
     repomanifest=$(mktemp)
     grep "rhel\-$relversion" $orgrepomanifest | sed -e "s/^ *//" -e "s/ *$//" > $repomanifest

     CurrentArch=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'basearch' | awk -F":" '{print $2}' | sed -e "s/'//" -e "s/',//" -e "s/^ //" -e "s/$ //")
     repomanifest=$(mktemp)
     echo "Current Achitecture is $CurrentArch"
     if [[ $CurrentArch == *ppc* ]]
     then
	grep "rhel\-$relversion" $orgrepomanifest| grep "power" | sed -e "s/^ *//" -e "s/ *$//" > $repomanifest
     else
	grep "rhel\-$relversion" $orgrepomanifest| grep -v "power" | sed -e "s/^ *//" -e "s/ *$//" > $repomanifest
     fi
     
     d_echo "**************************************************"
     d_echo "********** Content Test Start "
     d_echo "**************************************************"
     content_test $repomanifest $CurrentRelServer $CurrentArch $content_level $relserver
     d_echo "**************************************************"
     d_echo "********** Content Test End "
     d_echo "**************************************************"
     rm -f $repomanifest
     rm -f $orgrepomanifest
     rm -f *.pem
     exit

