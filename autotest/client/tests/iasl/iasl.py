import os,time,re,shutil
from autotest_lib.client.bin import test, utils
from autotest_lib.client.common_lib import error


class iasl(test.test):
    version = 2

    def setup(self, tarball='iasl.tar.gz'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)

    def initialize(self):
        self.job.require_gcc()
        self.results = []

    def run_once(self, cmd='./iasl-test.sh'):
        os.chdir(self.srcdir)
        utils.system("rm -rf result && mkdir result")
        self.results.append(utils.system_output(cmd,retain_output=True))

    def postprocess_iteration(self):
        try:
            fd = open("result/result-summary.txt","r")
        except IOError:
            error.TestError("Fail to open result/result-summary.txt") 
        lines = fd.readlines()
        fd.close()
        fail_num = 0
        pass_num = 0
        group_num = 0
        for line in lines:
            f = re.findall("Fail tcs: *([0-9]*)", line)
            if f:
                fail_num +=int(f[0])
                group_num += 1
            p = re.findall("Pass tcs: *([0-9]*)", line)
            if p:
                pass_num +=int(p[0])
        total_num = pass_num + fail_num
        summary = """ 
                  SUMMARY:
                  Group num: %d\n
                  Total tcs: %d\n
                  Pass  tcs: %d\n
                  Fail  tcs: %d\n
                  """     % (group_num, total_num, pass_num, fail_num)
        fd = open("result/result-summary.txt","w")
        fd.write(summary)
        fd.writelines(lines)
        fd.close()
        utils.system("rm -rf %s/result" % self.resultsdir)
        utils.system("rm -rf %s/tmp" % self.resultsdir)
        shutil.copytree("result","%s/result" % self.resultsdir)
        shutil.copytree("tmp","%s/tmp" % self.resultsdir)
        if fail_num > 0:
            raise error.TestFail("%s test case(s) failed!" % fail_num)
