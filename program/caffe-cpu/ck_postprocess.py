#
# Converting raw Caffe output to CK timing format
#
# Developer: Grigori Fursin, cTuning foundation, 2016
#

import json
import os

d={}

print ('  (processing OpenME output ...)')

# Preload tmp-ck-timer.json from OpenME if exists.
exists=True
try:
  f=open('tmp-ck-timer.json', 'r')
except Exception as e:
  exists=False
  pass

if exists:
  try:
    s=f.read()
    d=json.loads(s)
  except Exception as e:
    exists=False
    pass

  if exists:
    f.close()

d['post_processed']='yes'

# Temporal hack to fix strange problem in serialization of JSON via internet
#x=d.get('run_time_state',{}).get('RESULTS#max_abs_diff','')
#if x!='':
#   d['run_time_state']['RESULTS#max_abs_diff']=str(x)

# Adding user to identify crowdtuning results
user=os.environ.get('CK_CROWDTUNING_USER','')
if user!='':
   d['crowdtuning_user']=user

# Read vector of values.
exists=True
try:
  f=open('tmp-output.txt', 'r')
except Exception as e:
  exists=False
  pass

if exists:
  try:
    s=f.read()
  except Exception as e:
    exists=False
    pass

  if exists:
    f.close()

    if len(s)>0:
      if s[-1]==',': s=s[:-1]
      d['result_string']=s

# Read stdout.
exists=True
try:
  f=open('run.stdout', 'r')
except Exception as e:
  exists=False
  pass

if exists:
  try:
    s=f.read()
  except Exception as e:
    exists=False
    pass

  if exists:
    f.close()
    d['stdout']=s

# Read stderr.
exists=True
try:
  f=open('run.stderr', 'r')
except Exception as e:
  exists=False
  pass

if exists:
  try:
    s=f.read()
  except Exception as e:
    exists=False
    pass

  if exists:
    f.close()
    d['stderr']=s

# Temporary workaround for when executing with "--sudo".
os.system('sudo rm tmp-ck-timer.json')

# Write CK json.
f=open('tmp-ck-timer.json','wt')
f.write(json.dumps(d, indent=2, sort_keys=True)+'\n')
f.close()
