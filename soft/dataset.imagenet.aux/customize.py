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

    cus['path_bin']=pi

    s+='export PATH='+cus['path_bin']+':$PATH\n'

    ep=cus.get('env_prefix','')
    env[ep]=pi

    env['CK_CAFFE_IMAGENET_TEST_TXT']=pi+sdirs+'test.txt'
    env['CK_CAFFE_IMAGENET_TRAIN_TXT']=pi+sdirs+'train.txt'
    env['CK_CAFFE_IMAGENET_VAL_TXT']=pi+sdirs+'val.txt'

    env['CK_CAFFE_IMAGENET_DET_SYNSET_WORDS_TXT']=pi+sdirs+'det_synset_words.txt'
    env['CK_CAFFE_IMAGENET_SYNSET_WORDS_TXT']=pi+sdirs+'synset_words.txt'
    env['CK_CAFFE_IMAGENET_SYNSETS_TXT']=pi+sdirs+'synsets.txt'

    env['CK_CAFFE_IMAGENET_MEAN_BIN']=pi+sdirs+'imagenet_mean.binaryproto'
    env['CK_CAFFE_IMAGENET_BET_BIN']=pi+sdirs+'imagenet.bet.pickle'

    return {'return':0, 'bat':s}
