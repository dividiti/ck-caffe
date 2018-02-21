#
# Preprocessing Caffe templates
#
# Developers:
# - Grigori Fursin, cTuning foundation, 2016
# - Anton Lokhmotov, dividiti, 2017
#

import json
import os
import re

def ck_preprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    env=i['env']
    nenv={} # new environment to be added to the run script

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']
    remote=tosd.get('remote','')

    if remote=='yes':
       es=tosd['env_set']
    else:
       es=hosd['env_set'] # set or export

    params=rt['params']
    cm_key=params['caffemodel_key']

    classification=params.get('classification','')

    b='\n'

    # Get number of images
    if classification=='yes':
        nim=1
    elif 'dataset-imagenet-lmdb' in deps:
        nim=deps.get('dataset-imagenet-lmdb',{}).get('dict',{}). \
            get('customize',{}).get('features',{}).get('number_of_original_images','')
        if nim=='':
           return {'return':1, 'error':'can\'t find number of images in a dataset'}
        nim=int(nim)
    else:
        nim=-1

    # Find template
    x=deps['caffemodel']
    cm_path=x['dict']['env']['CK_ENV_MODEL_CAFFE']

    cmw_path_full=x['dict']['env']['CK_ENV_MODEL_CAFFE_WEIGHTS']
    nenv['CK_ENV_MODEL_CAFFE_WEIGHTS']=cmw_path_full

    mean_bin='imagenet_mean.binaryproto'
    aux_mean_bin = ''
    if deps.get('imagenet-aux', '') != '':
        aux_mean_bin = deps['imagenet-aux']['dict']['env'].get('CK_CAFFE_IMAGENET_MEAN_BIN', '')
    model_mean_bin = x['dict']['env'].get('CK_ENV_MODEL_CAFFE_MEAN_BIN', '')

    if aux_mean_bin != '':
        mean_bin = aux_mean_bin
    if model_mean_bin != '':
        mean_bin = model_mean_bin

    nenv['CK_CAFFE_MODEL_MEAN_BIN'] = mean_bin

    if remote=='yes':
       # For Android we need only filename without full path
       cmw_path=os.path.basename(cmw_path_full)
    else:
       cmw_path=cmw_path_full

    nenv['CK_CAFFE_MODEL_WEIGHTS']=cmw_path

    cus=x['cus']['params'][cm_key]

    template=cus['template']

    # Load network topology template
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
    if bs=='': bs=env.get('BATCH_SIZE','')

    if bs!='':
       sub['batch_size']=bs
       sub['val_batch_size']=bs
       sub['train_batch_size']=bs
    else:
       bs=sub.get('batch_size','')
       if bs=='':
          bs=sub.get('val_batch_size','')

    nenv['CK_CAFFE_BATCH_SIZE']=bs # FGG added recently to save final BATCH SIZE (for stats)

    # Check iterations
    iters=env.get('CK_CAFFE_ITERATIONS','')

    if iters=='':
       if bs=='':
          iters=1
       elif nim!=-1:
          bs=int(bs)
          iters=nim/bs

       env['CK_CAFFE_ITERATIONS']=iters
       b+=es+' CK_CAFFE_ITERATIONS='+str(iters)+'\n'

    for k in sub:
        v=sub[k]
        st=st.replace('$#'+k+'#$',str(v))

    # Get path to imagenet aux
    plmdb=''
    paux=''
    path_to_labelmap = x['dict']['env'].get('CK_ENV_MODEL_CAFFE_LABELMAP', '')

    if classification!='yes' and nim!=-1:
        paux=deps['dataset-imagenet-aux']['dict']['env']['CK_ENV_DATASET_IMAGENET_AUX']+'/'
        plmdb=deps['dataset-imagenet-lmdb']['dict']['env']['CK_ENV_DATASET_IMAGENET_VAL_LMDB']

    st=st.replace('$#train_mean#$', mean_bin)
    st=st.replace('$#val_mean#$', mean_bin)
    st=st.replace('$#path_to_imagenet_aux#$', paux)
    st=st.replace('$#train_lmdb#$', plmdb)
    st=st.replace('$#val_lmdb#$', plmdb)
    st=st.replace('$#path_to_labelmap#$', path_to_labelmap)

    # Check default type and math for forward and backward propagation
    # (for NVIDIA's caffe-0.16+ branch)
    default_forward_type=env.get('CK_CAFFE_DEFAULT_FORWARD_TYPE','')
    if default_forward_type!='': st='default_forward_type:'+default_forward_type+'\n'+st
    default_backward_type=env.get('CK_CAFFE_DEFAULT_BACKWARD_TYPE','')
    if default_backward_type!='': st='default_backward_type:'+default_backward_type+'\n'+st
    default_forward_math=env.get('CK_CAFFE_DEFAULT_FORWARD_MATH','')
    if default_forward_math!='': st='default_forward_math:'+default_forward_math+'\n'+st
    default_backward_math=env.get('CK_CAFFE_DEFAULT_BACKWARD_MATH','')
    if default_backward_math!='': st='default_backward_math:'+default_backward_math+'\n'+st

    # Record template
    r=ck.save_text_file({'text_file':fn, 'string':st})
    if r['return']>0: return r

    # Prepare path to model
    b+=es+' CK_CAFFE_MODEL='+fn+'\n'
    env['CK_CAFFE_MODEL']=fn

    fnx=os.path.basename(fn)
    b+=es+' CK_CAFFE_MODEL_FILE='+fnx+'\n'
    env['CK_CAFFE_MODEL_FILE']=fnx

    return {'return':0, 'bat':b, 'new_env':nenv}

# Do not add anything here!
