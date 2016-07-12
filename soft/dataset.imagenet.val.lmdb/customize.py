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

    cdeps=i['deps_copy'] # even if original is removed, we still have a copy to figure out number of images

    iv=i.get('interactive','')

    cus=i.get('customize',{})
    fp=cus.get('full_path','')

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    sdirs=hosd.get('dir_sep','')

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    remote=tosd.get('remote','')
    tbits=tosd.get('bits','')

    env=i['env']

    pi=os.path.dirname(fp)

    ep=cus.get('env_prefix','')
    env[ep]=pi

    env['CK_CAFFE_IMAGENET_VAL_LMDB']=pi

    # Checking number of images
    pff=cus['ck_features_file']
    pf=os.path.join(pi, pff)
    features=cus.get('features',{})

    pim=cdeps.get('dataset-imagenet-raw',{}).get('dict',{}).get('env',{}).get('CK_CAFFE_IMAGENET_VAL','')
    if pim=='':
       if os.path.isfile(pf):
          r=ck.load_json_file({'json_file':pf})
          if r['return']>0: return r
          cus['features']=r['dict']
       else:
          return {'return':1, 'error':'CK features for DNN lmdb dataset are not defined and file '+pff+' doesn\'t exist'}

    else:
       num=cus.get('first_images','')
       if num!='':
          num=int(num)
       else:
          dl=os.listdir(pim)

          num=0

          for fn in dl:
              if fn.endswith('.JPEG') or fn.endswith('.jpeg'):
                 num+=1

       features['number_of_original_images']=num

       ie=cus.get('install_env',{})
       rw=ie.get('RESIZE_WIDTH','')
       rh=ie.get('RESIZE_HEIGHT','')
       sh=ie.get('SHUFFLE','')

       features['resize_width']=rw
       features['resize_height']=rh
       features['shuffle']=sh

       cus['features']=features

       r=ck.save_json_to_file({'json_file':pf, 'dict':features})
       if r['return']>0: return r

    return {'return':0, 'bat':s}
