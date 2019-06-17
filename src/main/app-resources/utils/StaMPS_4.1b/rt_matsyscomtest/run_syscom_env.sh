#!/bin/sh

APPSHOME="/home/aapostolakis"

source $APPSHOME/StaMPS_CONFIG_sandbox.bash

MCR="$APPSHOME/R2015a_runtime/v85"

#$APPSHOME/StaMPS_4.1b/rt_matsyscomtest/run_syscomtest.sh $MCR $@
strace -Cfo /tmp/stamp24042019-1.strace.log $APPSHOME/StaMPS_4.1b/rt_matsyscomtest/run_syscomtest.sh $MCR $@
