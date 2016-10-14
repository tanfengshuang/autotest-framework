# Unstable Loop Implementation:
# 1) Pull new modifications from svn/git
# 2) Execute the loop test
# 3) Gathering the result and send the email

import os, commands, sys, re, socket

try:
    staf_kvm_path = sys.argv[1]
    kvm_autotest_path = sys.argv[2]
    test_cmd = sys.argv[3]
    mail_list = sys.argv[4]
    pull_cmd = sys.argv[5]
    subject = sys.argv[6]
except:
    print 'usage: %s path-of-staf-kvm path-of-kvm-autotest ' \
          'test-command mailing-list pull-command mail-subject' % sys.argv[0]
    sys.exit(1)

print 'Verifying the status'
if not os.path.exists(staf_kvm_path):
    print '%s not exist' % staf_kvm_path
    sys.exit(1)
if not os.path.exists(kvm_autotest_path):
    print '%s not exist' % kvm_autotest_path
    sys.exit(1)

print 'Pull new modifications for kvm-autotest'
os.chdir(kvm_autotest_path)
commands.getstatusoutput(pull_cmd)
s, o = commands.getstatusoutput("git log | grep commit")
staf_kvm_version = re.findall("commit(.*)", o)[0]
print 'staf-kvm version %s' % staf_kvm_version

print 'Pull new modifications for staf-kvm'
os.chdir(staf_kvm_path)
commands.getstatusoutput(pull_cmd)
s, o = commands.getstatusoutput("git log | grep commit")
autotest_version = re.findall("commit(.*)", o)[0]
print 'staf-kvm version %s' % autotest_version

print 'execute the test command %s' % test_cmd
s, start_date = commands.getstatusoutput("date")
os.system(test_cmd)
s, end_date = commands.getstatusoutput("date")

print 'Gather the result and send the email'
kvm_autotest_path = os.path.join(kvm_autotest_path,"client/tests/kvm")
os.chdir(kvm_autotest_path)

result_filename = "/tmp/result"
if os.path.exists(result_filename):
    os.unlink(result_filename)

result_file = file(result_filename, "a+")
hostname = socket.gethostname()
kvm_version = file("/sys/module/kvm/version").read()
s, kernel_version = commands.getstatusoutput("uname -r")

result_file.write("[Host Attribute]\n\n")
result_file.write("hostname = %s \n" % hostname)
result_file.write("kvm_version = %s \n" % kvm_version)
result_file.write("kernel_version = %s \n" % kernel_version)
result_file.write("start time = %s \n" % start_date)
result_file.write("finish time = %s \n" % end_date)
result_file.write("staf-kvm commit: %s\n" % staf_kvm_version)
result_file.write("autotest commit: %s\n" % autotest_version)
result_file.write("test command: %s\n" % test_cmd)
result_file.write("\n\n[Test Result]\n\n")

print result_file.read()

s, o = commands.getstatusoutput("./scan_results.py >> %s" % result_filename)
os.system("mail -s %s-%s %s < %s" % (hostname, subject,
                                     mail_list, result_filename))





