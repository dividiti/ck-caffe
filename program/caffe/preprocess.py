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

    env=i['env']

    params=rt['params']
    cm_key=params['caffemodel_key']

    b='\n'

    # Get number of images
    nim=deps.get('dataset-imagenet-lmdb',{}).get('dict',{}). \
        get('customize',{}).get('features',{}).get('number_of_original_images','')
    if nim=='':
       return {'return':1, 'error':'can\'t find number of images in a dataset'}
    nim=int(nim)

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

    try:
        cur_dir=os.getcwd()
    except OSError:
        os.chdir('..')
        cur_dir=os.getcwd()

    # Generate tmp file
    rx=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.prototxt', 'remove_dir':'yes'})
    if rx['return']>0: return rx
    fn=os.path.join(cur_dir,rx['file_name'])

    # Customize template
    sub=cus.get('substitute',{})

    # Check batch_size
    bs=env.get('CK_CAFFE_BATCH_SIZE','')
    if bs!='':
       sub['batch_size']=bs
       sub['val_batch_size']=bs
       sub['train_batch_size']=bs
    else:
       bs=sub.get('batch_size','')
       if bs=='':
          bs=sub.get('val_batch_size','')

    iters=env.get('CK_CAFFE_ITERATIONS','')

    if iters=='':
       if bs=='':
          iters=1
       else:
          bs=int(bs)
          iters=nim/bs

       env['CK_CAFFE_ITERATIONS']=iters
       b+='export CK_CAFFE_ITERATIONS='+str(iters)+'\n'

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
    b+='export CK_CAFFE_MODEL='+fn+'\n'
    env['CK_CAFFE_MODEL']=fn

    return {'return':0, 'bat':b}

# Do not add anything here!
