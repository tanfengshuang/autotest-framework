##@ Summary: Configure Soak Testing
##@ Description: Configure Loop Testing which guests/platform/hosts type could be chose
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:    Wed Apr 22, 2009
##@ Version:    2
##@ Debug

import sys, os, math, commands
import wrapper, common

if __name__ == "__main__":

    # Build dict from argv
    dict = wrapper.build_dict_from_argv(sys.argv[1:])
    common.virtlab_parse(dict, argv=sys.argv)

    # Big Loop Fixup
    fixup ="""
"""
    if dict.get('runcasein') and dict.get('runcasein')=="guest":
        max_cpu, max_mem = common.get_host_capability()
    else:
        (ret,output)=commands.getstatusoutput("uname -a")
        if "s390" in output or "ppc" in output or "ia64" in output or "aarch64" in output:
            max_cpu, max_mem = 4, 4096
        else:
            max_cpu, max_mem = common.get_host_capability()
            
    dict_loop = {}
    guestname = dict.get('guestname')
#    guestname = dict.get('guestname')
    guestname = "guest_name = "+guestname
    guestname.strip()

    lines = file("autotest/client/tests/kvm/virtlab_tests.cfg").read()
    if not guestname in lines:	
            print guestname
            print "Error: Guest Name not available in virtlab_test.cfg"
            sys.exit(-1)

    category = dict.get('category')
    function_loop = False

    if category not in ['acceptance_test_rhel5','acceptance_test_rhel6','regression']:
        fixup += common.common_parameter_parse(dict, function_loop)
    else:
        if dict.get('srchost') != '0.0.0.0':
            fixup += "srchost = %s\n" % dict.get('srchost')
    

    if category != 'all':
        try:
            lines = file("desc/%s.desc" % category).readlines()
        except:
            print "Warning: Could not found corresponding desc file!"
            sys.exit(-1)

        f = ''.join(lines)
        f = f.replace("{max_mem}", str(max_mem))
        fixup += f.replace("{max_cpu}", str(max_cpu))

        # looping strategy
        loop_type = dict.get('loop_type', 'fixed')
        if loop_type == 'fixed':
            mid_cpu = int(math.pow(2, math.ceil(math.log(max_cpu / 2, 2))))
            mem_g = max_mem / 1024
            mem_g = int(math.pow(2, math.ceil(math.log(mem_g / 2, 2))))
            mid_mem = mem_g * 1024
            if category == "function_all" or category == "function_base":
                function_loop = True
                if max_mem >= 8192 and max_cpu >= 4:
                    fixup += """
variants:
    - smp%s.%sm:
        smp = %s
        mem = %s
    - smp%s.%sm:
        smp = %s
        mem = %s
""" % (max_cpu, max_mem, max_cpu, max_mem, mid_cpu, mid_mem, mid_cpu, mid_mem)
                else:
                    fixup += """
variants:
    - smp2.4096m:
        smp = 2
        mem = 4096
"""
        elif loop_type == 'classic3':
            # max, middle and min (vcpu_nr, mem_sz)
            smp_mem_set = set([(max_cpu, max_mem)])

            try:
                mid_cpu = int(math.pow(2, math.ceil(math.log(max_cpu / 2, 2))))

                mem_g = max_mem / 1024
                mem_g = int(math.pow(2, math.ceil(math.log(mem_g / 2, 2))))
                mid_mem = mem_g * 1024

                smp_mem_set.add((mid_cpu, mid_mem))
            except ValueError:
                # max_cpu / 2 == 0 or mem_g / 2 == 0 will cause
                # math.log throw 'math domain error',
                # we ignore this.
                pass

            smp_mem_set.add((1, 1024))

            smp_mem_list = sorted(smp_mem_set, reverse=True)
            fixup += """
variants:"""
            for smp_mem in smp_mem_list:
                fixup += """
    - smp%d.%dm:
        smp = %d
        mem = %d
""" % (smp_mem[0], smp_mem[1], smp_mem[0], smp_mem[1])

        else:
            fixup += common.add_loop_variants('smp', 1, max_cpu, multiplier=2)
            fixup += common.add_loop_variants('mem', 512, max_mem, multiplier=4)

    if category == 'acceptance_test' and dict.get('bridge') != None:
        fixup += "script = scripts/qemu-ifup-%s\n" % dict.get('bridge')

    if dict['nrepeat']:
        fixup += common.gen_nrepeat_variants(int(dict.get('nrepeat')))

    if dict.get('clone') == 'no':
        fixup += 'no unattended_install.cd\n'
    else:
        fixup += 'unattended_install.cd:\n'
        fixup += '    only repeat1\n'
        fixup += '    iterations = 1\n'

    # Configure & launch test now
    common.start(fixup, dict)
