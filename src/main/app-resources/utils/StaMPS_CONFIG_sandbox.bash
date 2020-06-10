export STAMPS="$_CIOP_APPLICATION_PATH/utils/StaMPS_4.1b/StaMPS-master"
#export SAR="/home/celene/ROI_PAC_3_0_1/"
#export GETORB_BIN="/usr/local/bin"
export SAR_ODR_DIR="/home/celene/auxillary/orbits/ODR/"
#export SAR_PRC_DIR  "/home/ahooper/software/SAR_FILES/PRC"
#export VOR_DIR="/home/celene/auxillary/orbits/ENVISAT_DOR/VOR/"
#export INS_DIR="/home/celene/auxillary/INS/"
#export DORIS_BIN="/usr/local/bin"
export SNAPHU_BIN="$_CIOP_APPLICATION_PATH/utils/snaphu/bin"
export ISCECONTRIB="$_CIOP_APPLICATION_PATH/utils/ISCEcontrib/bin"
export TRIANGLE_BIN="$_CIOP_APPLICATION_PATH/utils/bin/triangle"

export ROI_PAC="$SAR/ROI_PAC"
#####################################
# ROI_PAC VERSION 3 
#####################################
export INT_BIN="/usr/local/bin"
export INT_SCR="$ROI_PAC/INT_SCR"
#####################################
#FFTW library
export FFTW_LIB_DIR="$SAR/ROI_PAC/NetInst/fftw-180413-2111/lib64"
export FFTW_INC_DIR="$SAR/ROI_PAC/NetInst/fftw-180413-2111/include"

#####################################
# ROI_PAC VERSION 2.3 and before 
#####################################
#set MACH=`uname -s`
#if ($MACH == "HP-UX") then
#  export ARCHC=HP
#else if ($MACH == "IRIX") then
#  export ARCHC=SGI
#else if ($MACH == "SunOS") then
#  export ARCHC=SUN
#else if ($MACH == "Linux") then
#  export ARCHC=LIN
#else if ($MACH == "Darwin") then
#  export ARCHC=MAC
#fi
#export INT_LIB="$ROI_PAC/LIB/$ARCHC"
#export INT_BIN="$ROI_PAC/BIN/$ARCHC"
#export FFTW_LIB="$SAR/FFTW/$ARCHC""_fftw_lib"
#####################################

#####################################
# shouldn't need to change below here
#####################################

export MY_BIN="$INT_BIN"
#export MATLABPATH=$STAMPS/matlab:`echo $MATLABPATH`
export MATLABPATH="$STAMPS/matlab:${MATLABPATH}"
export DORIS_SCR="$STAMPS/DORIS_SCR"

# Needed for ROI_PAC (a bit different to standard)

### use points not commas for decimals, and give dates in US english
export LC_NUMERIC="en_US.UTF-8"
export LC_TIME="en_US.UTF-8"

export MY_SAR="$SAR"
export OUR_SCR="$MY_SAR/OUR_SCR"
export MY_SCR="$STAMPS/ROI_PAC_SCR"

export SAR_TAPE="/dev/rmt/0mn"

export MCR="/opt/v85"
#export PATH=${PATH}:$STAMPS/bin:$MY_SCR:$INT_BIN:$INT_SCR:$OUR_SCR:$DORIS_SCR:$GETORB_BIN:$DORIS_BIN:$TRIANGLE_BIN:$SNAPHU_BIN
#export PATH=${PATH}:$STAMPS/bin:$SNAPHU_BIN:$ISCECONTRIB
export PATH="${PATH}:$STAMPS/bin:$SNAPHU_BIN:$ISCECONTRIB:$TRIANGLE_BIN"
