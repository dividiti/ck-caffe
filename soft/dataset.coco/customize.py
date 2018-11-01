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

    val_dir = cus.get('install_env', '').get('VAL_DIR', '')
    labels_dir = cus.get('install_env', '').get('LABELS_DIR', '')

    if val_dir != '':
        env[ep + '_VAL_IMAGE_DIR'] = val_dir
        env['CK_ENV_DATASET_IMAGE_DIR'] = p1

    if labels_dir != '':
        full_path = os.path.join(pi, labels_dir)
        train_file = cus.get('instances_train_file', '')
        val_file = cus.get('instances_val_file', '')
        env[ep + '_LABELS_DIR'] = full_path
        val_labels_dir = os.path.join(full_path, val_dir)
        if not os.path.exists(val_labels_dir):
            os.mkdir(val_labels_dir)
        env['CK_ENV_DATASET_LABELS_DIR'] = val_labels_dir
        annotations = os.path.join(full_path, val_file)
        env['CK_ENV_DATASET_ANNOTATIONS'] = annotations
        annotations_to_labels(val_labels_dir, annotations, p1)

    env['CK_ENV_DATASET_TYPE']='coco'
    env[ep] = pi

    return {'return':0, 'bat':s}

def annotations_to_labels(d, f, images_dir):
    import json
    import re

    print('Converting annotations from ' + f + ' to text in ' + d)

    dataset = json.load(open(f, 'r'))

    images = dict()
    images_anns = dict()
    categories = dict()

    for img in dataset['images']:
        images[img['id']] = os.path.join(images_dir, img['file_name'])
        images_anns[img['id']] = list()

    for ann in dataset['annotations']:
        images_anns[ann['image_id']].append(ann)

    for cat in dataset['categories']:
        categories[cat['id']] = cat['name']

    for image_id, image_file in images.items():
        label_file = os.path.join(d, os.path.splitext(os.path.basename(image_file))[0] + '.txt')
        with open(label_file, 'w') as lf:
            for ann in images_anns[image_id]:
                name = re.sub(r'\s+', '', categories[ann['category_id']])
                bbox = ann['bbox']
                xmin = bbox[0]
                ymin = bbox[1]
                xmax = xmin + bbox[2]
                ymax = ymin + bbox[3]
                lf.write(name + ' 0 0 0 ' + str(xmin) + ' ' + str(ymin) + ' ' + str(xmax) + ' ' + str(ymax) + '\n')
