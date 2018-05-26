#
# CK configuration script for MXNet package
#
# Developer(s): 
#  * Grigori Fursin, dividiti/cTuning foundation
#

import os
import sys
import json

##############################################################################
# customize installation

def setup(i):
    # Reuse custom from master entry

    ck=i['ck_kernel']

    return ck.access({'action':'run',
                      'module_uoa':'script',
                      'script_module_uoa':'package',
                      'data_uoa':'720d42842c47ec84', # lib-mxnet-0.11.0-cpu
                      'code':'custom',
                      'func':'setup',
                      'dict':i})
