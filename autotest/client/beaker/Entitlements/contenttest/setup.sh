contenttestsetup()
{
  dependencies
  gitclone
}

dependencies() 
{
  rlPhaseStartSetup "Setup up epel repo and install test code dependencies"
      ###############################################################################
      # The test code has dependencies on packages that are not in RHEL proper
      # Need to setup epel repo and install the dependencies
      ###############################################################################

repo_url="http://hp-z220-11.qe.lab.eng.nay.redhat.com/projects/content-sku/epel/$master_rel/$host_arch/"
echo "[epel]
name=git install
failovermethod=priority
baseurl=$repo_url
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-$basearch
" > /etc/yum.repos.d/epel.repo

      rlLog "Epel Repo Setup complete"

      rlLog "Executing: yum install -y git perl-Git perl-Error kobo kobo-rpmlib koji"
      yum install -y git perl-Git perl-Error kobo kobo-rpmlib koji
    rlPhaseEnd
}

gitclone()
{
  rlPhaseStartSetup "git clone the test code"
      ###############################################################################
      # git clone the test code
      ###############################################################################
      rlLog "Executing: git clone git://qe-git.englab.nay.redhat.com/hss-qe/entitlement/autotest/.git"
      git clone git://qe-git.englab.nay.redhat.com/hss-qe/entitlement/autotest/.git
  rlPhaseEnd
}
