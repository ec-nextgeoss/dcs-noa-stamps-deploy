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
ERR_SETPARM = 3
ERR_INSAR = 4

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
           ERR_COPY: 'Error in copy to process folder',
           ERR_STAMPS_HEADER: 'Error in stamps_mc_header',
           ERR_SETPARM: 'Error in parameter setting',
           ERR_INSAR: 'INSAR folder is missing'
           }
 
    ciop.log(log_level, msg[exit_code])  

def untartoprocessdir(master, process):
    if master[-6:]=='tar.gz' or master[-3:]=='tar':
        params = 'xf' if master[-3:]=='tar' else 'xfz'
        cmdlist = ['tar', params , master, '-C', process]
        res=subprocess.call(cmdlist)
        return res
    return -100

def INSARdir(processdir):
    insardir = [d for d in os.listdir(processdir) if re.match(r'^INSAR_', d)]
    if len(insardir)>=1:
        return os.path.join(processdir,insardir[0])
    else:
        return None

def main():
    # Loops over all the inputs

    #PROCESSDIR="/shared/ath_sent1_test2/stamps_steps_2"
    PROCESSDIR=ciop.getparam('outputdir')
    home=os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
    runstampsheader = os.path.join(home,'StaMPS_4.1b/rt_stamps_mc_sb_2/run_header_env.sh')

    for inputfile in sys.stdin:
        #masterfolder=inputfile.replace("\t","").replace("\n","").replace("\r","")
        masterfolder=ciop.getparam('masterfolder')
    
        ciop.log('INFO', 'Master folder is: ' + masterfolder)
           
        ciop.log('INFO', 'Process folder is: ' + PROCESSDIR)
        ciop.log('INFO', 'path exists  ' + PROCESSDIR + ' : ' + '%s'%os.path.exists(PROCESSDIR))
        
        if not os.path.exists(PROCESSDIR):
            os.makedirs(PROCESSDIR)
            os.chmod(PROCESSDIR,stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)


        insarfolder = INSARdir(PROCESSDIR)    
        if not insarfolder:
            if masterfolder[-6:]=='tar.gz' or masterfolder[-3:]=='tar':
                ciop.log('INFO', 'Extract  ' + masterfolder + ' to ' + PROCESSDIR)
                res = untartoprocessdir(masterfolder, PROCESSDIR)
                if res!=0:
                    clean_exit(ERR_COPY)
                assert(res == 0)
            else:
                ciop.log('INFO', 'Copy  ' + masterfolder + ' to ' + PROCESSDIR)
                if os.path.isdir(masterfolder):
                    ret = ciop.copy(masterfolder, PROCESSDIR)
                    res = 0
                    if not ret:
                        res = ERR_COPY
                        clean_exit(ERR_COPY)
                    assert(res == 0)
                elif os.path.isfile(masterfolder):
                    shutil.copyfile(masterfolder, os.path.join(PROCESSDIR, os.path.basename(masterfolder)))
            res = 0
            insarfolder = INSARdir(PROCESSDIR)
            if not insarfolder:
                res = ERR_INSAR
                clean_exit(ERR_INSAR)
            assert(res == 0)
                  
            ciop.log('INFO', 'Finished creatring ' + insarfolder)

            #Possible alternative: Use of copytree
            #try:
            #    shutil.copytree(masterfolder, PROCESSDIR)
            #except:
            #    clean_exit(1)

        #change working directory
        os.chdir(insarfolder)
        ciop.log('INFO', 'Change working directory to  :' + insarfolder)

        #set parameters to stamps
        ciop.log('INFO', 'Setting Parameters')
        runsetparm = os.path.join(home,'StaMPS_4.1b/rt_setparm/run_setparm.sh')
        cmdlist = [runsetparm]
        ciop.log('INFO', 'Log saved parameters')
        res=subprocess.call(cmdlist)
        if res!=0:
            clean_exit(3)
        assert(res == 0)
        paramlistst = ciop.getparam('setparams').strip()
        paramlist = []
        if paramlistst:
            paramlist = [s.split("=") for s in paramlistst.split("#")]
        for p in paramlist:
            if len(p)>1:
                cmdlist = [runsetparm, '%s'%p[0].strip(), '%s'%p[1].strip()]
                ciop.log('INFO', 'Setting Parameter:'+' '.join(cmdlist))
                res=subprocess.call(cmdlist)
        if res!=0:
            clean_exit(3)
        assert(res == 0)

        #run stamps header            
        #if not os.path.isfile(os.path.join(insarfolder,'patch_list_split_1')):
        cmdlist = [ runstampsheader, '1', '1', 'y', '0']
        ciop.log('INFO', 'Run Command :' + ' '.join(cmdlist))
        res=subprocess.call(cmdlist)
        #res=0
        if res!=0:
            clean_exit(2)
        assert(res == 0)
 
        # publish the result 
        # ciop.publish publish the patches names to create same number of susequent node instances
        os.chdir(insarfolder)

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
            published = ciop.publish(os.path.join(insarfolder,patch), mode = "silent")
            ciop.log('INFO', 'Published ' + published)
    
try:
    main()
except SystemExit as e:
    if e.args[0]:
        clean_exit(e.args[0])
    raise
else:
    atexit.register(clean_exit, 0)
