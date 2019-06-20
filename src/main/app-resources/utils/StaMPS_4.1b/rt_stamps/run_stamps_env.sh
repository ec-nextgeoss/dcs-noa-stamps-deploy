#!/bin/sh

APPSHOME="/home/aapostolakis"

source $APPSHOME/StaMPS_CONFIG_sandbox.bash

MCR="$APPSHOME/R2015a_runtime/v85"

echo $APPSHOME/StaMPS_4.1b/rt_stamps/run_stamps.sh $MCR $@
$APPSHOME/StaMPS_4.1b/rt_stamps/run_stamps.sh $MCR $@
