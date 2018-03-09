#!/usr/bin/python

#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
def pre_path(i):
    tags=i['tags']
    env=i.get('install_env',{})

    # Add tags depending on env
    if env.get('CAFFE_BUILD_PYTHON','').lower()=='on' and 'vpython' not in tags: tags.append('vpython')

    return {'return':0}

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

              (install_env) - prepare environment to be used before the install script
            }

    """

    import os
    import shutil

    # Get variables
    o=i.get('out','')

    ck=i['ck_kernel']

    hos=i['host_os_uoa']
    tos=i['target_os_uoa']

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    hbits=hosd.get('bits','')
    tbits=tosd.get('bits','')

    hname=hosd.get('ck_name','')    # win, linux
    hname2=hosd.get('ck_name2','')  # win, mingw, linux, android
    macos=hosd.get('macos','')      # yes/no

    tname=tosd.get('ck_name','')    # win, linux
    tname2=tosd.get('ck_name2','')  # win, mingw, linux, android

    hft=i.get('features',{}) # host platform features
    habi=hft.get('os',{}).get('abi','') # host ABI (only for ARM-based); if you want to get target ABI, use tosd ...
                                        # armv7l, etc...

    p=i['path']

    env=i['env']
    nenv=i['new_env']

    deps=i['deps']

    pi=i.get('install_path','')

    cus=i['customize']
    ie=cus.get('install_env',{})
    nie={} # new env

    # Update vars
    if hname=='win' and tname=='win':
       if nenv.get('CAFFE_BUILD_PYTHON','')=='ON':
          pver=deps.get('python',{}).get('dict',{}).get('env',{}).get('CK_PYTHON_VER3','')
          x=''
          if pver=='YES': x='3'

          nie['CK_CMAKE_EXTRA_BOOST_PYTHON']='-DBoost_PYTHON_LIBRARY_DEBUG:FILEPATH=%CK_ENV_LIB_BOOST_LIB%\\boost_python'+x+'-mt-gd.lib -DBoost_PYTHON_LIBRARY_RELEASE:FILEPATH=%CK_ENV_LIB_BOOST_LIB%\\boost_python'+x+'-mt.lib'

    return {'return':0, 'install_env':nie}
