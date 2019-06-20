#!/opt/anaconda/bin/python

import sys
import os
import unittest
import string
from StringIO import StringIO

# Simulating the Runtime environment
os.environ['TMPDIR'] = '/tmp'
os.environ['_CIOP_APPLICATION_PATH'] = '/application'
os.environ['ciop_job_nodeid'] = 'dummy'
os.environ['ciop_wf_run_root'] = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'artifacts')

sys.path.append('../main/app-resources/util/')

from util import log_input

class NodeATestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_log(self):
        # Example of data reference passed as input
        input_reference = "https://data2.terradue.com/eop/sentinel2/dataset/search?uid=S2A_OPER_PRD_MSIL1C_PDMC_20160508T221513_R008_V20160508T104027_20160508T104027"

        # The log function uses ciop.log, which writes on stderr. Therefore we
        # need to check the stderr to test the function.
        stderr = StringIO()
        sys.stderr = stderr
        log_input(input_reference)
        output = stderr.getvalue()
        log_message = string.split(output ,'\n')[1][27:]
        self.assertEqual(log_message, "[INFO   ] [user process] processing input: "+ input_reference, "Input reference not logged")

if __name__ == '__main__':
    unittest.main()
