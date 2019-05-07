#!/opt/anaconda/bin/python

import sys
import atexit
import os
import shutil
import subprocess

# import the ciop functions (e.g. copy, log)
import cioppy
ciop = cioppy.Cioppy()

# define the exit codes
SUCCESS = 0
ERR_CLEANUP = 2

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
            ERR_CLEANUP: 'Failed cleaning master folder'
           }
 
    ciop.log(log_level, msg[exit_code])  
    
def main():
    # Loops over all the inputs

    for inputfile in sys.stdin:
        # report activity in log
        ciop.log('INFO', 'The tmp master folder is: ' + inputfile)
 
        processfolder = inputfile.replace("\t","").replace("\n","").replace("\r","")
  
        if os.path.exists(processfolder):
            ciop.log('INFO', 'Removing tmp master folder ' + processfolder)
            run_proc=ciop.getparam('realrun')
            try:
                if run_proc=="yes":
                    shutil.rmtree(processfolder)
            except:
                clean_exit(2)
    
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
