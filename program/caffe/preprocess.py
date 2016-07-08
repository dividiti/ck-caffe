#
# Preprocessing Caffe templates
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os
import re

def ck_preprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    params=rt['params']
    cm_key=params['caffemodel_key']

    # Find template
    x=deps['caffemodel']
    cm_path=x['dict']['env']['CK_ENV_MODEL_CAFFE']

    cus=x['cus']['params'][cm_key]
    template=cus['template']

    # load network topology template
    pp=os.path.join(cm_path,template)

    r=ck.load_text_file({'text_file':pp})
    if r['return']>0: return r
    st=r['string']

    b=''

    cur_dir=os.getcwd()

    # Generate tmp file
    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.prototxt', 'remove_dir':'yes'})
    if rx['return']>0: return rx
    fn=os.path.join(cur_dir,rx['file_name'])

    # Customize template
    sub=cus.get('substitute',{})
    for k in sub:
        v=sub[k]
        st=st.replace('$#'+k+'#$',str(v))

    # Get path to imagenet aux
    paux=deps['dataset-imagenet-aux']['dict']['env']['CK_ENV_DATASET_IMAGENET_AUX']+'/'
    st=st.replace('$#path_to_imagenet_aux#$', paux)

    # add LMDB
    plmdb=deps['dataset-imagenet-lmdb']['dict']['env']['CK_ENV_DATASET_IMAGENET_VAL_LMDB']

    st=st.replace('$#train_lmdb#$', plmdb)
    st=st.replace('$#val_lmdb#$', plmdb)

    # Record template
    r=ck.save_text_file({'text_file':fn, 'string':st})
    if r['return']>0: return r

    # Prepare path to model
    b='export CK_CAFFE_MODEL='+fn+'\n'

    return {'return':0, 'bat':b}

# Do not add anything here!
