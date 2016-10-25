#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os

##############################################################################
# setup environment setup

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
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    import os

    # Get variables
    ck=i['ck_kernel']
    s=''

    iv=i.get('interactive','')

    cus=i.get('customize',{})
    fp=cus.get('full_path','')

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    win=tosd.get('windows_base','')
    remote=tosd.get('remote','')
    mingw=tosd.get('mingw','')

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    remote=tosd.get('remote','')
    tbits=tosd.get('bits','')

    env=i['env']

    pi=fp
    found=False
    while True:
       if os.path.isdir(os.path.join(pi,'include')):
          found=True
          break
       pix=os.path.dirname(pi)
       if pix==pi:
          break
       pi=pix

    if not found:
       return {'return':1, 'error':'can\'t find root dir of the CAFFE installation'}

    p1=os.path.dirname(fp)

    cus['path_bin']=p1

    pl=os.path.join(pi,'lib')
    if not os.path.isdir(pl):
       pl=os.path.join(pi,'.build_release','lib')
       if not os.path.isdir(pl):
          return {'return':1, 'error':'can\'t find lib dir of the CAFFE installation'}

    ep=cus.get('env_prefix','')

    cus['path_lib']=pl
    cus['path_include']=os.path.join(pi,'include')

    if win=='yes':
       if remote=='yes' or mingw=='yes': 
          sext='.a'
          dext='.so'
       else:
          sext='.lib'
          dext='.dll'
    else:
       sext='.a'
       dext='.so'

    cus['static_lib']='libcaffe'+sext
    cus['dynamic_lib']='libcaffe'+dext

    env[ep+'_STATIC_NAME']=cus.get('static_lib','')
    env[ep+'_DYNAMIC_NAME']=cus.get('dynamic_lib','')

    s+='export PATH='+cus['path_bin']+':$PATH\n'
    if cus.get('path_lib','')!='':
       s+='export LD_LIBRARY_PATH="'+cus['path_lib']+'":$LD_LIBRARY_PATH\n'
       s+='export LIBRARY_PATH="'+cus['path_lib']+'":$LIBRARY_PATH\n\n'

    env[ep]=pi

    env[ep+'_EXTRA_INCLUDE']=os.path.join(pi,'.build_release','src')

    env['CAFFE_INSTALL_DIR']=pi

    return {'return':0, 'bat':s}
