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
ERR_STEP_5b = 2
ERR_STEP_6 = 3
ERR_STEP_7 = 4

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
           ERR_STEP_5b: 'Error in STAMPS step 5b',
           ERR_STEP_6: 'Error in STAMPS step 6',
           ERR_STEP_7: 'Error in STAMPS step 7',
           }
 
    ciop.log(log_level, msg[exit_code])  
    
def main():
 
    home=os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
    runstamps = os.path.join(home,'StaMPS_4.1b/rt_stamps_2/run_stamps_env.sh')

    # Loops over all the inputs

    for inputfile in sys.stdin:

        masterfolder=inputfile.replace("\t","").replace("\n","").replace("\r","")
        ciop.log('INFO', 'Master folder : ' + masterfolder)
        processfolder = masterfolder
        #ciop.log('INFO', 'Master process folder: ' + processfolder)
            
        os.chdir(processfolder)
        run_proc=ciop.getparam('realrun57')
        stepsrange=ciop.getparam('runsteps57').split('-')
        startstep=int(stepsrange[0])
        endstep=int(stepsrange[1])
        # TODO validation
        
        for i in range(startstep,endstep+1):
            ciop.log('INFO', 'Running Step %d'%(i))
        
            patch_flag='y' if i==5 else 'n'
            stamps_PART_limitation='2' if i==5 else '0'
            cmdlist = [ runstamps, '%d'%i, '%d'%i, patch_flag, '0', '[]', stamps_PART_limitation]
            ciop.log('INFO', 'Command :' + ' '.join(cmdlist))
            if run_proc=="yes":
                res=subprocess.call(cmdlist)
                if res!=0:
                    clean_exit(1+i)
                assert(res == 0)
                
        #output_path = os.path.join(ciop.tmp_dir, 'output')
        #os.makedirs(output_path)

        # publish the result 
        # ciop.publish copies the data retrieved  to the distributed filesystem (HDFS)
        ciop.log('INFO', 'Publishing result '+ processfolder)
        published = ciop.publish(processfolder, mode='silent')
        ciop.log('INFO', 'Published ' + published)
        break
       
    
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
