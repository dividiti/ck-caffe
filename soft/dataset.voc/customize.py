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
    p2=os.path.dirname(p1)
    p3=os.path.dirname(p2)
    p4=os.path.dirname(p3)
    pi=os.path.dirname(p4)

    ep=cus.get('env_prefix','')

    voc_dir1 = cus.get('install_env', '').get('VOC_DIR1', '')
    voc_dir2 = cus.get('install_env', '').get('VOC_DIR2', '')
    train_dir = cus.get('install_env', '').get('TRAIN_DIR', '')
    test_dir = cus.get('install_env', '').get('TEST_DIR', '')

    envs_list = ['IMAGE_DIR', 'LABELS_DIR', 'SEG_CLASS_DIR', 'SEG_OBJ_DIR',
                 'IMAGESETS_DIR', 'IMAGESETS_IMAGE_DIR', 'IMAGESETS_SEG_DIR',
                 'IMAGESETS_TESTS_DIR', 'SEG_OBJ_DIR']

    envs_dict = {}
    for x in envs_list:
        envs_dict[x] = cus.get('install_env', '').get(x, '')

    dirs = []
    if train_dir != '':
        dirs.append({'dirname': train_dir, 'env': "TRAIN"})
    if test_dir != '':
        dirs.append({'dirname': test_dir, 'env': "TEST"})

    for x in dirs:
        abs_path = os.path.join(pi, x['dirname'], voc_dir1, voc_dir2)
        full_env = ep + "_" + x['env']
        for key, value in envs_dict.iteritems():
            env[full_env + '_' + key] = os.path.join(abs_path, value)

    env[ep]=pi

    return {'return':0, 'bat':s}

