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
ERR_STEP_1 = 2
ERR_STEP_2 = 3
ERR_STEP_3 = 4
ERR_STEP_4 = 5
ERR_STEP_5 = 6

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
           ERR_STEP_1: 'Error in STAMPS step 1',
           ERR_STEP_2: 'Error in STAMPS step 2',
           ERR_STEP_3: 'Error in STAMPS step 3',
           ERR_STEP_4: 'Error in STAMPS step 4',
           ERR_STEP_5: 'Error in STAMPS step 5'
           }
 
    ciop.log(log_level, msg[exit_code])
    
def find_patchlist(patchlist_folder, patch_no):
    patchlistfiles = [f for f in os.listdir(patchlist_folder) if re.match(r'^patch_list_split', f)]
    for fname in patchlistfiles:
        with open(os.path.join(patchlist_folder,fname),"r") as pl:
            patch = pl.readline().rstrip()
            pl_patch_no = re.search("[^_]*$", patch).group(0)
            if patch_no == pl_patch_no:
                return fname
    return None
    
def main():
    # Loops over all the inputs

    home=os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
    runstamps = os.path.join(home,'StaMPS_4.1b/rt_stamps_2/run_stamps_env.sh')


    for inputfile in sys.stdin:
        # report activity in log
        ciop.log('INFO', 'The input file is: ' + inputfile)

        #patch_no = inputfile[-1:]
        match = re.search(r"PATCH_.*",inputfile)
        match2 = re.search("[^_]*$", match.group(0))
        patch_no = match2.group(0).rstrip()
        
        masterfolder=os.path.dirname(inputfile)
        ciop.log('INFO', 'Master folder is: ' + masterfolder)
        
        processfolder = masterfolder
        ciop.log('INFO', 'Master temp folder: ' + processfolder)

        os.chdir(processfolder)
        run_proc=ciop.getparam('realrun15')
        stepsrange=ciop.getparam('runsteps15').split('-')
        startstep=int(stepsrange[0])
        endstep=int(stepsrange[1])
        # TODO validation
        
        for i in range(startstep,endstep+1):
            ciop.log('INFO', 'Processing PATCH ' + patch_no)
            ciop.log('INFO', 'Running Step %d for PATCH %s'%(i,patch_no))
            
            patch_list_name = find_patchlist(processfolder, patch_no)
        
            cmdlist = [ runstamps, '%d'%i, '%d'%i, 'y', '0', patch_list_name, '1']
            ciop.log('INFO', 'Command :' + ' '.join(cmdlist))
            if run_proc=="yes":
                res=subprocess.call(cmdlist)
                if res!=0:
                    clean_exit(1+i)
                assert(res == 0)

        # publish the result 
        
        #with open("/application/inputs/master", "r") as f:
        #    lines = f.readlines()
        #    f.close()
    
        #for line in lines:
        #    published = ciop.publish(line+'\n', mode = "silent")
        #    ciop.log('INFO', 'Publishing result ' + line)
        #    ciop.log('INFO', 'Published ' + published)
        
        ciop.log('INFO', 'Publishing result '+ processfolder)
        published = ciop.publish(processfolder+'\n', mode='silent')
        ciop.log('INFO', 'Published ' + published)
        
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
