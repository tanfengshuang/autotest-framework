
import os, logging, sys
import env_setup

def get_cpu_num():
    """ get cpu number of host machine """
    cmd = "cat /proc/cpuinfo | grep processor | wc -l"
    ncpu= int(os.popen(cmd).readlines()[0].strip())
    print "number of cpus got: %d" % ncpu
    return ncpu


def get_mem_num():
    """ get the memory number of host machine """
    nmem = 0
    mems = os.popen("dmidecode -t 17 | grep Size").readlines()
    for line in mems:
        m = line.split()[1]
        if m.isdigit():
            nmem += int(m)
    print "number of memories got: %d" % nmem
    return nmem


def get_host_capability():
    max_vcpu = get_cpu_num()
    max_mem = get_mem_num()
    if max_vcpu > 16:
        max_vcpu = 16
    return max_vcpu, max_mem


def common_prepare(dict):
    """ Common preparating routine
    """
    env_dict = env_setup.config_parser(dict)

    # verify the kvm installation
    env_setup.kvm_verify()
    env_setup.autotest_verify()

    # launch ksm
    env_setup.launch_ksm(env_dict)

    # setup directories and links for autotest
    env_setup.directory_setup(env_dict)

    # shutdown iptables in host
    env_setup.stop_iptables()

    # prepare qemu-ifup script
    env_setup.bridge_setup(env_dict)

    # install brewkoji
    env_setup.brewkoji_install()

    # modprobe the vhost module
    os.system("modprobe vhost_net")

    # setup remote machine environment
    # env_setup.remote_machine_setup(env_dict)

