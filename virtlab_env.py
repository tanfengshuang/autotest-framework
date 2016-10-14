# Virtlab environment related routine

import os, socket, math, re, commands
import logging, kvm_utils


def cfg_generator( pwd, text , name):
    """ generate configuration from text """
    filename = os.path.join(pwd, name)
    f = open(filename, 'w')
    lines = text.splitlines()
    if not (lines[1.0] == ' '):
        print "pure client mode"
        f.write(text)
    else:
        print "Server dispatch mode, indent fixup"
        for line in lines:
            line = line[4:]
            print line
            f.write(line+'\n')
    f.close()

def ksm_probe():
    """ probing the existence of KSM """
    try:
        if os.popen("ksmctl info").readlines()[0].split()[1].strip(',') =='1':
            return 1
        else:
            return 0
    except IndexError:
        return 0
    
def tagname(dict,index,max_instance,case,total,ksm):
    """ Routine to generate tagname of single test
        @index: instance index of paralleling job
        @max_instance: number of instances
        @case: current case no
        @totoal: cases sum
        @ksm: ksmctl status
    """
    if dict.get('logstyle') == 'autotest':
        return dict.get('shortname')
    else:
        format = "%s.Disable.GuestName=%s.memory=%s.vcpus=%s.img_format=%s.multi_guest=%d-%d.test_process=%d-%d.ksm=%d.tag=%s"
        guest_name = dict.get('image_name')[7:]
        if guest_name and "virtio" in guest_name:
            guest_name = guest_name[:-7]
        tagname = format % (dict.get('testcase'),guest_name,dict.get('mem'),dict.get('smp'),dict.get('image_format'),index,max_instance,int(case),int(total),int(ksm),dict.get('shortname'))
    return tagname

# -----------------------------------------------------
# Helper function to seperate prep case from test cases
# -----------------------------------------------------
def case_filter(list, single = True):
    """ Filter preperation routine from test routine
        Return value:
        [ dict list of prep routine, dict list of case routine]
    """
    prep_type = ['guest_install','fastinstall']
    list_prep = []
    list_test = []
    list_image = []

    for dict in list:
        if dict.get('type') in prep_type:
            image_name = dict.get('image_name')
            if not image_name in list_image or single:
                list_image.append(image_name)
                list_prep.append(dict)
        else:
            list_test.append(dict)
    
    return list_prep, list_test

# --------------------------------
# VCPU/Memory paramter calculation
# --------------------------------
def iteration(list_test, ncpu, nmem):
    """ Dynamically generate the iteration of vcpu/memory depends on the host.
        Return value:
        (testcases, max, total)
    """
    max_mem = nmem
    step = 2

    # Adjust the big mode and small mode according to virt-dashborad requirement
    if list_test[0].get('hosttype') == 'big':
        print 'Big Mode'
        vcpu = 4
        mem = 4096
        max_vcpu = ncpu
    else:
        print 'Small Mode'
        vcpu = 1
        mem = 1024
        if ncpu >= 4:
            max_vcpu = 4
        else:
            max_vcpu = ncpu
        max_mem = nmem/2

    logging.debug("max vcpu -> %d max mem -> %d" % (max_vcpu,max_mem))
    
    testcfg = []
    total = 0
    max = 1

    meml = []
    vcpul = []
    
    while mem < max_mem:
        meml.append(mem)
        mem *= step
    meml.append(max_mem)

    while vcpu < max_vcpu:
        vcpul.append(vcpu)
        vcpu *= step
    vcpul.append(max_vcpu)

    for instance in range(1,2):
        for v in vcpul:
            for m in meml:
                logging.debug("cfg %d %d %d" % (instance,v,m))
                if m * instance <= max_mem and v * instance <= max_vcpu:
                    testcfg.append((instance,v,m))
                    logging.debug("succeed")
                    total += len(list_test)
                    if instance > max:
                        max = instance
                else:
                    logging.debug("failed")
    return testcfg, max, total

# -----------------
# Image cloning ...
# -----------------
# FIXME: move this to kvm_autotest in order to be visible in virtlab
def image_clone(list_prep, max ,snapshot = 'no'):
    """ Clone images
        if snapshot == True, use external snapshot
    """

    pwd = os.path.join(os.environ['AUTODIR'],'tests/kvm')
    images = os.path.realpath(pwd)

    for dict in list_prep:
        image_name = os.path.join(images,dict['image_name'])
        for i in range(0,max):
            image_format = dict['image_format']
            dst_name = "%s.%d.%s" % (image_name,i,image_format)
            if snapshot == 'yes' and image_format == 'qcow2':
                logging.debug("Createing snapshot")
                clone_cmd = "qemu-img create -b %s.%s -f qcow2 %s" % (image_name,image_format,dst_name)
                print "create external snapshot %s" % clone_cmd
            else:
                src_name = "%s.%s" % (image_name,dict['image_format'])
                if max == 1:
                    clone_cmd = "mv %s %s" % (src_name, dst_name)
                else:
                    clone_cmd = "cp %s %s" % (src_name, dst_name)
                
                logging.debug("Image cloning")
                if os.system(clone_cmd):
                    print "warning: clone %s failed" % dst_name
                else:
                    print "OK"
                    
