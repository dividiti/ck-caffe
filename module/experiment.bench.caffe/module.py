#
# Collective Knowledge: crowdbenchmarking using ARM's workload automation and CK
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

cfg={}  # Will be updated by CK (meta description of this module)
work={} # Will be updated by CK (temporal data)
ck=None # Will be updated by CK (initialized CK kernel) 

# Local settings
compiler_choices='#choices#compiler_flags#'

line='================================================================'

fsummary='summary.json'
fclassification='classification.json'
fgraph='tmp-reactions-graph.json'
ffstat='ck-stat-flat-characteristics.json'

##############################################################################
# Initialize module

def init(i):
    """

    Input:  {}

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """
    return {'return':0}

##############################################################################
# crowdsource these experiments

def crowdsource(i):
    """
    Input:  {
              (local)               - if 'yes', local crowd-benchmarking, instead of public
              (user)                - force different user ID/email for demos

              (repetitions)         - statistical repetitions (default=1), for now statistical analysis is not used (TBD)
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy
    import os

    # Setting output
    o=i.get('out','')
    oo=''
    if o=='con': oo='con'

    quiet=i.get('quiet','')

    er=i.get('exchange_repo','')
    if er=='': er=ck.cfg['default_exchange_repo_uoa']
    esr=i.get('exchange_subrepo','')
    if esr=='': esr=ck.cfg['default_exchange_subrepo_uoa']

    if i.get('local','')=='yes': 
       er='local'
       esr=''

    la=i.get('local_autotuning','')

    repetitions=i.get('repetitions','')
    if repetitions=='': repetitions=3
    repetitions=int(repetitions)

    record='no'

    # Get user 
    user=''

    mcfg={}
    ii={'action':'load',
        'module_uoa':'module',
        'data_uoa':cfg['module_deps']['program.optimization']}
    r=ck.access(ii)
    if r['return']==0:
       mcfg=r['dict']

       dcfg={}
       ii={'action':'load',
           'module_uoa':mcfg['module_deps']['cfg'],
           'data_uoa':mcfg['cfg_uoa']}
       r=ck.access(ii)
       if r['return']>0 and r['return']!=16: return r
       if r['return']!=16:
          dcfg=r['dict']

       user=dcfg.get('user_email','')

    # Initialize local environment for program optimization ***********************************************************
    pi=i.get('platform_info',{})
    if len(pi)==0:
       ii=copy.deepcopy(i)
       ii['action']='initialize'
       ii['module_uoa']=cfg['module_deps']['program.optimization']
       ii['data_uoa']='caffe'
       ii['exchange_repo']=er
       ii['exchange_subrepo']=esr
       ii['skip_welcome']='yes'
       ii['skip_log_wait']='yes'
       ii['crowdtuning_type']='caffe-crowd-benchmarking'
       r=ck.access(ii)
       if r['return']>0: return r

       pi=r['platform_info']
       user=r.get('user','')

    hos=pi['host_os_uoa']
    hosd=pi['host_os_dict']

    tos=pi['os_uoa']
    tosd=pi['os_dict']
    tbits=tosd.get('bits','')

    remote=tosd.get('remote','')

    tdid=pi['device_id']

    features=pi.get('features',{})

    fplat=features.get('platform',{})
    fos=features.get('os',{})
    fcpu=features.get('cpu',{})
    fgpu=features.get('gpu',{})

    plat_name=fplat.get('name','')
    os_name=fos.get('name','')
    cpu_name=fcpu.get('name','')
    if cpu_name=='': cpu_name='unknown-'+fcpu.get('cpu_abi','')
    gpu_name=fgpu.get('name','')
    gpgpu_name=''
    sn=fos.get('serial_number','')

    # Ask for cmd
    tp=['cpu', 'cuda', 'opencl']

    ck.out(line)
    ck.out('Select Caffe library type:')
    ck.out('')
    r=ck.access({'action':'select_list',
                 'module_uoa':cfg['module_deps']['choice'],
                 'choices':tp})
    if r['return']>0: return r
    xtp=r['choice']

    # Get extra platform features if "cuda" or "opencl"
    run_cmd='time_cpu'
    tags='lib,caffe'
    ntags='vcuda,vopencl'
    if xtp=='cuda' or xtp=='opencl':
        run_cmd='time_gpu'
        r=ck.access({'action':'detect',
                     'module_uoa':cfg['module_deps']['platform.gpgpu'],
                     'host_os':hos,
                     'target_os':tos,
                     'device_id':tdid,
                     'share':'yes',
                     'exchange_repo':er,
                     'exchange_subrepo':esr})
        if r['return']>0: return r
        gfeat=r.get('features',{})
        gpgpus=gfeat.get('gpgpu',[])

        if len(gpgpus)>0:
            gpgpu_name=gpgpus[0].get('gpgpu',{}).get('name','')

        ntags=''
        tags+=',v'+xtp

    # Get deps from caffe program
    r=ck.access({'action':'load',
                 'module_uoa':cfg['module_deps']['program'],
                 'data_uoa':'caffe'})
    if r['return']>0: return r

    deps=r['dict']['compile_deps']
    pp=r['path']

    lib_dep=deps['lib-caffe']
    lib_dep['tags']=tags
    lib_dep['no_tags']=ntags

    # Check environment for selected type
    r=ck.access({'action':'resolve',
                 'module_uoa':cfg['module_deps']['env'],
                 'deps':deps,
                 'host_os':hos,
                 'target_os':tos,
                 'device_id':tdid,
                 'out':o})
    if r['return']>0: return r
    deps=r['deps']

    # Prepare CK pipeline for a given workload
    ii={'action':'pipeline',

        'module_uoa':cfg['module_deps']['program'],
        'data_uoa':'caffe',

        'prepare':'yes',

        'dependencies':deps,
        'cmd_key':run_cmd,
        'no_state_check':'yes',
        'no_compiler_description':'yes',
        'skip_info_collection':'yes',
        'skip_calibration':'yes',
        'cpu_freq':'max',
        'gpu_freq':'max',
        'env_speed':'yes',
        'energy':'no',
        'skip_print_timers':'yes',
        'generate_rnd_tmp_dir':'no',

        'out':oo}
    rr=ck.access(ii)
    if rr['return']>0: return rr

    fail=rr.get('fail','')
    if fail=='yes':
        return {'return':10, 'error':'pipeline failed ('+rr.get('fail_reason','')+')'}

    ready=rr.get('ready','')
    if ready!='yes':
        return {'return':11, 'error':'couldn\'t prepare universal CK program workflow'}

    state=rr['state']
    tmp_dir=state['tmp_dir']

    # Clean pipeline
    if 'ready' in rr: del(rr['ready'])
    if 'fail' in rr: del(rr['fail'])
    if 'return' in rr: del(rr['return'])

    # Check if aggregted stats
    aggregated_stats={} # Pre-load statistics ...

    # Prepare high-level experiment meta
    meta={'cpu_name':cpu_name,
          'os_name':os_name,
          'plat_name':plat_name,
          'gpu_name':gpu_name,
          'caffe_type':xtp,
          'gpgpu_name':gpgpu_name,
          'cmd_key':run_cmd,
          'user':user} # in the future should move user out here 

    # Process deps
    xdeps={}
    for k in deps:
        dp=deps[k]
        xdeps[k]={'name':dp.get('name',''), 'data_name':dp.get('dict',{}).get('data_name',''), 'ver':dp.get('ver','')}

    meta['xdeps']=xdeps

    mmeta=copy.deepcopy(meta)
#    mmeta['user']=user

    # Check if already exists
    # tbd

    # Run CK pipeline *****************************************************
    pipeline=copy.deepcopy(rr)

    ii={'action':'autotune',
        'module_uoa':cfg['module_deps']['pipeline'],

        'iterations':1,
        'repetitions':repetitions,

        'collect_all':'yes',
        'process_multi_keys':['##characteristics#*'],

        'tmp_dir':tmp_dir,

        'pipeline':pipeline,

        'stat_flat_dict':aggregated_stats,

        "features_keys_to_process":["##choices#*"],

        "record_params": {
          "search_point_by_features":"yes"
        },

        'out':oo}

    rrr=ck.access(ii)
    if rrr['return']>0: return rrr

    ls=rrr.get('last_iteration_output',{})
    state=ls.get('state',{})
    xchoices=copy.deepcopy(ls.get('choices',{}))
    lsa=rrr.get('last_stat_analysis',{})
    lsad=lsa.get('dict_flat',{})

    ddd={'meta':mmeta}

    ddd['choices']=xchoices

    features=ls.get('features',{})

    deps=ls.get('dependencies',{})

    fail=ls.get('fail','')
    fail_reason=ls.get('fail_reason','')

    ch=ls.get('characteristics',{})

    # Save pipeline
    ddd['state']={'fail':fail, 'fail_reason':fail_reason}
    ddd['characteristics']=ch

    ddd['user']=user

    if o=='con':
        ck.out('')
        ck.out('Saving results to the remote public repo ...')
        ck.out('')

        # Find remote entry
        rduid=''

        ii={'action':'search',
            'module_uoa':work['self_module_uid'],
            'repo_uoa':er,
            'remote_repo_uoa':esr,
            'search_dict':{'meta':meta}}
        rx=ck.access(ii)
        if rx['return']>0: return rx

        lst=rx['lst']

        if len(lst)==1:
            rduid=lst[0]['data_uid']
        else:
            rx=ck.gen_uid({})
            if rx['return']>0: return rx
            rduid=rx['data_uid']

        # Update meta
        rx=ck.access({'action':'update',
                      'module_uoa':work['self_module_uid'],
                      'data_uoa':rduid,
                      'repo_uoa':er,
                      'remote_repo_uoa':esr,
                      'dict':ddd,
                      'substitute':'yes',
                      'sort_keys':'yes'})
        if rx['return']>0: return rx

        # Push statistical characteristics
        fstat=os.path.join(pp,tmp_dir,ffstat)

        r=ck.save_json_to_file({'json_file':fstat, 'dict':lsad})
        if r['return']>0: return r

        rx=ck.access({'action':'push',
                      'module_uoa':work['self_module_uid'],
                      'data_uoa':rduid,
                      'repo_uoa':er,
                      'remote_repo_uoa':esr,
                      'filename':fstat,
                      'overwrite':'yes'})
        if rx['return']>0: return rx

        os.remove(fstat)

        # Info
        if o=='con':
            ck.out('Succesfully recorded results in remote repo (Entry UID='+rduid+')')

    return {'return':0}
