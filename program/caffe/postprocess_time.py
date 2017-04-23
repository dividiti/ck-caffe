#
# Convert raw output of the Caffe 'time' command
# to the CK timing format.
#
# Developers:
#   - Grigori Fursin, cTuning foundation / dividiti, 2016
#   - Anton Lokhmotov, dividiti, 2016-2017
#

import json
import os
import re
import sys

def ck_postprocess(i):
    ck=i['ck_kernel']
    rt=i['run_time']
    deps=i['deps']

    d={}

    env=i.get('env',{})

    # Load both stderr and stdout. Concatenate into one list.
    # NB: This assumes that Caffe iterates only once (--iterations=1).
    # Otherwise, looping over the log would be required.
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

    d['per_layer_info']=[]
    layer_index = 0

    # The new prototxt format includes data layer but for compatibility
    # with stale branches (notably, with NVIDIA's fp16) we converted
    # the AlexNet, GoogleNet and SqueezeNet 1.1 models to the old
    # prototxt format. For compatibility with experimental data obtained
    # before this conversion (e.g. on the GTX 1080), we can emulate the
    # presence of the data layer. It shouldn't be needed for new experiments.
    emulate_data_layer = False
    if emulate_data_layer:
        for direction in ['forward','backward']:
            data_layer_info = {}
            data_layer_info['direction'] = direction
            data_layer_info['index'] = layer_index
            data_layer_info['label'] = "00: data"
            data_layer_info['time_ms'] = 0.0
            data_layer_info['time_s'] = 0.0
            data_layer_info['timestamp'] = "0101 00:00:00.000000"
            d['per_layer_info'].append(data_layer_info)
        layer_index = 1

    d['REAL_ENV_CK_CAFFE_BATCH_SIZE']=env.get('CK_CAFFE_BATCH_SIZE','')
    d['REAL_ENV_CK_CAFFE_ITERATIONS']=env.get('CK_CAFFE_ITERATIONS','')
    d['REAL_ENV_CK_CAFFE_MODEL']=env.get('CK_CAFFE_MODEL','')

    for line in lst:
        # Update for Android (minor hack)
        line=line.replace('..\\caffe','caffe')
        line=line.replace('../caffe','caffe')

        # Match layer info.
        layer_regex = \
            'I(?P<timestamp>\d{4}(\s+)\d{2}:\d{2}:\d{2}\.\d{6})' + \
            '(\s+)(?P<unknown_integer>\d+)(\s+)' + \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
            '(?P<label>[\w/_]+)(\s+)'  + \
            '(?P<dir>forward|backward)(:\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(layer_regex, line)
        if match:
            info = {}
            info['direction'] = match.group('dir')
            if info['direction'] == 'forward':
                layer_index += 1
            info['index'] = layer_index - 1
            info['label'] = '%s: %s' % (str(info['index']).zfill(2), match.group('label'))
            info['time_ms'] = float(match.group('ms'))
            info['time_s'] = info['time_ms']*1e-3
            info['timestamp'] = match.group('timestamp')
            d['per_layer_info'].append(info)

        # Match memory required for data.
        memory_regex = \
            'net\.cpp:\d{3,4}](\s+)' + \
            'Memory required for data:(\s+)' + \
            '(?P<bytes>\d*)'
        match = re.search(memory_regex, line)
        if match:
            d['memory_bytes'] = int(match.group('bytes'))
            d['memory_kbytes'] = float(d['memory_bytes'])*1e-3
            d['memory_mbytes'] = float(d['memory_bytes'])*1e-6

        # Match forward execution time.
        fw_regex = \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
            'Average Forward pass:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(fw_regex, line)
        if match:
            d['time_fw_ms'] = float(match.group('ms'))
            d['time_fw_s']= d['time_fw_ms']*1e-3

        # Match backward execution time.
        bw_regex = \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
            'Average Backward pass:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(bw_regex, line)
        if match:
            d['time_bw_ms'] = float(match.group('ms'))
            d['time_bw_s']= d['time_bw_ms']*1e-3

        # Matchforward-backward execution time.
        fwbw_regex = \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
            'Average Forward-Backward:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(fwbw_regex, line)
        if match:
            d['time_fwbw_ms'] = float(match.group('ms'))
            d['time_fwbw_s']= d['time_fwbw_ms']*1e-3

        # Match total execution time.
        total_regex = \
            'caffe(\w*)\.cpp:\d{3,4}](\s+)' + \
            'Total Time:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(total_regex, line)
        if match:
            ms=float(match.group('ms'))
            d['time_total_ms']=ms
            d['time_total_ms_kernel_0']=ms
            s=ms*1e-3
            d['time_total_s']=s
            d['time_total_s_kernel_0']=s
            d['post_processed']='yes'
            # Internal CK key to show overall time.
            d['execution_time']=s

    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
        # Save to file.
        r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
        if r['return']>0: return r
    else:
        rr['return']=1
        rr['error']='failed to find the \'Total Time\' string in Caffe output'
#        print (d)

    return rr

# Do not add anything here!
