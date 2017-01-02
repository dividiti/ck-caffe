#
# Convert raw output of the Caffe 'test' command
# to the CK format.
#
# Sample output:
#      I0717 14:16:39.975189 10804 caffe.cpp:359] accuracy = 0.57
#      I0717 14:16:39.975280 10804 caffe.cpp:359] accuracy_top5 = 0.81
#
# Developers:
#   - Grigori Fursin, cTuning foundation, 2016
#   - Anton Lokhmotov, dividiti, 2016
#

import json
import os
import re

def ck_postprocess(i):

    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    cm_key=rt['params']['caffemodel_key']
    cus=deps['caffemodel']['cus']['params'][cm_key]

    # Load output as list.
    rf1=rt['run_cmd_out1']
    rf2=rt['run_cmd_out2']

    lst=[]

    if os.path.isfile(rf1):
       r=ck.load_text_file({'text_file':rf1,'split_to_list':'yes'})
       if r['return']>0: return r
       lst+=r['lst']
    if os.path.isfile(rf2):
       r=ck.load_text_file({'text_file':rf2,'split_to_list':'yes'})
       if r['return']>0: return r
       lst+=r['lst']

    # Match accuracy and loss info.
    d={}
    for accuracy_layer in cus['accuracy_layers']:
        accuracy_regex = \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
             accuracy_layer + \
             '(\s+)=(\s+)(?P<number>\d*\.?\d*)'
        for line in lst:
            match = re.search(accuracy_regex, line)
            if match:
                d[accuracy_layer] = float(match.group('number'))
                d['post_processed']='yes'

    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
       # Save to file.
       r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
       if r['return']>0: return r
    else:
       rr['return']=1
       rr['error']='failed to match any accuracy layer info in Caffe output'

    return rr

# Do not add anything here!
