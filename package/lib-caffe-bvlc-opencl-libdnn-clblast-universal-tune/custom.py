#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
# customize installation

def setup(i):

    ck=i['ck_kernel']

    return ck.access({'action':'run', 'module_uoa':'script', 
                      'script_module_uoa':'package', 'data_uoa':'b39f40abfd34f10b',
                      'code':'custom', 'func':'setup', 'dict':i})
