#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
#
# Developer: Zaborovskiy Vladislav, vladzab@yandex.ru, 
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

    p1=os.path.dirname(fp)
    pi=os.path.dirname(p1)

    ep=cus.get('env_prefix','')

    train_dir = cus.get('install_env', '').get('TRAIN_DIR', '')
    val_dir = cus.get('install_env', '').get('VAL_DIR', '')
    test_dir = cus.get('install_env', '').get('TEST_DIR', '')
    labels_dir = cus.get('install_env', '').get('LABELS_DIR', '')

    if train_dir != '':
        env[ep + '_TRAIN_IMAGE_DIR'] = train_dir
    if val_dir != '':
        env[ep + '_VAL_IMAGE_DIR'] = val_dir
    if test_dir != '':
        env[ep + '_TEST_IMAGE_DIR'] = test_dir
    if labels_dir != '':
        full_path = os.path.join(ep, labels_dir)
        train_file = cus.get('instances_train_file', '')
        val_file = cus.get('instances_val_file', '')
        env[ep + '_LABELS_DIR'] = full_path
        env[ep + 'TRAIN_LABELS_DIR'] = os.path.join(full_path, train_file)
        env[ep + 'TRAIN_LABELS_FILE'] = train_file
        env[ep + 'VAL_LABELS_DIR'] = os.path.join(full_path, val_file)
        env[ep + 'VAL_LABELS_FILE'] = val_file
    env[ep] = pi




    return {'return':0, 'bat':s}

