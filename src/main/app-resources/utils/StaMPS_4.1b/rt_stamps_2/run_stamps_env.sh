#!/bin/sh

APPSHOME="$_CIOP_APPLICATION_PATH/utils"
source $APPSHOME/StaMPS_CONFIG_sandbox.bash
echo $APPSHOME/StaMPS_4.1b/rt_stamps_2/run_stamps.sh $MCR $@
$APPSHOME/StaMPS_4.1b/rt_stamps_2/run_stamps.sh $MCR $@
