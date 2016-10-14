import os, re, shelve

from autotest_lib.client.bin import utils, test

class ffsb(test.test):
    version = 6

    # http://sourceforge.net/projects/ffsb/
    def setup(self, tarball='ffsb-6.0-rc2.tar.bz2'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)
        os.chdir(self.srcdir)

        utils.system('patch -p1 < ../ffsb_runtime.patch')
        utils.configure()
        utils.system('make')


    def initialize(self):
        self.job.require_gcc()
        self.results = []
        self.ffsb = os.path.join(self.srcdir, 'ffsb')
        if not os.path.isdir("/mnt/fstest"):
            os.mkdir("/mnt/fstest")


    def run_once(self, dir='.', seconds=360):
        loadfile = os.path.join(self.srcdir, 'examples/profile_everything')
        cmd = '%s %s' % (self.ffsb, loadfile)
        self.results = utils.system_output(cmd, retain_output=True)


    def postprocess_iteration(self):
        print self.resultsdir
        fd = file("%s/ffsb.result" % self.resultsdir, "w+")
        record_flag = 0
        for i in re.split('\n+', self.results):
            if record_flag == 1:
                fd.write("%s\n" % i)
            if re.match('Results:', i):
                record_flag = 1
        fd.close()
