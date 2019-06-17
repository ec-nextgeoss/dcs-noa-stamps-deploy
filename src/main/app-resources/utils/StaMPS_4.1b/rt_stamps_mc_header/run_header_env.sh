#!/bin/sh

APPSHOME="/home/aapostolakis"

source $APPSHOME/StaMPS_CONFIG_sandbox.bash

MCR="$APPSHOME/R2015a_runtime/v85"

$APPSHOME/StaMPS_4.1b/rt_stamps_mc_header/run_stamps_mc_header_sb.sh $MCR $@
