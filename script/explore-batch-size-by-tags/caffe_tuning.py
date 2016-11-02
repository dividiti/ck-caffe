import ck.kernel as ck
import copy

istart=1
istep=1
istop=4
idefault=1

def start(i):

    # Detect basic platform info
    ii={'action':'detect',
        'module_uoa':'platform',
        'out':'out'}
    r=ck.access(ii)
    if r['return']>0: return r

    # Host and target OS params
    hos=r['host_os_uoa']
    hosd=r['host_os_dict']

    tos=r['os_uoa']
    tosd=r['os_dict']
    tdid=r['device_id']

    # Load Caffe program meta and desc to check deps
    rx=ck.access({'action':'load',
                  'module_uoa':'program',
                  'data_uoa':'caffe'})
    if rx['return']>0: return rx
    mm=rx['dict']

    # Update deps from GPGPU or ones remembered during autotuning
    cdeps=mm.get('compile_deps',{})

    # Caffe libs
    depl=copy.deepcopy(cdeps['lib-caffe'])

    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'deps':{
           "lib-caffe": copy.deepcopy(depl)
          }
        }
    r=ck.access(ii)
    if r['return']>0: return r

    udepl=r['deps']['lib-caffe'].get('choices',[]) # All UOAs of env for Caffe lib
    if len(udepl)==0:
        return {'return':1, 'error':'no installed Caffe libs'}

    # Caffe models
    depm=copy.deepcopy(cdeps['caffemodel'])

    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'deps':{
           "caffemodel": copy.deepcopy(depm)
          }
        }
    r=ck.access(ii)
    if r['return']>0: return r

    udepm=r['deps']['caffemodel'].get('choices',[]) # All UOAs of env for Caffe models
    if len(udepm)==0:
        return {'return':1, 'error':'no installed Caffe models'}

    # Prepare pipeline
    cdeps['lib-caffe']['uoa']=udepl[0]
    cdeps['caffemodel']['uoa']=udepm[0]

    ii={'action':'pipeline',

        'module_uoa':'program',
        'data_uoa':'caffe',

        'prepare':'yes',

        'dependencies': cdeps,

        'cmd_key':'time_gpu',

        'no_state_check':'yes',
        'no_compiler_description':'yes',
        'skip_calibration':'yes',

        'cpu_freq':'max',
        'gpu_freq':'max',
        'env_speed':'yes',
        'energy':'no',

        'skip_print_timers':'yes',

        'out':'con'}

    r=ck.access(ii)
    if r['return']>0: return r

    fail=r.get('fail','')
    if fail=='yes':
       return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

    ready=r.get('ready','')
    if ready!='yes':
       return {'return':11, 'error':'couldn\'t prepare autotuning pipeline'}

    state=r['state']
    tmp_dir=state['tmp_dir']

    # Remember resolved deps for this benchmarking session
    xcdeps=r.get('dependencies',{})

    # Clean pipeline
    if 'ready' in r: del(r['ready'])
    if 'fail' in r: del(r['fail'])
    if 'return' in r: del(r['return'])

    pipeline=copy.deepcopy(r)

    # Loops
    for lib_uoa in udepl:
        for model_uoa in udepm:
             # Prepare pipeline
             ck.out('-------------------------------------------------------')
             ck.out('Caffe lib env UOA: '+lib_uoa)
             ck.out('Caffe model env UOA: '+model_uoa)

             # Preparing autotuning input
             cpipeline=copy.deepcopy(pipeline)

             # Reset deps and change UOA
             cpipeline['dependencies']['lib-model']=copy.deepcopy(depl)
             cpipeline['dependencies']['lib-model']['uoa']=lib_uoa

             cpipeline['dependencies']['lib-model']=copy.deepcopy(depm)
             cpipeline['dependencies']['lib-model']['uoa']=model_uoa

             record_uoa='new-caffe-tuning-'+lib_uoa+'-'+model_uoa

             ii={'action':'autotune',

                 'module_uoa':'pipeline',
                 'data_uoa':'program',

                 "choices_order":[
                     [
                         "##env#CK_CAFFE_BATCH_SIZE"
                     ]
                 ],
                 "choices_selection":[
                     {"type":"loop", "start":istart, "stop":istop, "step":istep, "default":idefault}
                 ],

                 "features_keys_to_process":["##choices#*"],

                 "iterations":-1,
                 "repetitions":5,

                 "record":"yes",
                 "record_failed":"yes",
                 "record_params":{
                     "search_point_by_features":"yes"
                 },
                 "record_repo":"local",
                 "record_uoa":record_uoa,

                 "tags":["time_gpu", "$hostname", "$caffemodel_tags", "$caffe_tags"],

                 'pipeline':cpipeline,
                 'out':'out'}

             r=ck.access(ii)
             if r['return']>0: return r

             fail=r.get('fail','')
             if fail=='yes':
                return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

    return {'return':0}

r=start({})
if r['return']>0: ck.err(r)
