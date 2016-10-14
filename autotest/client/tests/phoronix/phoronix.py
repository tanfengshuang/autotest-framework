import os, logging, re
from autotest_lib.client.bin import test, utils
from autotest_lib.client.common_lib import error


class phoronix(test.test):
    version = 1

    def setup(self, tarball='phoronix-test-suite-2.6.1.tar.gz'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)
        os.chdir(self.srcdir)

        # skip user agreement
        utils.system("patch -p1 < ../phoronix-probe.patch")


    def initialize(self):
        self.homedir = os.environ['HOME']
        # prepare config file
        utils.system("mkdir -p %s/.phoronix-test-suite/" % self.homedir)

        usrconfig = os.path.join(self.bindir, "user-config.xml")
        self.cfg = os.path.join(self.homedir,
                                ".phoronix-test-suite/user-config.xml")
        self.results = os.path.join(self.homedir,
                                ".phoronix-test-suite/test-results")
        utils.system("cp -f %s %s" % (usrconfig, self.cfg))

        self.job.require_gcc()
        # php is required by phoronix tests suite
        self.require_php()


    def run_once(self, tests='apache'):
        logging.info("tests to run: %s" % tests)

        if os.path.exists(self.cfg):
            logging.debug("Got config file.")
        else:
            raise error.TestError("No config file for phoronix test suite.")

        os.chdir(self.srcdir)
        self.phoronix_cmd = "./phoronix-test-suite batch_benchmark %s"

        test_list = tests.split()
        for t in test_list:
            self.run_test(t)


    def postprocess(self):
        # make tarball of the results
        os.chdir(self.resultsdir)
        utils.system("for f in `ls`; do tar czvf $f.tgz $f; done")


    def run_test(self, tname):
        logging.info("phoronix %s running..." % tname)
        ret = None
        try:
            ret = utils.run(self.phoronix_cmd % tname)
        except Exception:
            raise error.TestFail("%s failed with output:\n%s",
                                 (self.phoronix_cmd % tname, ret.stdout))

        logging.info("phoronix %s finisded." % tname)

        # rename the result dir and move it to self.resultsdir
        try:
            ret = utils.run("ls %s" % self.results)
        except Exception:
            raise error.TestFail("Failed to list phoronix results dir.")

        matched_result = 0
        res_dir = ""
        for l in ret.stdout.splitlines():
            logging.info(l)
            m = re.match("^\d{4}-\d{2}-\d{2}-\d{4}$", l)
            if m is None:
                continue
            matched_result += 1
            res_dir = l

        if matched_result < 1:
            raise error.TestError("Failed to get %s results." % tname)
        if matched_result > 1:
            raise error.TestError("Unprocessed result found.")

        src_res = os.path.join(self.results, res_dir)
        dst_res = os.path.join(self.resultsdir, tname + res_dir)
        utils.system("mv %s %s" % (src_res, dst_res))


    def require_php(self):
        try:
            utils.run("php --version")
        except Exception:
            raise error.TestError("Test requires php-cli.")

