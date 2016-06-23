#
# Converting raw Caffe output to CK timing format
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os

d={}

def ck_postprocess(i):

    ck=i['ck_kernel']

    d={}

    # Load output as list
    r=ck.load_text_file({'text_file':'stderr.log','split_to_list':'yes'})
    if r['return']>0: return r

    lst=r['lst']
    for l in lst:
        j=l.find('Total Time:')
        if j>0:
           l=l[j+12:]

           j1=l.find(' ')
           if j1>0:
              l=l[:j1]

              ttp=float(l)*1.0E-3

              d['post_processed']='yes'
              d['execution_time']=ttp
              d['execution_time_kernel_0']=ttp

    rr={'return':0}

    if d.get('post_processed','')=='yes':
       # Record to CK timer file
       r=ck.save_json_to_file({'json_file':'tmp-ck-timer.json', 'dict':d})
       if r['return']>0: return r
    else:
       rr['return']=1
       rr['error']='didn\'t manage to find Total Time string in Caffe output ...'

    return rr

# Do not add anything here!
