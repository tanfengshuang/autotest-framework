import os, shutil, logging
from autotest_lib.client.bin import test, utils
from autotest_lib.client.common_lib import error


class stressapptest(test.test):
    """
    This autotest module runs Stressful Application Test (or
    stressapptest, its unix name), which tries to maximize
    randomized traffic to memory from processor and I/O, with
    the intent of creating a realistic high load situation in
    order to test the existing hardware devices in a computer.

    @author Cao, Chen (kcao@redhat.com)
    @see: http://code.google.com/p/stressapptest/
    """

    version = 1
    def initialize(self):
        """
        Sets the overall failure counter for the test.
        """
        self.nfail = 0


    def setup(self, tarball='stressapptest-1.0.3_autoconf.tar.gz'):
        """
        @param tarball: stressapptest tarball
        """
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)

        os.chdir(self.srcdir)

        utils.system('patch -p1 < ../remove-static-in-configure.diff')
        utils.configure()
        utils.system('make')

        logging.debug('Setup stressapptest good.')


    def run_once(self, args="-C 8 -i 8 -m 8 -s 1200 -W --cc_test"):
        """
        Runs the test, with the appropriate control file.

        For more options to stressapptest, see the man page in src dir.
        Additional "funny" args:
        --force_errors_like_crazy
        --force_errors
        (but these two will make the test failed even on physical machine.)

        -v <level> Verbosity (0-20), default is 8.
        -M <mbytes> Megabytes of RAM to test.
        -A Run in degraded mode on incompatible systems.
        """
        os.chdir(self.srcdir)
        try:
            result = utils.run('./src/stressapptest %s' % args)
            logging.debug(result.stdout)
        except Exception, e:
            logging.error(e)
            self.nfail += 1


    def cleanup(self):
        """
        Cleans up source directory and raises on failure.
        """
        if os.path.isdir(self.srcdir):
            shutil.rmtree(self.srcdir)
        if self.nfail != 0:
            raise error.TestFail('stressapptest suite failed.')
        else:
            logging.info("stressapptest finished.")

