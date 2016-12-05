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

    sv1='$('
    sv2=')'

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

    # Set default parameters
    params={
     "use_index_64": 0,
     "native_fp16": 0,
     "use_cuda": 0,
     "use_greentea": 0,
     "use_libdnn": 0,
     "viennacl_dir": sv1+'CK_ENV_LIB_VIENNACL_INCLUDE'+sv2,
     "use_clblast": 0,
     "clblast_include": sv1+'CK_ENV_LIB_CLBLAST_INCLUDE'+sv2,
     "clblast_lib": sv1+'CK_ENV_LIB_CLBLAST_LIB'+sv2,
     "use_clblas": 0,
     "clblas_include": sv1+'CK_ENV_LIB_CLBLAS_INCLUDE'+sv2,
     "clblas_lib": sv1+'CK_ENV_LIB_CLBLAS_LIB'+sv2,
     "use_isaac": 0,
     "use_fft": 0,
     "use_cudnn": 0,
     "cpu_only": 0,
     "use_openmp": 0,
     "use_opencv": 1,
     "opencv_version": 2,
     "use_leveldb": 1,
     "use_lmdb": 1,
     "custom_cxx": sv1+'CK_CXX'+sv2,
     "cuda_dir": sv1+'CK_ENV_COMPILER_CUDA'+sv2,
     "cpu_blas": "open",
     "cpu_blas_include": sv1+'CK_ENV_LIB_OPENBLAS_INCLUDE'+sv2,
     "cpu_blas_lib": sv1+'CK_ENV_LIB_OPENBLAS_LIB'+sv2,
     "debug": 0,
     "viennacl_debug": 0
    }

    # Try to detect OpenCV version (from CK deps)
    ocv=deps.get('lib-opencv',{})

    ver=ocv.get('ver','')
    if len(ver)>0:
       ver1=ver[0:1]
       params['opencv_version']=ver1

    # Update from package meta
    params.update(cus.get('params',{}))

    # Load Makefile.config.template
    pp=os.path.join(p, 'Makefile.config.template')
    r=ck.load_text_file({'text_file':pp})
    if r['return']>0: return r

    s=r['string']

    # Replace all params
    for k in params:
        v=params[k]
        s=s.replace('$#'+k+'#$', str(v))

    # Record Makefile.config
    pp=os.path.join(p, 'Makefile.config')
    r=ck.save_text_file({'text_file':pp, 'string':s})
    if r['return']>0: return r

    # Update install environment, if needed
    ie={}

    return {'return':0, 'install_env':ie}
