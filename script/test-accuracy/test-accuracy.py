#! /usr/bin/python
import ck.kernel as ck
import copy
import re
import argparse

platform_tags='nvidia-gtx1080'

def do(i, arg):
    # Detect basic platform info.
    ii={'action':'detect',
        'module_uoa':'platform',
        'out':'out'}
    r=ck.access(ii)
    if r['return']>0: return r

    # Host and target OS params.
    hos=r['host_os_uoa']
    hosd=r['host_os_dict']

    tos=r['os_uoa']
    tosd=r['os_dict']
    tdid=r['device_id']
    # Program and command.
    program='caffe'
    cmd_key='test_gpu'

    # Load Caffe program meta and desc to check deps.
    ii={'action':'load',
        'module_uoa':'program',
        'data_uoa':program}
    rx=ck.access(ii)
    if rx['return']>0: return rx
    mm=rx['dict']

    # Get compile-time and run-time deps.
    cdeps=mm.get('compile_deps',{})
    rdeps=mm.get('run_deps',{})
    # Merge rdeps with cdeps for setting up the pipeline (which uses
    # common deps), but tag them as "for_run_time".
    for k in rdeps:
        cdeps[k]=rdeps[k]
        cdeps[k]['for_run_time']='yes'
    # Caffe libs.
    depl=copy.deepcopy(cdeps['lib-caffe'])
    if (arg.tos is not None) and (arg.did is not None):
        tos=arg.tos
        tdid=arg.did

    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'out':'con',
        'deps':{'lib-caffe':copy.deepcopy(depl)}
    }
    r=ck.access(ii)
    if r['return']>0: return r

    udepl=r['deps']['lib-caffe'].get('choices',[]) # All UOAs of env for Caffe libs.
    if len(udepl)==0:
        return {'return':1, 'error':'no installed Caffe libs'}

    # Caffe models.
    depm=copy.deepcopy(cdeps['caffemodel'])

    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'out':'con',
        'deps':{'caffemodel':copy.deepcopy(depm)}
    }
    r=ck.access(ii)
    if r['return']>0: return r

    udepm=r['deps']['caffemodel'].get('choices',[]) # All UOAs of env for Caffe models.
    if len(udepm)==0:
        return {'return':1, 'error':'no installed Caffe models'}

    # ImageNet LMDBs.
    depimg=copy.deepcopy(cdeps['dataset-imagenet-lmdb'])
    ii={'action':'resolve',
        'module_uoa':'env',
        'host_os':hos,
        'target_os':tos,
        'device_id':tdid,
        'out':'con',
        'deps':{'dataset-imagenet-lmdb':copy.deepcopy(depimg)}
    }
    r=ck.access(ii)
    if r['return']>0: return r
    c = r['deps']
    udepi=r['deps']['dataset-imagenet-lmdb'].get('choices',[]) # All UOAs of env for ImageNet LMDBs.
    if len(udepi)==0:
       return {'return':1, 'error':'no installed ImageNet LMDB'}

    # Prepare pipeline.
    cdeps['lib-caffe']['uoa']=udepl[0]
    cdeps['caffemodel']['uoa']=udepm[0]
    cdeps['dataset-imagenet-lmdb']['uoa']=udepi[0]


    ii={'action':'pipeline',
        'prepare':'yes',
        'dependencies':cdeps,

        'module_uoa':'program',
        'data_uoa':program,
        'cmd_key':cmd_key,

        'target_os':tos,
        'device_id':tdid,

        'no_state_check':'yes',
        'no_compiler_description':'yes',
        'skip_calibration':'yes',

        'env':{
          'CK_CAFFE_BATCH_SIZE':2,
          'CK_CAFFE_ITERATIONS':1,
          'OPENBLAS_NUM_THREADS':4
        },

        'cpu_freq':'max',
        'gpu_freq':'max',

        'flags':'-O3',
        'speed':'no',
        'energy':'no',

        'skip_print_timers':'yes',
        'out':'con'
    }

    r=ck.access(ii)
    if r['return']>0: return r

    fail=r.get('fail','')
    if fail=='yes':
        return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

    ready=r.get('ready','')
    if ready!='yes':
        return {'return':11, 'error':'pipeline not ready'}

    state=r['state']
    tmp_dir=state['tmp_dir']

    # Remember resolved deps for this benchmarking session.
    xcdeps=r.get('dependencies',{})

    # Clean pipeline.
    if 'ready' in r: del(r['ready'])
    if 'fail' in r: del(r['fail'])
    if 'return' in r: del(r['return'])

    pipeline=copy.deepcopy(r)

    # For each Caffe lib.*******************************************************
    for lib_uoa in udepl:
        # Load Caffe lib.
        ii={'action':'load',
            'module_uoa':'env',
            'data_uoa':lib_uoa}
        r=ck.access(ii)
        if r['return']>0: return r
        # Get the tags from e.g. 'BVLC Caffe framework (libdnn,viennacl)'
        lib_name=r['data_name']
        lib_tags=re.match('BVLC Caffe framework \((?P<tags>.*)\)', lib_name)
        lib_tags=lib_tags.group('tags').replace(' ', '').replace(',', '-')
        # Skip some libs with "in [..]" or "not in [..]".
        if lib_tags not in ['cudnn']: continue

        skip_compile='no'

        # For each Caffe model.*************************************************
        for model_uoa in udepm:
            # Load Caffe model.
            ii={'action':'load',
                'module_uoa':'env',
                'data_uoa':model_uoa}
            r=ck.access(ii)
            if r['return']>0: return r
            # Get the tags from e.g. 'Caffe model (net and weights) (deepscale, squeezenet, 1.1)'
            model_name=r['data_name']
            model_tags=re.match('Caffe model \(net and weights\) \((?P<tags>.*)\)', model_name)
            model_tags=model_tags.group('tags').replace(' ', '').replace(',', '-')
            # Skip some models with "in [..]" or "not in [..]".
            if model_tags not in ['bvlc-alexnet', 'bvlc-googlenet', 'deepscale-squeezenet-1.1']: continue

            # For each ImageNet LMDB.*******************************************
            for img_uoa in udepi:
                ii={'action':'load',
                'module_uoa':'env',
                'data_uoa':img_uoa}
                r=ck.access(ii)
                if r['return']>0: return r
                img_name=r['data_name']
                img_tags=r.get('dict',{}).get('tags',[])
                if model_tags in img_tags: break
            # Skip models having no compatible LMDBs.
            if model_tags not in img_tags: continue
            resize_tags = [ tag for tag in img_tags if tag.find('resize-')!=-1 ]
            resize_tag = resize_tags[0] if resize_tags else 'resize-unknown'
            img_tags = 'imagenet-val-lmdb-'+resize_tag

            record_repo='local'
            record_uoa=model_tags+'-'+lib_tags+'-'+img_tags
            # Prepare pipeline.
            ck.out('---------------------------------------------------------------------------------------')
            ck.out('%s - %s' % (lib_name, lib_uoa))
            ck.out('%s - %s' % (model_name, model_uoa))
            ck.out('%s - %s' % (img_name, img_uoa))
            ck.out('Experiment - %s:%s' % (record_repo, record_uoa))

            # Prepare autotuning input.
            cpipeline=copy.deepcopy(pipeline)

            # Reset deps and change UOA.
            new_deps={'lib-caffe':copy.deepcopy(depl),
                      'caffemodel':copy.deepcopy(depm),
                      'dataset-imagenet-lmdb':copy.deepcopy(depimg)}

