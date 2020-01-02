#!/opt/anaconda/bin/python

import sys
import atexit
import os
import shutil
import subprocess
import re
import stat
import fnmatch

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

    #PROCESSDIR="/shared/ath_sent1_test2/stamps_steps_2"
    PROCESSDIR=ciop.getparam('outputdir')
    home=os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
    runstampsheader = os.path.join(home,'StaMPS_4.1b/rt_stamps_mc_sb_2/run_header_env.sh')

    for inputfile in sys.stdin:
        masterfolder=inputfile.replace("\t","").replace("\n","").replace("\r","")
        #masterfolder=ciop.getparam('masterfolder')
    
        ciop.log('INFO', 'Master folder is: ' + masterfolder)
           
        processfolder = os.path.join(PROCESSDIR,os.path.basename(masterfolder))
        ciop.log('INFO', 'Master temp folder: ' + processfolder)
        ciop.log('INFO', 'path exists  ' + processfolder + ' : ' + '%s'%os.path.exists(processfolder))
        ciop.log('INFO', 'path exists  ' + PROCESSDIR + ' : ' + '%s'%os.path.exists(PROCESSDIR))
        
        if not os.path.exists(PROCESSDIR):
            os.makedirs(PROCESSDIR)
            os.chmod(PROCESSDIR,stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            
        if not os.path.exists(processfolder):
            ciop.log('INFO', 'Copy  ' + masterfolder + ' to ' + PROCESSDIR)
            retrieved = ciop.copy(masterfolder, PROCESSDIR)
            if not retrieved:
                clean_exit(1)
            assert(retrieved)
            ciop.log('INFO', 'Finished : ' + os.path.basename(retrieved))
            #Possible alternative: Use of copytree
            #try:
            #    shutil.copytree(masterfolder, PROCESSDIR)
            #except:
            #    clean_exit(1)

        #change working directory
        os.chdir(processfolder)
        ciop.log('INFO', 'Change working directory to  :' + processfolder)

        #set parameters to stamps
        ciop.log('INFO', 'Setting Parameters')
        paramlistst = ciop.getparam('setparams').strip()
        paramlist = []
        if paramlistst:
            paramlist = [s.split("=") for s in paramlistst.split("#")]
            runsetparm = os.path.join(home,'StaMPS_4.1b/rt_setparm/run_setparm.sh')
        for p in paramlist:
            if len(p)>1:
                cmdlist = [runsetparm, '%s'%p[0].strip(), '%s'%p[1].strip()]
                ciop.log('INFO', 'Setting Parameter:'+' '.join(cmdlist))
                res=subprocess.call(cmdlist)

        #run stamps header            
        #if not os.path.isfile(os.path.join(processfolder,'patch_list_split_1')):
        cmdlist = [ runstampsheader, '1', '1', 'y', '0']
        ciop.log('INFO', 'Run Command :' + ' '.join(cmdlist))
        res=subprocess.call(cmdlist)
        #res=0
        if res!=0:
            clean_exit(2)
        assert(res == 0)
 
        # publish the result 
        # ciop.publish publish the patches names to create same number of susequent node instances
        os.chdir(processfolder)

        #define and publish patch list
        ciop.log('INFO', 'Publishing patches')

        if os.path.isfile("path.list"):
            with open("patch.list", "r") as f:
                patches = f.readlines()
                f.close()
        else:
            patches=[]
            for root, dirs, files in os.walk("."):
                for dirname in dirs:
                    if fnmatch.fnmatch(dirname, "PATCH_*"):
                        patches=patches+[dirname+"\r\n"]
	
        ciop.log('INFO', "Patch list:\n%s"%patches)    
        
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
