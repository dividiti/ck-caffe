#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json
import re

def setup(i):
    """
    Input:  {
              cfg              - meta of the soft entry
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

              (install_env) - prepare environment to be used before the install script
            }

    """

    import os
    import shutil
    import glob

    # Get variables
    ck=i['ck_kernel']

    interactive=i.get('interactive','')

    o=i.get('out','')

    hos=i['host_os_uoa']
    tos=i['target_os_uoa']

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    hbits=hosd.get('bits','')
    tbits=tosd.get('bits','')

    hname=hosd.get('ck_name','')    # win, linux
    hname2=hosd.get('ck_name2','')  # win, mingw, linux, android
    tname2=tosd.get('ck_name2','')  # win, mingw, linux, android

    macos=hosd.get('macos','')      # yes/no

    hft=i.get('features',{}) # host platform features
    habi=hft.get('os',{}).get('abi','') # host ABI (only for ARM-based); if you want to get target ABI, use tosd ...
                                        # armv7l, etc...

    p=i['path']

    env=i['new_env']

    pi=i.get('install_path','')

    cus=i['customize']
    ie=cus.get('install_env',{})
    nie={} # new env

    deps=i.get('deps','')

    cfg=i.get('cfg',{})

    # If need OpenCL, test GPGPU feature to disable unified memory if needed
    if env.get('DISABLE_DEVICE_HOST_UNIFIED_MEMORY','')!='ON':
       ask=False
       if cfg.get('need_gpgpu_type','')=='opencl':
          for q in i.get('features',{}).get('gpgpu',[]):
              x=q.get('gpgpu_misc',{})

              x1=x.get('unified memory','').strip()
              x2=x.get('software (driver) version','').strip()

              if x1=='yes' and len(x2)>0 and x2[0:1]=='1':
                 ask=True
                 break

       if ask:
          disable=True
          if o=='con' and interactive=='yes':
             ck.out('')
             r=ck.inp({'text':'WARNING: your OpenCL device may not support unified memory. Disable (Y/n)? '})
             if r['return']>0: return r
             x=r['string'].strip().lower()
             if x=='n' or x=='no':
                disable=False

          if disable:
             env['DISABLE_DEVICE_HOST_UNIFIED_MEMORY']='ON'

    # redirect to orignal one
    r=ck.access({'action':'run',
                 'module_uoa':'script',
                 'data_uoa':'fd44428fbc77f77f',
                 'code':'custom',
                 'func':'setup',
                 'dict':i})
    return r

