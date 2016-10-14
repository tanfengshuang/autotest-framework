#!/bin/bash
# vim: dict=/usr/share/beakerlib/dictionary.vim cpt=.,w,b,u,t,i,k
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   runtest.sh of /CoreOS/Entitlements/contentsetup
#   Description: Setup for BASIC RHEL content testing
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Check our the latest test code, convert manifest from json to xml
#  for required architectures, set environment variables
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Author: Jenny Severance <jgalipea@redhat.com>
#   Date  : October 8, 2013
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2010 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Include data-driven test data file:

# Include rhts environment
. /usr/bin/rhts-environment.sh
. /usr/share/beakerlib/beakerlib.sh
. ./setup.sh
. ./contenttest.sh

rlJournalStart
    ##############################################################################
    # Determine the machine's arch
    #############################################################################
    release=`lsb_release -r -s`
    rlLog "RHEL release is $release"
    master_rel=${release:0:1}

    arch=`arch`

    case $arch in
        i686 | i386)
                host_arch='i386'
                platform=32
                ;;
        x86_64)
                host_arch='x86_64'
                platform=64
                ;;
        s390x | s390)
                host_arch='s390x'
                platform=64
                ;;
        ppc64 | ppc)
                host_arch='ppc64'
                platform=64
                ;;
        ia64)
                host_arch='ia64'
                platform=64
                ;;
    esac

    rlLog "Machine arch: $host_arch"
    rlLog "Machine plaform: $platform"

    #################################################################################
    # Determine the RHEL variant
    ################################################################################

    cat /etc/redhat-release | grep Server
    if [ $? -eq 0 ]; then variant='Server'
    fi

    cat /etc/redhat-release | grep Client
    if [ $? -eq 0 ]; then variant='Client'
    fi

    cat /etc/redhat-release | grep Workstation
    if [ $? -eq 0 ]; then variant='Workstation'
    fi

    rlLog "RHEL variant: $variant"

    export release platform host_arch variant master_rel

  ##########################
  # Setup test environment #
  ##########################

  contenttestsetup

  #########################
  # Run Tests             #
  #########################

  contenttestrun

  rlJournalPrintText
rlJournalEnd
