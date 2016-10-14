import os, re, logging
from autotest_lib.client.common_lib import error
from autotest_lib.client.virt import aexpect

def run_qemu_io(test, params, env):
    """
    Run qemu_iotests.sh script:
    1) Do some qemu_io operations(write & read etc.)
    2) Check whether qcow image file is corrupted

    @param test:   kvm test object
    @param params: Dictionary with the test parameters
    @param env:    Dictionary with test environment.
    """
    test_script = os.path.join(test.bindir, 'scripts/qemu_iotests.sh')
    logging.info("Running script now: %s" % test_script)
    test_image = params.get("test_image", "/tmp/test.qcow2")
    s, test_result = aexpect.run_fg("sh %s %s" % (test_script,
                                                         test_image),
                                           logging.debug, timeout = 1800)

    err_string = {
       "err_nums":    "\d errors were found on the image.",
       "an_err":      "An error occurred during the check",
       "unsupt_err":  "This image format does not support checks",
       "mem_err":     "Not enough memory",
       "open_err":    "Could not open",
       "fmt_err":     "Unknown file format",
       "commit_err":  "Error while committing image",
       "bootable_err":  "no bootable device",
       }

    for err_type in err_string.keys():
        msg = re.findall(err_string.get(err_type), test_result)
        if msg:
            raise error.TestFail, msg
