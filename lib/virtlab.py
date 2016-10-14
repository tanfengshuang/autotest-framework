#

import os, sys, socket, commands, re
import wrapper, logging, env_setup


def parse_run(dict, argv):
    if dict['virtlab'] != 'yes':
        return
    if not dict['user']:
        dict['user'] = os.environ.get('USER')
    if not dict['profile']:
        o = commands.getoutput("virtlab list_profiles")
        p = "\| (RHEL.*kvm\S*) *\| Success rate:"
        dict['profile'] = re.findall(p, o)[-1]

    cmd = [i for i in argv]
    for i in ['user', 'tree', 'tags', 'profile', 'virtlab']:
        for j in argv:
            if i in j:
                cmd.remove(j)

    content = """<?xml version="1.0" encoding="UTF-8"?>
<virtlab>
<job name="%s-%s-%s-%s-%s-%s" product="RHEV" component="kvm-new"
 need_reboot="True" need_reinstall="True" need_multiple_machine="False">
""" % (dict['guestname'], dict['driveformat'], dict['nicmodel'],
       dict['imageformat'], dict['category'], dict['profile'])
    content += "<profile>%s</profile>\n" % dict['profile']
    content += "<tags>%s</tags>\n" % dict['tags']
    content += """<case name="CustomizedTree">
<parameter name="cmd">python %s</parameter>
<parameter name="tree">%s</parameter>
</case>
</job>
</virtlab>
""" % (' '.join(cmd), dict['tree'])

    f = file("/tmp/virtlab.xml", 'w')
    f.write(content)
    f.close()
    cmd = "virtlab add_job -u %s -f /tmp/virtlab.xml" % dict['user']
    print ''.join(re.findall("Create Job (\d+).", commands.getoutput(cmd)))
    sys.exit()


