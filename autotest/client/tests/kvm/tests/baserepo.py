import commands


class baserepo():
    def __init__(self):
        self.rversion = ""
        self.rfile = "/etc/redhat-release"
        self.details = ""
        self.archd = ""
        self.baseurl = ""
        self.tailurl = ""

    def process(self):
        # Reading release variant from /etc/redhat-release
        with open(self.rfile) as releasefile:
            self.details = releasefile.readline()
        self.details = self.details.split()
        # Baseurl configure for  GA and Beta release
        #if 'Beta' in self.details:
        #        self.tailurl = "beta-rpms"
        #else:
        self.tailurl = "rpms"
        
        # Reading arch detail from  "uname -a " command
        self.archd = commands.getstatusoutput("uname -a")
        if self.archd[0] != 0:
            print ("uname -a ended with non zero")
        # configure base repourl for aarch64  arch
        if 'aarch64' in self.archd[1]:
            if self.details[4] == "Server" and ('Development Preview' in ' '.join(self.details)):
            	self.baseurl = "rhel-server-for-arm-development-preview-rpms"
            	
            elif self.details[4] == "Server":
                # "/etc/redhat-release" entry is different for aarch64  arch
                
                #When the rhel for aarch64 is an separate release version, use following lines 38-39 of code for testing;
                #When the rhel for aarch64 has been merged into the rhel7.2, it's needed to use the later two lines 41-42 of code 
                #self.rversion = int(float(self.details[8]))
                #self.baseurl = "rhel-%s-server-for-arm-%s" % (self.rversion, self.tailurl)

                self.rversion = int(float(self.details[6]))
                self.baseurl = "rhel-%s-for-arm-%s" % (self.rversion, self.tailurl)
        else:
            # Configure  basrerepo url for  x86_64 , i386 , ppc64 , s390x arch
            # Configure  baserepo url for  variant Server , client, workstation,
            # computenode
                self.rversion = int(float(self.details[6]))
                if 'x86_64'or 'i386' in self.archd[1]:
                        if self.details[4] == "Server":
                                self.baseurl = "rhel-%s-server-%s" % (self.rversion, self.tailurl)
                        if self.details[4] == "Workstation":
                                self.baseurl = "rhel-%s-workstation-%s" % (self.rversion, self.tailurl)
                        if self.details[4] == "Client":
                                self.baseurl = "rhel-%s-desktop-%s" % (self.rversion, self.tailurl)
                        if self.details[4] == "ComputeNode":
                                self.baseurl = "rhel-%s-hpc-node-%s" % (self.rversion, self.tailurl)

                if 'ppc64' in self.archd[1]:
                        if self.details[4] == "Server":
                                self.baseurl = "rhel-%s-for-power-%s" % (self.rversion, self.tailurl)
                if 's390x' in self.archd[1]:
                        if self.details[4] == "Server":
                                self.baseurl = "rhel-%s-for-system-z-%s" % (self.rversion, self.tailurl)
                if 'ppc64le' in self.archd[1]:
                        self.baseurl = "rhel-%s-for-power-le-%s" % (self.rversion, self.tailurl)
        return (self.baseurl.lower())
