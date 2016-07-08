#
# Preprocessing Caffe templates
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os
import re

def ck_postprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    params=rt['params']
    cm_key=params['caffemodel_key']

    # Find accuracy 
    x=deps['caffemodel']
    cm_path=x['dict']['env']['CK_ENV_MODEL_CAFFE']

    cus=x['cus']['params'][cm_key]

    al=cus['accuracy_layers']

    print ('Accuracy layers: ',al)

    return {'return':0}

# Do not add anything here!
