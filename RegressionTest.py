##@ Summary: Regression Test for KVM
##@ Description: Let sing test run with different kvm version
##@ Maintainer: Jason Wang <jasowang@redhat.com>
##@ Updated:    Jan 5th, 2010
##@ Version:    1

import sys
import wrapper, common

if __name__ == "__main__":

    # Build dict from argv
    dict = wrapper.build_dict_from_argv(sys.argv[1:])

    versions = dict.get("versions").split(',')
    testcase = dict.get("testcase")

    # Big Loop Fixup
    fixup ="""
"""

    fixup += common.common_parameter_parse(dict)
    fixup += "only full\n"
    fixup += """
variants:
    - @pre_image:
        only unattended_install.cd.aio_threads"""
    for version in versions:
        string = """
    - %s:
        release = %s
        variants:
            - build:
                only build
            - %s: build
                only %s
""" % (version, version, testcase, testcase)
        fixup += string

    if dict.get('clone') == 'no':
        fixup +="no unattended_install.cd.aio_threads\n"

    # Configure & launch test now
    common.start(fixup, dict)