### maybe here    exit(1)
            new_deps['lib-caffe']['uoa']=lib_uoa
            new_deps['caffemodel']['uoa']=model_uoa
            new_deps['dataset-imagenet-lmdb']['uoa']=img_uoa
            jj={'action':'resolve',
                'module_uoa':'env',
                'host_os':hos,
                'target_os':tos,
                'device_id':tdid,
                'deps':new_deps}
            r=ck.access(jj)
            if r['return']>0: return r

            cpipeline['dependencies'].update(new_deps)

            cpipeline['no_clean']=skip_compile
            cpipeline['no_compile']=skip_compile

            cpipeline['cmd_key']=cmd_key

            ii={'action':'autotune',

                'module_uoa':'pipeline',
                'data_uoa':'program',

                'iterations':1,
                'repetitions':1,

                'record':'yes',
                'record_failed':'yes',
                'record_params':{
                    'search_point_by_features':'yes'
                },
                'record_repo':record_repo,
                'record_uoa':record_uoa,

                'tags':['test-accuracy', cmd_key, model_tags, lib_tags, img_tags, platform_tags ],

                'pipeline':cpipeline,
                'out':'con'}

            r=ck.access(ii)
            if r['return']>0: return r

            fail=r.get('fail','')
            if fail=='yes':
                return {'return':10, 'error':'pipeline failed ('+r.get('fail_reason','')+')'}

            skip_compile='yes'

    return {'return':0}

parser = argparse.ArgumentParser(description='Pipeline')
parser.add_argument("--target_os", action="store", dest="tos")
parser.add_argument("--device_id", action="store", dest="did")
myarg=parser.parse_args()


r=do({}, myarg)
if r['return']>0: ck.err(r)
