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

    env[ep+'_WEIGHTS']=os.path.join(pi, cus.get('file_with_weights',''))
    env[ep+'_WEIGHTS_FILE']=cus.get('file_with_weights','')

    mean_bin_file = cus.get('file_mean_bin','')
    if (mean_bin_file != ''):
      env[ep + '_MEAN_BIN'] = os.path.join(pi, mean_bin_file)
      env[ep + '_MEAN_BIN_FILE'] = mean_bin_file

    # record params
    pff=cus['ck_params_file']
    pf=os.path.join(pi, pff)
    params=cus.get('params',{})

    if len(params)==0:
       if os.path.isfile(pf):
          r=ck.load_json_file({'json_file':pf})
          if r['return']>0: return r
          cus['params']=r['dict']
       else:
          return {'return':1, 'error':'CK params for the DNN are not defined and file '+pff+' doesn\'t exist'}

    else:
       r=ck.save_json_to_file({'json_file':pf, 'dict':params})
       if r['return']>0: return r

    return {'return':0, 'bat':s}
