#
# Convert raw output of the Caffe 'time' command
# to the CK timing format.
#
# Developers:
#   - Grigori Fursin, cTuning foundation, 2016
#   - Anton Lokhmotov, dividiti, 2016
#

import json
import os
import re
import sys

def ck_postprocess(i):
    ck=i['ck_kernel']
    deps=i['deps']

    d={}

    env=i.get('env',{})

    # Load stderr as list.
    # NB: This assumes that Caffe iterates only once (--iterations=1).
    # Otherwise, looping over the log would be required.
    r=ck.load_text_file({'text_file':'stderr.log','split_to_list':'yes'})
    if r['return']>0: return r

    d['per_layer_info']=[]
    layer_index = 0

    d['REAL_ENV_CK_CAFFE_BATCH_SIZE']=env.get('CK_CAFFE_BATCH_SIZE','')
    d['REAL_ENV_CK_CAFFE_ITERATIONS']=env.get('CK_CAFFE_ITERATIONS','')
    d['REAL_ENV_CK_CAFFE_MODEL']=env.get('CK_CAFFE_MODEL','')

    for line in r['lst']:
        # Match layer info.
        layer_regex = 'caffe\.cpp:\d{3,4}](\s+)' + \
            '(?P<label>[\w/_]+)(\s+)'  + \
            '(?P<dir>forward|backward)(:\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(layer_regex, line)
        if match:
            info = {}
            info['index'] = layer_index
            info['label'] = '%s: %s' % (str(layer_index).zfill(2), match.group('label'))
            info['direction'] = match.group('dir')
            info['time_ms'] = float(match.group('ms'))
            info['time_s'] = info['time_ms']*1e-3
            d['per_layer_info'].append(info)
            if info['direction'] == 'backward':
                layer_index += 1

        # Match forward execution time.
        fw_regex = 'caffe\.cpp:\d{3,4}](\s+)' + \
            'Average Forward pass:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(fw_regex, line)
        if match:
            d['time_fw_ms'] = float(match.group('ms'))
            d['time_fw_s']= d['time_fw_ms']*1e-3

        # Match backward execution time.
        bw_regex = 'caffe\.cpp:\d{3,4}](\s+)' + \
            'Average Backward pass:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(bw_regex, line)
        if match:
            d['time_bw_ms'] = float(match.group('ms'))
            d['time_bw_s']= d['time_bw_ms']*1e-3

        # Match forward-backward execution time.
        fwbw_regex = 'caffe\.cpp:\d{3,4}](\s+)' + \
            'Average Forward-Backward:(\s+)' + \
            '(?P<ms>\d*\.*\d*(e\+\d+)*) ms\.'
        match = re.search(fwbw_regex, line)
        if match:
            d['time_fwbw_ms'] = float(match.group('ms'))
            d['time_fwbw_s']= d['time_fwbw_ms']*1e-3

        # Match total execution time.
        total_regex = 'caffe\.cpp:\d{3,4}](\s+)' + \
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

    # Process output of dividiti's OpenCL profiler.
    dvdt_prof=deps.get('dvdt_prof',{})
    if dvdt_prof!={}:
        with open('tmp-dvdt-prof-deps.json', 'w') as f:
            json.dump(dvdt_prof, f, indent=2)
        # Load stdout.
        r=ck.load_text_file({'text_file':'stdout.log','split_to_list':'no'})
        if r['return']>0: return r
        # Parse either cjson or ostream stdout.
        dvdt_prof_cjson=dvdt_prof['dict']['deps'].get('lib-cjson',{})
        if dvdt_prof_cjson!={}:
            # FIXME: Fragile as assumes stdout only contains profiler
            # output. Should extract it by pattern matching first.
            d['dvdt_prof']=json.loads(r['string'])
        else:
            # Locate profiler parser.
            dvdt_prof_dir=dvdt_prof['dict']['env']['CK_ENV_TOOL_DVDT_PROF']
            dvdt_prof_src_python=os.path.join(dvdt_prof_dir,'src','python')
            sys.path.append(dvdt_prof_src_python)
            from prof_parser import prof_parse
            # Parse profiler output.
            d['dvdt_prof']=prof_parse(r['string'])

    rr={}
    rr['return']=0
    if d.get('post_processed','')=='yes':
       # Save to file.
       r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
       if r['return']>0: return r
    else:
       rr['return']=1
       rr['error']='failed to find the \'Total Time\' string in Caffe output'

    return rr

# Do not add anything here!
