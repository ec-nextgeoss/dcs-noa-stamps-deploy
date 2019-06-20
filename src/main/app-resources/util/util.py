#!/opt/anaconda/bin/python

import cioppy

ciop = cioppy.Cioppy()

def log_input(reference):
    """
    Just logs the input reference, using the ciop.log function
    """

    ciop.log('INFO', 'processing input: ' + reference)

def pass_next_node(input):
    """
    Pass the input reference to the next node as is, without storing it on HDFS
    """

    ciop.publish(input, mode='silent')
