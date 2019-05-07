#!/opt/anaconda/bin/python

import sys
import atexit
import os
import shutil
import subprocess
import re

# import the ciop functions (e.g. copy, log)

import cioppy
ciop = cioppy.Cioppy()

# define the exit codes
SUCCESS = 0
ERR_COPY = 1
ERR_STAMPS_HEADER = 2

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
           ERR_COPY: 'Error in copy to process folder',
           ERR_STAMPS_HEADER: 'Error in stamps_mc_header'
           }
 
    ciop.log(log_level, msg[exit_code])  
    
def main():
    # Loops over all the inputs

    PROCESSDIR="/shared/ath_sent1_test2/mtpreptest"
    home='/home/aapostolakis'
    runstampsheader = os.path.join(home,'StaMPS_4.1b/rt_stamps_mc_sb_2/run_header_env.sh')

    for inputfile in sys.stdin:
        masterfolder=inputfile.replace("\t","").replace("\n","").replace("\r","")
        #masterfolder=ciop.getparam('masterfolder')
    
        ciop.log('INFO', 'Master folder is: ' + masterfolder)
           
        processfolder = os.path.join(PROCESSDIR,os.path.basename(masterfolder))
        ciop.log('INFO', 'Master temp folder: ' + processfolder)
    
        # retrieve the MER_RR__1P product to the local temporary folder TMPDIR provided by the framework (this folder is only used by this process)
        # the ciop.copy function will use one of online resource available in the metadata to copy it to the TMPDIR folder
        # the funtion returns the local path so the variable retrieved contains the local path to the MERIS product
        
        #retrieved = ciop.copy(inputfile, ciop.tmp_dir)
    
        ciop.log('INFO', 'path exists  ' + processfolder + ' : ' + '%s'%os.path.exists(processfolder))
        ciop.log('INFO', 'path exists  ' + PROCESSDIR + ' : ' + '%s'%os.path.exists(PROCESSDIR))
            
        if not os.path.exists(processfolder):
            ciop.log('INFO', 'Copy  ' + masterfolder + ' to ' + PROCESSDIR)
            retrieved = ciop.copy(masterfolder, PROCESSDIR)
            if not retrieved:
                clean_exit(1)
            assert(retrieved)
            ciop.log('INFO', 'Retrieved ' + os.path.basename(retrieved))
            
        if not os.path.isfile(os.path.join(processfolder,'patch_list_split_1')):
            os.chdir(processfolder)
            ciop.log('INFO', 'Change working directory to  :' + processfolder)
            cmdlist = [ runstampsheader, '1', '1', 'y', '0']
            ciop.log('INFO', 'Command :' + ' '.join(cmdlist))
            res=subprocess.call(cmdlist)
            #res=0
            if res!=0:
                clean_exit(2)
            assert(res == 0)
 
        # publish the result 
        # ciop.publish copies the data retrieved  to the distributed filesystem (HDFS)
        ciop.log('INFO', 'Publishing patches')
        #published = ciop.publish(retrieved)
        #published = ciop.publish(os.path.join(processfolder,'patch.list'))
        
        #with open("/application/inputs/list", "r") as f:
        
        os.chdir(processfolder)
        with open("patch.list", "r") as f:
            patches = f.readlines()
            f.close()
    
        for patch in patches:
            #line=line.rstrip('\n').rstrip('\r')
            published = ciop.publish(os.path.join(processfolder,patch), mode = "silent")
            ciop.log('INFO', 'Published ' + published)
    
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
