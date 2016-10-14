import logging,os,commands
from autotest_lib.client.common_lib import error

def run_cpuflags(test,params,env):
    """
    Check guest cpu extension flags supported by host
    1) Log into  guest
    2) Get guest cpu information and host cpu information
    3) Compare with each other make sure host cpu extension flags
       bits contain guest

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = env.get_vm(params["main_vm"])
    vm.verify_alive()
    session = vm.wait_for_login(timeout=int(params.get("login_timeout", 360)))

    get_cpuflags_cmd = params.get("getcpuflags")
    s, o = session.get_command_status_output(get_cpuflags_cmd)
    if s != 0:
        raise error.TestFail, "Could not read guest cpu flags"
    guest_cpuflags_list = o.splitlines()[0].split(':')[1].split()
    host_cpuflags_list = commands.getoutput(get_cpuflags_cmd).\
                         splitlines()[0].split(':')[1].split()

    logging.debug("Host flags %s" % host_cpuflags_list)
    logging.debug("Guest flags %s" % guest_cpuflags_list)

    # There are some special flags, for example 'hypervisor', 'sep',
    # present in guests but not in the hosts, exclude these flags from
    # comparison.
    ban_flags_list = params.get("ban_flags").split()

    guest_cpuflags_set = set(guest_cpuflags_list)
    host_cpuflags_set = set(host_cpuflags_list)

    # If the excluded flags provided by the config file that exist in the
    # host, remove them from the ban_flags_list, because we require kvm
    # virtualize/simulate the host.
    if params.get("strict_check") == "yes":
        for flag in ban_flags_list:
            if flag in host_cpuflags_list:
                ban_flags_list.remove(flag)

    # exclude the banned flags from guest flags set.
    for flag in ban_flags_list:
        if flag in guest_cpuflags_set:
            guest_cpuflags_set.remove(flag)

    if guest_cpuflags_set.issubset(host_cpuflags_set):
        logging.info("Guest cpu flags all supported by host")
    else:
        invalidflags_set = guest_cpuflags_set - host_cpuflags_set
        host_cpuflags_str = str(host_cpuflags_set)[4:-1]
        invalidflags_str = ''
        for i in invalidflags_set:
            if host_cpuflags_str.find(i.strip()) == -1:
                invalidflags_str = invalidflags_str + i + ','

        if invalidflags_str.strip() != '':
            raise error.TestFail("Unsupported cpu flags by host: %s" % \
                                                invalidflags_str[0:-1])

    # check the extra cpuflags in guest.
    extra_flags_set = set(params.get("extra_flags").split())
    if extra_flags_set.issubset(guest_cpuflags_set):
        logging.info("All extra flags are found in guest.")
    else:
        invalidflags_set = extra_flags_set - guest_cpuflags_set
        invalidflags_str = ''
        for i in invalidflags_set:
            invalidflags_str = invalidflags_str + i + ','
        raise error.TestFail("Unsupported extra flags by guest: %s" % \
                                                invalidflags_str[0:-1])

    session.close()
