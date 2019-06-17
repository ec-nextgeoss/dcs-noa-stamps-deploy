#!/bin/sh
APPSHOME="$_CIOP_APPLICATION_PATH/utils"
source $APPSHOME/StaMPS_CONFIG_sandbox.bash
echo $APPSHOME/StaMPS_4.1b/rt_stamps_mc_sb_2/run_stamps_mc_header_nostart_sandbox.sh $MCR $@
$APPSHOME/StaMPS_4.1b/rt_stamps_mc_sb_2/run_stamps_mc_header_nostart_sandbox.sh $MCR $@
