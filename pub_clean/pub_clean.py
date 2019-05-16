#!/opt/anaconda/bin/python

import sys
import atexit
import os
import shutil
import subprocess
from datetime import datetime
import re

# import the ciop functions (e.g. copy, log)
import cioppy
ciop = cioppy.Cioppy()

# define the exit codes
SUCCESS = 0
ERR_CLEANUP = 2
ERR_TIME = 3
ERR_ZIP = 4

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
            ERR_CLEANUP: 'Failed cleaning master folder',
            ERR_TIME: 'Calculation of process duration failed. File STAMPS.log may not exist or it is incomplete',
            ERR_ZIP: 'Failed to zip and publish INSAR folder'
           }
 
    ciop.log(log_level, msg[exit_code])  
    
def processdur(fstampslog):
    try:
        with open(fstampslog, 'r') as flog:
            loglines=flog.read()
            flog.close()
        
        st_start_time = re.search('\n(.*)(?= STAMPS           Will process patch subdirectories)',loglines,re.MULTILINE).group(1)
        st_end_time = re.search('\n(.*)(?= PS_SMOOTH_SCLA   Finished)',loglines,re.MULTILINE).group(1)
        start_time = datetime.strptime(st_start_time, '%d-%b-%Y %H:%M:%S')
        end_time = datetime.strptime(st_end_time, '%d-%b-%Y %H:%M:%S')
        
        dur = end_time - start_time
        return dur

    except:
        raise
    
def main():
    # Loops over all the inputs

    for inputfile in sys.stdin:
        # report activity in log
        ciop.log('INFO', 'The tmp master folder is: ' + inputfile)
 
        processfolder = inputfile.replace("\t","").replace("\n","").replace("\r","")

        # Find processing time from STAMPS.log        
        try:
            dur = processdur(fstampslog)
            st_dur = str(dur)
            ciop.log('INFO', 'StaMPS PS processing time steps 1-7 : ' + st_dur)
        except:
            clean_exit(ERR_TIME)

        pub=ciop.getparam('pub')
        if pub=='yes':
            # zip INSAR folder and publish metalink
            try:
                # Compress the folder and define the zip file
                zipfolder = shutil.make_archive(processfolder, 'zip', processfolder)
                # Publish the zipfolder
                ciop.log('INFO', 'Publishing ' + zipfolder)
                ciop.publish(zipfolder, metalink=True)
            except:
                clean_exit(ERR_ZIP)
  
        if os.path.exists(processfolder):
            ciop.log('INFO', 'Removing tmp master folder ' + processfolder)
            run_proc=ciop.getparam('cleanup')
            try:
                if run_proc=="yes":
                    shutil.rmtree(processfolder)
            except:
                clean_exit(ERR_CLEANUP)
                
        break
    
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
