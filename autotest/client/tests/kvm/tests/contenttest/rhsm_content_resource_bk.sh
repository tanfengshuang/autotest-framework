#! /bin/bash
###
# common functions and variables for content testing
# requirements:
#     rhsm_<product>_content_verify.conf
# common functions:
#     1. Register
#     2. Subscribe (according to ProductIds in rhsm_<product>_content_verify.conf)
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

function pass() {
    d_echo "********** PASS "
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
# check the system subscribe or not
##
function is_subscribed() {
    cmd="subscription-manager list --consumed"
    eval $cmd
    (ls /etc/pki/entitlement/ | grep -v key.pem) && return 0
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
         return 1    
    else 
         d_echo "Product $prd_id is not subscribed" && fail
    fi
}

##
# Is repomd.xml contain pkgs
#$pkglist
##
function is_contained_pkgs() {
    pkglistlen=$(cat $pkglist | wc -l)
    if [ $pkglistlen -ne 0 ]
    then
         d_echo "repomd.xml list $pkglistlen packages!!!"
    else
         d_echo "repomd.xml have no pkgs!!!"
    fi
}

##
# Is Packages directory contain rpms content
# $pkgcontent
##
function is_contained_content() {
    rpmpkglen=$(grep "RPM package" $pkgcontent | wc -l)
    if [ $rpmpkglen -ne 0 ]
    then
         d_echo "Packages directory contain $rpmpkglen packages!!!"
    else
         d_echo "Packages directory have no rpms content!!!"
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
    d_echo $cmd
    eval $cmd
    is_registered
    if [ $? -ne 0 ] 
    then 
	d_echo "Fail to register the system to server." 
    else
	d_echo "Successfully register the system to server."
    fi
    d_echo "********** Step1. Register End "
}

##
# list available subscriptions
##
function list_avail() {
    cmd="subscription-manager list --available"
    d_echo $cmd
    eval $cmd
}

function list_avail2() {
    d_echo "List Available Pool"
    cmd="subscription-manager list --available"
    d_echo $cmd
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
    eval $cmd
    d_echo "********** Step4. Unregister End "
}

function subscribe_pool(){
    local sku
    sku=$1
    d_echo "********** Step2. Subscribe to a Pool Start "
    prd_id=$(echo $sku | grep '^ *' | awk -F"," '{print $1}')
    pool_id=""
    pool_id=$(grep --max-count=1 -A 1 $prd_id $tmp | awk -F":" '/PoolId/{print $2;}' | sed 's/^[ \t]*//;s/[ \t]*$//')
    if [ $pool_id'X' = 'X' ]
    then
        d_echo "no SKU=$prd_id available. To confirm, run subscription-manager list --available" && fail
    else
        d_echo "Subscribing to poolId $pool_id (PId=$prd_id)"
        cmd="subscription-manager subscribe --pool=$pool_id"
        d_echo "$cmd"
        eval $cmd
        is_subscribed_prd $prd_id
    fi
    d_echo "********** Step2. Subscirbe to a Pool End "
}

##
# check whether the system need subscribe to a baseproduct
##
function check_and_subscribe_baseproduct(){
    local prdid
    prdid=$1
    d_echo "********** Step2.5 Check and Subscribe the Base Product Start "
    sku2=$(echo $prdid | awk -F"," '{print $2}')
    if [ $sku2'X' = 'X' ]
    then
        d_echo "no base product"
    else
        tmp=$(mktemp)
        list_avail2 | tee $tmp
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
    d_echo "********** Step2.5 Check and Subscribe the Base Product End "
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
     d_echo "********** Step2.5 Verify SKU and PID in Entitlement Cert Start "
     prd_id=$(echo $sku | grep '^ *' | awk -F"," '{print $1}')
     #echo "prd_id" + $prd_id
     result1=$(for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i;done | grep $prd_id)
     result2=$(for i in $(ls /etc/pki/entitlement/ | grep -v key.pem); do openssl x509 -text -noout -in /etc/pki/entitlement/$i;done | grep --max-count=1 -A 1 ${str}${PID})
     if [ $result1'X' != 'X' ]	
     then 
         d_echo "Verify SKU in entitlement,SKU:$prd_id---PASS"
     else
         d_echo "Verify SKU in entitlement,SKU:$prd_id---FAIL" 
     fi
     if [[ -n "$result2" ]] 
     then 
	 d_echo "Verify PID in entitlement cert,PID:$PID---PASS"
     else
         d_echo "Verify PID in entitlement cert,PID:$PID---FAIL" 
     fi
     d_echo "********** Step2.5 Verify SKU and PID in Entitlement Cert End "
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
# enable betarepo and disable productrepo
##
function enable_betarepo_and_disable_productrepo(){
    d_echo "********** Step3.0. Disable Distrepo And Enable Betarepo Start "
    yum_repolist
    #cmd="yum-config-manager --disable $REPO"
    #echo $cmd
    #eval $cmd
    betarepo=$1
    echo "betarepo is $betarepo"
    repo=$(echo $1 | sed "s/-beta//")
    echo "repo is $repo"

    line=$(($(grep -n "^\[$repo\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+3))
    sed -i "$line s/1/0/" /etc/yum.repos.d/redhat.repo

    #cmd="yum-config-manager --enable $BETAREPO"
    #echo $cmd
    #eval $cmd
    line=$(($(grep -n "^\[$betarepo\]" /etc/yum.repos.d/redhat.repo | awk -F":" '{print $1}')+3))
    sed -i "$line s/0/1/" /etc/yum.repos.d/redhat.repo
    d_echo "display repos and packages"
    yum_repolist
    d_echo "********** Step3.0. Disable Distrepo And Enable Betarepo End "
}

##
# verify two "listing file"
# @url
##
function verify_listing_files(){
    d_echo "********** Step3. Level1-1 Verify Listing Files Start "
    url=$1
    #get release listing file
    rellistingurl=$(echo $url |sed "s/$(echo $url | awk -F"/" '{print $9}')/listing/")
    cmd="curl --cert $(ls /etc/pki/entitlement/* | grep -v key.pem) --key $(ls /etc/pki/entitlement/* | grep key.pem) -k $rellistingurl"
    d_echo "$cmd"
    rellisting=$($cmd)

    #get release directories
    reldirurl=$(echo $url |sed "s/$(echo $url | awk -F"/" '{print $9}')//" )
    cmd="curl --cert $(ls /etc/pki/entitlement/* | grep -v key.pem) --key $(ls /etc/pki/entitlement/* | grep key.pem) -k $reldirurl > /tmp/reldirs"
    d_echo "$cmd"
    eval $cmd
    reldirs=$(sed -e '/Parent/d' -e '/\.old/d' /tmp/reldirs | grep DIR | awk '{print $5}' | awk -F '"' '{print $2}' | sed 's/\///' )

    #check rellisting file
    if [[ "$reldirs" = "$rellisting" ]]
    then
        d_echo "Verify Release Listing Files Pass"
    else
        d_echo "Verify Release Listing Files Fail"
    fi

    #get arch listing file
    archlistingurl=$(echo $url | sed 's/$/\/listing/')
    cmd="curl --cert $(ls /etc/pki/entitlement/* | grep -v key.pem) --key $(ls /etc/pki/entitlement/* | grep key.pem) -k $archlistingurl"
    d_echo "$cmd"
    archlisting=$($cmd)

    #get arch directories
    archdirurl=$(echo $url | sed 's/$/\//')
    cmd="curl --cert $(ls /etc/pki/entitlement/* | grep -v key.pem) --key $(ls /etc/pki/entitlement/* | grep key.pem) -k $archdirurl > /tmp/archdirs"
    d_echo "$cmd"
    eval $cmd
    archdirs=$(sed -e '/Parent/d' /tmp/archdirs | grep DIR | awk '{print $5}' | awk -F '"' '{print $2}' | sed 's/\///'| sort )
    
    #check archlisting file
    if [[ "$archdirs" = "$archlisting" ]]
    then
        d_echo "Verify Arch Listing Files Pass"
    else
        d_echo "Verify Arch Listing Files Fail"
    fi	
    d_echo "********** Step3. Level1-1 Verify Listing Files End "
    rm -f /tmp/reldirs
    rm -f /tmp/archdirs
}

##
# @ $repoid
# @Pkgurl
##
function verify_content(){
    d_echo "********** Step3. Level1-2 Verify Package Content Start "
    
    repoid=$1	
    PkgUrl=$2
    d_echo "Get Available Pkglist Name" 
    pkglist=$(mktemp)
    cmd="repoquery --show-dupes --all --repoid=$repoid --qf "%{name}-%{version}-%{release}.%{arch}" | sed \s/$/\.rpm/ > $pkglist"
    d_echo "$cmd"
    eval $cmd

    d_echo "Check Pkg List"
    is_contained_pkgs $pkglist
    
    d_echo "Get Available Pkg rpms Content"
    pkgcontent=$(mktemp)
    cmd="curl --cert $(ls /etc/pki/entitlement/* | grep -v key.pem) --key $(ls /etc/pki/entitlement/* | grep key.pem) -k $PkgUrl > $pkgcontent"
    d_echo "$cmd"
    eval $cmd

    d_echo "Check Pkgs Content"
    is_contained_content $pkgcontent

    d_echo "Verify rpms Content"
    pkginvalid=$(mktemp)
    while read line
    do
          grep $line $pkgcontent > /dev/null
          if [ $? -ne 0 ];
          then
                d_echo $line "do not find!!!"
                d_echo $line >> $pkginvalid
          fi
    done < $pkglist

    cat $pkginvalid
    d_echo "Above $(cat $pkginvalid | wc -l) pkgs could not find in Packages Directory!" 

    d_echo "********** Step3. Level1-2 Verify Content Packages End "
    rm -f $pkgcontent
    rm -f $pkglist
    rm -f $pkginvalid
}

##
# @repoid
##
function install_package(){
    d_echo "********** Step3. Level2-1 Install Package Start "
    #random get one package to be installed
    repoid=$1
    cmd="yum list available"
    repolist=$(yum repolist | grep 'rhel-' | grep -v $repoid | awk -F" " '{print $1}')
    for i in $repolist; do cmd=$cmd" --disablerepo=$i";done
    echo $cmd
    file=$(mktemp)
    eval $cmd > $file
    
    #get available packages to install
    cat $file | awk -F" " 'BEGIN{i=0;}{++i; if(i>3) print $1;}' | sed -e 's/\.i386//' -e 's/\.x86_64//' -e 's/\.i686//' -e '/^[0-9]/d' | sort -u > $file

    total=$(awk 'END{print NR}' $file)
    if [[ $total -ne 0 ]]
    then
    	num=$(($RANDOM%$total))
	rnum=$(($num + 1))
    	pkgname=$(sed -n "$rnum p" $file)
     	#install the selected package
     	cmd="yum -y install $pkgname"
     	echo $cmd
     	eval $cmd|tee tmp
     	grep "Complete\!" tmp
     	right=$?
     	grep "Error:" tmp
     	wrong=$?
     	if [ $right -eq 0 ] && [ $wrong -ne 0 ]
     	then
        	 d_echo "Install package PASS: $pkgname is installed successfully"
     	else
        	 d_echo "Install package FAIL: $pkgname could not be installed"
     	fi
     	rm -f tmp

    else
        d_echo "There is no package to install"
    fi

    d_echo "********** Step3. Level2-2 Install Package End "
}

function verify_productId(){
     d_echo "********** Step3. Level2-3 Verify PID in Product Cert Start "
     local i
     str="1.3.6.1.4.1.2312.9.1."
     result3=$(for i in /etc/pki/product/*;do openssl x509 -text -noout -in $i;done | grep ${str}${PID})
     if [[ -n "$result3" ]]  
     then
	 d_echo "Verify PID in product cert,PID:$PID---PASS"
     else
         d_echo "Verify PID in product cert,PID:$PID---FAIL" 
     fi
     d_echo "********** Step3. Level2-3 Verify PID in Product Cert End "
}

##
# @repoid
##
function install_all_available_pkgs(){
     d_echo "********** Step3. Level3 Install All Available Packages Start "
     REPOID=$1
     file=$(mktemp)
     repoquery -a --repoid=$REPOID --qf "%{name}" | sort -u > $file
     total=$(awk 'END{print NR}' $file)

     #the number of packages to be installed per iteration
     step=20
     i=1
     while [ $i -le $total ]
     do
	     d_echo "[$(date "+%F %T")]  #$i yum install -y --skip-broken $(sed -n $i,$((i+step))p $file)#"
    	 yum install -y --skip-broken $(sed -n $i,$((i+step))p $file) | grep -v "already installed and latest version"
    	 i=$((i+step))
     done

     rm $file
     d_echo "********** Step3. Level3 Install All Available Packages End "
}

##
#  content test
# @1=  level1, level2 or level3, or level1,level2
# @2=  dist or beta
##
function content_test()
{    
     register $User $PWD
     check_and_subscribe_baseproduct $SKU
     tmp=$(mktemp)
     list_avail | tee $tmp
     subscribe_pool $SKU
     verify_entitlement $SKU
     yum_clean_cache
     PkgUrl=$1     
     d_echo " the first para is $1 "
     #obtain repoid from third parameter
     d_echo " the third para is $3 "
     repoid=$3
     if [[ $3 == *beta* ]]
     then
            enable_betarepo_and_disable_productrepo $repoid
     else
            yum_repolist
     fi

     d_echo " the second parametar is $2 "
     case $2 in
         level1)
		verify_listing_files $URLPRE
		verify_content $repoid $PkgUrl
		;;
         level2)
		install_package $repoid
		verify_productId $PID
		;;
         level3)
		install_all_available_pkgs $repoid
		;;
         level1,level2)
		verify_listing_files $URLPRE
                verify_content $repoid $PkgUrl

                install_package $repoid
                verify_productId $PID
		;;
	 level1,level3)
		verify_listing_files $URLPRE
                verify_content $repoid $PkgUrl

		install_all_available_pkgs $repoid
		;;
	 level2,level3)
                install_package $repoid
                verify_productId $PID

                install_all_available_pkgs $repoid
		;;
	 level1,level2,level3)
		verify_listing_files $URLPRE
                verify_content $repoid $PkgUrl
                
                install_package $repoid
                verify_productId $PID

                install_all_available_pkgs $repoid
		;;
	* )
		d_echo "please kindly give me a correct 'level' to test."
     esac
           
     unregister
     is_registered && fail
     pass

     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     d_echo "**************************************************"
     rm -f $tmp

}

     #Main
     #Main
     d_echo "**************************************************"
     d_echo "**********Step Setup. Loading Configure File "
     d_echo "**************************************************"
     User=$1
     PWD=$2
     SKU=$3
     PID=$4
     REPO=$5
     predix=$6
     URLEND=$7
     content_level=$8

     CurrentRelServer=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'releasever' | awk -F":" '{print $2}' | sed  -e "s/^ '//" -e "s/'}$//") 
 
    if [[ $CurrentRelServer == *6* ]]
    then
           Release='6'
    elif [[ $CurrentRelServer == *5* ]]
    then
           Release='5'
    else
           d_echo "The machine has no product installed for test, please install one product first!"
           exit
    fi
     URLPRE=$predix/$Release/$CurrentRelServer
     
     CurrentArch=$(python -c "import yum, pprint; yb = yum.YumBase(); pprint.pprint(yb.conf.yumvar, width=1)" | grep 'basearch' | awk -F":" '{print $2}' | sed -e "s/'//" -e "s/',//" -e "s/^ //" -e "s/$ //")
     
     PkgUrl=$URLPRE/$CurrentArch/$URLEND
     d_echo "**************************************************"
     d_echo "********** Content Test Start "
     d_echo "**************************************************"
     content_test $PkgUrl $content_level $REPO
     d_echo "**************************************************"
     d_echo "********** Content Test End "
     d_echo "**************************************************"
     exit

