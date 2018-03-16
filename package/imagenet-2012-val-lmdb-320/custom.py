#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
# customize installation

def pre_path(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet

              path             - path to entry (with scripts)
              install_path     - installation path
            }

    Output: {
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0
              (install-env) - prepare environment to be used before the install script
            }

    """

    # Get variables
    ck=i['ck_kernel']
    s=''

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    phosd=hosd.get('ck_name','')

    ie={}

    svarb=hosd.get('env_var_start','')
    svarb1=hosd.get('env_var_extra1','')
    svare=hosd.get('env_var_stop','')
    svare1=hosd.get('env_var_extra2','')

    iv=i.get('interactive','')
    cus=i.get('customize',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})

    p=i.get('path','')
    pi=i.get('install_path','')

    fi=cus.get('first_images','')
    if fi=='':
       r=ck.inp({'text':'Input number of images to process (or press Enter for default): '})
       if r['return']>0: return r
       s=r['string'].strip()

       if s!='':
          s=int(s)
          cus['first_images']=s

          esp=cus.get('extra_suggested_path','')
          x='-img'+str(s)
          cus['extra_suggested_path']=esp+x

          extra_name = cfg.get('package_extra_name') + ' ('+str(s)+' images)'
          cus['package_extra_name'] = extra_name
          cfg['package_extra_name'] = extra_name

    return {'return':0, 'install_env':ie}

##############################################################################
# customize installation

def post_deps(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet

              path             - path to entry (with scripts)
              install_path     - installation path
            }

    Output: {
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0
              (install-env) - prepare environment to be used before the install script
            }

    """

    # Get variables
    ck=i['ck_kernel']
    s=''

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    phosd=hosd.get('ck_name','')

    ie={}

    svarb=hosd.get('env_var_start','')
    svarb1=hosd.get('env_var_extra1','')
    svare=hosd.get('env_var_stop','')
    svare1=hosd.get('env_var_extra2','')

    iv=i.get('interactive','')
    cus=i.get('customize',{})
    cfg=i.get('cfg',{})
    deps=i.get('deps',{})

    p=i.get('path','')
    pi=i.get('install_path','')

    fi=cus.get('first_images','')
    if fi!='':
       fi=int(fi)

       # Get original val txt and produce new one with selected number of images ...
       vt=deps.get('dataset-imagenet-aux',{}).get('dict',{}).get('env',{}).get('CK_CAFFE_IMAGENET_VAL_TXT','')
       if vt!='':
          r=ck.gen_tmp_file({'prefix':'tmp-', 'suffix':'.tmp', 'remove_dir':'no'})
          if r['return']>0: return r
          fn=r['file_name']

          ck.out('Pruning file '+vt+' and recording to '+fn+' ...')

          ss=''
          r=ck.load_text_file({'text_file':vt, 'split_to_list':'yes'})
          if r['return']==0:
             lst=r['lst']
             n=0
             for s in lst:
                 n+=1
                 if n>fi:
                    break
                 ss+=s+'\n'

          r=ck.save_text_file({'text_file':fn, 'string':ss})
          if r['return']>0: return r

       ie['CK_CAFFE_IMAGENET_VAL_TXT']=fn

    return {'return':0, 'install_env':ie}
