##@ Summary: Configure Single Test
##@ Description: Single Functional Test
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:    Wed Apr 22, 2009
##@ Version:    2

import sys, re
import wrapper, common

if __name__ == "__main__":

    # Build dict from argv
    dict = wrapper.build_dict_from_argv(sys.argv[1:])

    common.virtlab_parse(dict, argv=sys.argv)

    # Big Loop Fixup
    fixup ="""
"""

    fixup += common.common_parameter_parse(dict)
    fixup += "only full\n"

    testcase = ' '.join(dict.get('testcase').split(','))
    if dict.get('clone') == 'no' or "unattended_install" in dict.get('testcase'):
        fixup += "only %s\n" % testcase
    else:
        fixup += 'variants:\n'
        fixup += '    pre_test:\n'
        fixup += '        only unattended_install.cd.default_install.aio_native'
        fixup += ' rh_kernel_update \n'
        fixup += '    run_test:\n'
        fixup += '        only %s\n' % testcase

    if dict.get('nrepeat'):
        fixup += common.gen_nrepeat_variants(int(dict.get('nrepeat')))

    fixup += 'pre_test:\n'
    fixup += '    only repeat1\n'
    fixup += '    iterations = 1\n'

    # Configure & launch test now
    common.start(fixup, dict)
