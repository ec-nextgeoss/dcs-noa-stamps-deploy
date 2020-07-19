#!/opt/anaconda/bin/python

import sys
import atexit
import os
import shutil
import subprocess
from datetime import datetime
import re
import traceback
import zipfile
import zlib
import ckanxml
import storeterradue

# import the ciop functions (e.g. copy, log)
import cioppy
ciop = cioppy.Cioppy()

# define the exit codes
SUCCESS = 0
ERR_CLEANUP = 2
ERR_TIME = 3
ERR_ZIP = 4
ERR_KML = 5
ERR_JPG = 6
ERR_HARVEST = 7

# add a trap to exit gracefully
def clean_exit(exit_code):
    log_level = 'INFO'
    if exit_code != SUCCESS:
        log_level = 'ERROR'  
   
    msg = { SUCCESS: 'Processing successfully concluded',
            ERR_CLEANUP: 'Failed cleaning master folder',
            ERR_TIME: 'Calculation of process duration failed. File STAMPS.log may not exist or it is incomplete',
            ERR_ZIP: 'Failed to zip and publish INSAR folder or plot files',
            ERR_KML: 'Failed to create kml',
            ERR_JPG: 'Failed to create jpg',
            ERR_HARVEST: 'Publish to harvest service failed'
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
    
def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files + dirs:
            ziph.write(os.path.join(root, file),\
                       os.path.relpath(os.path.join(root, file), os.path.join(path, os.path.pardir)),\
                       compress_type=zipfile.ZIP_DEFLATED)

def zipfiles(filelist, ziph):
    # ziph is zipfile handle
    for f in filelist:
        ziph.write(f, os.path.relpath(f, os.path.join(os.path.dirname(f), os.path.pardir)),\
                   compress_type=zipfile.ZIP_DEFLATED)


def main():
    # Loops over all the inputs

    for inputfile in sys.stdin:
        # report activity in log
        ciop.log('INFO', 'The StaMPS processing folder is: ' + inputfile)
 
        processfolder = inputfile.replace("\t","").replace("\n","").replace("\r","")

        # Find processing time from STAMPS.log        
        try:
            dur = processdur(os.path.join(processfolder,'STAMPS.log'))
            st_dur = str(dur)
            ciop.log('INFO', 'StaMPS PS processing time steps 1-7 : ' + st_dur)
        except:
            traceback.print_exc()
            clean_exit(ERR_TIME)

        kml=ciop.getparam('kml')
        if kml=='yes':
            # create kml
            try:
                home = os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
                runkml = os.path.join(home,'StaMPS_4.1b/rt_createkml/run_createkml.sh')
                os.chdir(processfolder)
                ciop.log('INFO', 'Create KML')
                kmlpoints = ciop.getparam('kmlpoints')
                cmdlist = [ runkml, kmlpoints]
                ciop.log('INFO', 'Command :' + ' '.join(cmdlist))
                res=subprocess.call(cmdlist)
                if res!=0:
                    clean_exit(ERR_KML)
                assert(res == 0)
            except:
                traceback.print_exc()
                clean_exit(ERR_KML)
            # create jpg
            try:
                home = os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'utils')
                runjpg = os.path.join(home,'StaMPS_4.1b/run_matlab.sh')
                os.chdir(processfolder)
                ciop.log('INFO', 'Create jpg')
                cmdlist = [ runjpg, 'plotvdo.exe']
                ciop.log('INFO', 'Command :' + ' '.join(cmdlist))
                res=subprocess.call(cmdlist)
                if res!=0:
                    clean_exit(ERR_KML)
                assert(res == 0)
            except:
                traceback.print_exc()
                clean_exit(ERR_KML)


        pub=ciop.getparam('pub')
        if pub=='yes':
            # zip INSAR folder and publish metalink
            try:
                # Compress the folder and define the zip file
                ciop.log('INFO', 'Compressing processing folder :'+processfolder)
                #zipfolder = shutil.make_archive(processfolder, 'zip', processfolder)
                zipfolder=processfolder+'.zip'
                zipf = zipfile.ZipFile(zipfolder, mode='w', allowZip64 = True)
                zipdir(processfolder, zipf)
                zipf.close()
                # Publish the zipped folder
                ciop.log('INFO', 'Publishing ' + zipfolder)
                ciop.publish(zipfolder, metalink=True)
            except:
                traceback.print_exc()
                clean_exit(ERR_ZIP)

        pub2=ciop.getparam('pub2')
        if pub2=='yes':
            # zip folder with plot files
            try:
                ciop.log('INFO', 'Compressing plot files')
                zipfolder=os.path.join(os.path.dirname(processfolder),'plotfiles.zip')
                zipf = zipfile.ZipFile(zipfolder, mode='w', allowZip64 = True)
                plot_files_list=['mean_v.mat', 'parms.mat', 'ph2.mat', 'phuw2.mat', 'ps2.mat', 'ps_plot_v-dso.mat',\
                                 'psver.mat', 'rc2.mat', 'scla2.mat', 'scn2.mat', 'tca2.mat', 'parms_aps.mat', 'gevelo.kml','mv2.mat', \
                                 'plotvdo.jpg', 'plotvdo.fig', 'ckaninfo.xml']
                plot_files_created=[]
                for f in plot_files_list:
                    fp=os.path.join(processfolder,f)
                    if os.path.exists(fp):
                        plot_files_created.append(fp)
                if len(plot_files_created)>0:
                    ciop.log('INFO', 'Compressing :'+str(plot_files_created))
                    zipfiles(plot_files_created, zipf)
                    zipf.close()
                    ciop.log('INFO', 'Publishing ' + zipfolder)
                    ciop.publish(zipfolder, metalink=True)
                else:
                    ciop.log('INFO', 'No plot files to publish')
            except:
                traceback.print_exc()
                clean_exit(ERR_ZIP)

        harvest=ciop.getparam('harvest')
        if harvest=="yes":
            try:
                harvestdir = ckanxml.updatexml('/shared/sant_test1/PS_platform/INSAR_20171108',os.path.join(os.environ['_CIOP_APPLICATION_PATH'],'pub_clean'),processfolder)
                files = [
                    {'name':'gevelo.kml', 'content_type':'text/xml'},
                    {'name':'plotvdo.jpg', 'content_type':'image/jpeg'},
                    {'name':'ckaninfo.xml', 'content_type':'text/xml'}
                ]
                storeterradue.sendfiles(files, processfolder, harvestdir)
            except:
                traceback.print_exc()
                clean_exit(ERR_HARVEST)

  
        del_proc=ciop.getparam('cleanup')
        if os.path.exists(processfolder) and del_proc=="yes":
            try:
                ciop.log('INFO', 'Removing processing folder ' + processfolder)
                shutil.rmtree(processfolder)
            except:
                traceback.print_exc()
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
