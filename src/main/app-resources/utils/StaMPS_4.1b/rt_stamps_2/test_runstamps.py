'''
Created on Dec 22, 2018

@author: celene
'''

import os
import subprocess

home=os.environ['HOME']
insar_folder = '/shared/ath_sent1_test2/stamps_steps/INSAR_20180717'
#insar_folder = 'geohazards/workDir/output_santorini_PS2/INSAR_20110929'

os.chdir(os.path.join(home,insar_folder))

runstamps = os.path.join(home,'StaMPS_4.1b/rt_stamps_2/run_stamps_env.sh')

res=subprocess.call([ runstamps, '1', '1', 'y', '0', 'patch_list_split_1', '1'])

print res

if __name__ == '__main__':
    pass
