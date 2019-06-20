'''
Created on Dec 22, 2018

@author: celene
'''

import os
import subprocess

home=os.environ['HOME']
insar_folder = '/shared/ath_sent1_test2/mtpreptest/INSAR_20180717'
#insar_folder = 'geohazards/workDir/output_santorini_PS2/INSAR_20110929'

os.chdir(os.path.join(home,insar_folder))

runstampsh = os.path.join(home,'StaMPS_4.1b/rt_stamps_mc_header/run_header_env.sh')
print runstampsh
res=subprocess.call([ runstampsh ])

print res

if __name__ == '__main__':
    pass
