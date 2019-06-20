'''
Created on Dec 22, 2018

@author: celene
'''

import os
import subprocess

home=os.environ['HOME']
insar_folder = 'output_santorini_test/INSAR_20110929'
#insar_folder = 'geohazards/workDir/output_santorini_PS2/INSAR_20110929'

os.chdir(os.path.join(home,insar_folder))

runstamps = os.path.join(home,'StaMPS_4.1b/rt_stamps/run_stamps_env.sh')
#runstamps = os.path.join(home,'STAMPS_4.1b/stamps/for_redistribution_files_only/run_stamps_env.sh')

res=subprocess.call([ runstamps, '1', '1', 'y', '0', 'patch_list_split_1', '1'])

print res

if __name__ == '__main__':
    pass