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
rrepo='upload' # TBD - get from cfg

compiler_choices='#choices#compiler_flags#'

line='================================================================'

fsummary='summary.json'
fclassification='classification.json'
fgraph='tmp-reactions-graph.json'
ffstat='ck-stat-flat-characteristics.json'

form_name='wa_web_form'
onchange='document.'+form_name+'.submit();'

hextra='<i><center>\n'
hextra+='This is an on-going long-term project. Please check our vision [ '
hextra+='<a href="http://doi.acm.org/10.1145/2909437.2909449">IWOCL\'16</a>, \n'
hextra+='<a href="http://arxiv.org/abs/1506.06256">CPC\'15</a>, \n'
hextra+='<a href="https://www.youtube.com/watch?v=Q94yWxXUMP0">YouTube</a>, \n'
hextra+='<a href="http://ctuning.org/cm/wiki/index.php?title=CM:data:45741e3fbcf4024b:1db78910464c9d05">wiki</a> ] '
hextra+=' and <a href="https://github.com/dividiti/ck-caffe">CK-Caffe GitHub repo</a> for more details!'
hextra+='</center></i>\n'
hextra+='<br>\n'

selector=[{'name':'Scenario', 'key':'crowd_uid', 'module_uoa':'65477d547a49dd2c', 'module_key':'##dict#title'},
          {'name':'Platform', 'key':'plat_name'},
          {'name':'CPU', 'key':'cpu_name', 'new_line':'yes'},
          {'name':'OS', 'key':'os_name'},
          {'name':'GPU', 'key':'gpu_name'}]

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

              (choices)             - force different choices to program pipeline

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

    # Check if any input has . and convert to dict
    for k in list(i.keys()):
        if k.find('.')>0:
            v=i[k]

            kk='##'+k.replace('.','#')

            del(i[k])

            r=ck.set_by_flat_key({'dict':i, 'key':kk, 'value':v})
            if r['return']>0: return r

    choices=i.get('choices',{})
    xchoices=copy.deepcopy(choices)

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
    plat_uid=features.get('platform_uid','')
    os_name=fos.get('name','')
    os_uid=features.get('os_uid','')
    cpu_name=fcpu.get('name','')
    if cpu_name=='': cpu_name='unknown-'+fcpu.get('cpu_abi','')
    cpu_uid=features.get('cpu_uid','')
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
    gpgpu_uid=''
    if xtp=='cuda' or xtp=='opencl':
        run_cmd='time_gpu'
        r=ck.access({'action':'detect',
                     'module_uoa':cfg['module_deps']['platform.gpgpu'],
                     'host_os':hos,
                     'target_os':tos,
                     'device_id':tdid,
                     'type':xtp,
                     'share':'yes',
                     'exchange_repo':er,
                     'exchange_subrepo':esr})
        if r['return']>0: return r
        gfeat=r.get('features',{})
        gpgpus=gfeat.get('gpgpu',[])

        if len(gpgpus)>0:
            gpgpu_name=gpgpus[0].get('gpgpu',{}).get('name','')
            gpgpu_uid=gpgpus[0].get('gpgpu_uoa','')

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

        'env':i.get('env',{}),
        'choices':choices,
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
          'cmd_key':run_cmd}

    # Process deps
    xdeps={}
    xnn=''
    xblas=''
    for k in deps:
        dp=deps[k]
        dname=dp.get('dict',{}).get('data_name','')

        if k=='caffemodel':
            xnn=dname

            j1=xnn.rfind('(')
            if j1>0:
                xnn=xnn[j1+1:-1]

        xdeps[k]={'name':dp.get('name',''), 'data_name':dname, 'ver':dp.get('ver','')}

    meta['xdeps']=xdeps
    meta['nn_type']=xnn

    mmeta=copy.deepcopy(meta)

    # Extra meta which is not used to search similar case ...
    mmeta['platform_uid']=plat_uid
    mmeta['os_uid']=os_uid
    mmeta['cpu_uid']=cpu_uid
    mmeta['gpgpu_uid']=gpgpu_uid
    mmeta['user']=user

    # Check if already exists
    # tbd

    # Run CK pipeline *****************************************************
    pipeline=copy.deepcopy(rr)
    if len(choices)>0:
        r=ck.merge_dicts({'dict1':pipeline['choices'], 'dict2':xchoices})
        if r['return']>0: return r

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

            # Check host URL prefix and default module/action
            url='http://cknowledge.org/repo/web.php?template=cknowledge&action=index&module_uoa=wfe&native_action=show&native_module_uoa=program.optimization&scenario=155b6fa5a4012a93&highlight_uid='+rduid
            ck.out('')
            ck.out('You can see your results at the following URL:')
            ck.out('')
            ck.out(url)

    return {'return':0}

##############################################################################
# show results

def show(i):
    """
    Input:  {
               (crowd_module_uoa) - if rendered from experiment crowdsourcing
               (crowd_key)        - add extra name to Web keys to avoid overlapping with original crowdsourcing HTML
               (crowd_on_change)  - reuse onchange doc from original crowdsourcing HTML
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os
    import copy

    st=''

    cmuoa=i.get('crowd_module_uoa','')
    ckey=i.get('crowd_key','')

    conc=i.get('crowd_on_change','')
    if conc=='':
        conc=onchange

    hi_uid=i.get('highlight_uid','')

    h='<hr>\n'
    h+='<center>\n'
    h+='\n\n<script language="JavaScript">function copyToClipboard (text) {window.prompt ("Copy to clipboard: Ctrl+C, Enter", text);}</script>\n\n' 

    h+='<h2>Aggregated results from Caffe crowd-benchmarking (time, accuracy, energy, cost, ...)</h2>\n'

    h+=hextra

    # Check host URL prefix and default module/action
    rx=ck.access({'action':'form_url_prefix',
                  'module_uoa':'wfe',
                  'host':i.get('host',''), 
                  'port':i.get('port',''), 
                  'template':i.get('template','')})
    if rx['return']>0: return rx
    url0=rx['url']
    template=rx['template']

    url=url0
    action=i.get('action','')
    muoa=i.get('module_uoa','')

    st=''

    url+='action=index&module_uoa=wfe&native_action='+action+'&'+'native_module_uoa='+muoa
    url1=url

    # List entries
    ii={'action':'search',
        'module_uoa':work['self_module_uid'],
        'add_meta':'yes'}

    if cmuoa!='':
        ii['module_uoa']=cmuoa

    r=ck.access(ii)
    if r['return']>0: return r

    lst=r['lst']

    # Check unique entries
    choices={}
    mchoices={} # cache of UID -> alias choices
    wchoices={}

    for q in lst:
        d=q['meta']
        meta=d.get('meta',{})

        for kk in selector:
            kx=kk['key']
            k=ckey+kx

            if k not in choices: 
                choices[k]=[]
                wchoices[k]=[{'name':'','value':''}]

            v=meta.get(kx,'')
            if v!='':

                if v not in choices[k]: 
                    choices[k].append(v)

                    muoa=kk.get('module_uoa','')
                    vv=v
                    if muoa!='':
                        if k not in mchoices:
                            mchoices[k]={}

                        vv=mchoices[k].get(v,'')
                        if vv=='':
                            r=ck.access({'action':'load',
                                         'module_uoa':muoa,
                                         'data_uoa':v})
                            if r['return']==0:
                                mk=kk.get('module_key','')
                                if mk=='': mk='##data_name'

                                rx=ck.get_by_flat_key({'dict':r, 'key':mk})
                                if rx['return']>0: return rx
                                vv=rx['value']

                        if vv=='' or vv==None: vv=v

                        mchoices[k][v]=vv

                    wchoices[k].append({'name':vv, 'value':v})

    # Prepare query div ***************************************************************
    if cmuoa=='':
        # Start form + URL (even when viewing entry)
        r=ck.access({'action':'start_form',
                     'module_uoa':cfg['module_deps']['wfe'],
                     'url':url1,
                     'name':form_name})
        if r['return']>0: return r
        h+=r['html']

    for kk in selector:
        k=ckey+kk['key']
        n=kk['name']

        nl=kk.get('new_line','')
        if nl=='yes':
            h+='<br>\n<div id="ck_entries_space8"></div>\n'

        v=''
        if i.get(k,'')!='':
            v=i[k]
            kk['value']=v

        # Show hardware
        ii={'action':'create_selector',
            'module_uoa':cfg['module_deps']['wfe'],
            'data':wchoices.get(k,[]),
            'name':k,
            'onchange':conc, 
            'skip_sort':'no',
            'selected_value':v}
        r=ck.access(ii)
        if r['return']>0: return r

        h+='<b>'+n+':</b> '+r['html'].strip()+'\n'

    # Check hidden
    if hi_uid!='':
        h+='<input type="hidden" name="highlight_uid" value="'+hi_uid+'">\n'

    h+='<br><br>'

    # Prune list ******************************************************************
    plst=[]

    for q in lst:
        d=q['meta']
        meta=d.get('meta',{})

        # Check selector
        skip=False
        for kk in selector:
            k=kk['key']
            n=kk['name']
            v=kk.get('value','')

            if v!='' and meta.get(k,'')!=v:
                skip=True

        if not skip:
            # Process raw results
            arr=d.get('all_raw_results',[])

            for g in arr:
                nn=copy.deepcopy(q)

                ih=g.get('image_height',0)
                iw=g.get('image_width',0)

                it=0
                if ih!=0 and iw!=0:
                    it=ih*iw

                key=str(ih)+' x '+str(iw)

                prd=g.get('prediction','')
                if prd!='':
                    j1=prd.find('\n')
                    if j1>0:
                        j2=prd.find('\n',j1+1)
                        if j2>0:
                            prd=prd[j1:j2]

                # Check timing - currently temporal ugly hack
                t=g.get('time',[])

                tmin=0
                tmax=0

                if len(t)>0:
                    tmin=min(t)/1E3
                    tmax=max(t)/1E3

                nn['extra']={'key':key, 'raw_results':g, 'time_min':tmin, 'time_max':tmax, 'prediction':prd}

                plst.append(nn)

    # Check if too many
    lplst=len(plst)
    if lplst==0:
        h+='<b>No results found!</b>'
        return {'return':0, 'html':h, 'style':st}
    elif lplst>50:
        h+='<b>Too many entries to show ('+str(lplst)+') - please, prune list further!</b>'
        return {'return':0, 'html':h, 'style':st}

    # Prepare table
    h+='<table border="1" cellpadding="7" cellspacing="0">\n'

    ha='align="center" valign="top"'
    hb='align="left" valign="top"'

    h+='  <tr style="background-color:#dddddd">\n'
    h+='   <td '+ha+'><b>Data UID / Behavior UID</b></td>\n'
    h+='   <td '+ha+'><b>Crowd scenario</b></td>\n'
    h+='   <td '+ha+'><b>Min/Max recognition time (sec.)</b></td>\n'
    h+='   <td '+ha+'><b>Image features</b></td>\n'
    h+='   <td '+ha+'><b>Predictions</b></td>\n'
    h+='   <td '+ha+'><b>Platform</b></td>\n'
    h+='   <td '+ha+'><b>CPU</b></td>\n'
    h+='   <td '+ha+'><b>GPU</b></td>\n'
    h+='   <td '+ha+'><b>OS</b></td>\n'
    h+='   <td '+ha+'><b>Mispredictions / unexpected behavior</b></td>\n'
    h+='   <td '+ha+'><b>User</b></td>\n'
    h+='  <tr>\n'

    # Dictionary to hold target meta
    tm={}

    ix=0
    bgraph={'0':[]} # Just for graph demo
    if hi_uid!='':
        bgraph['1']=[]

    # Sort
    splst=sorted(plst, key=lambda x: x.get('extra',{}).get('time_min',0))

    for q in splst:
        ix+=1

        duid=q['data_uid']
        path=q['path']

        d=q['meta']

        meta=d.get('meta',{})

        extra=q['extra']
        img=extra.get('img',{})
        rres=extra.get('raw_results',{})

        mp=rres.get('mispredictions',[])

        key=extra.get('key','')

        buid=rres.get('behavior_uid','')
        pred=extra.get('prediction','').replace(' ','&nbsp;')
        user=rres.get('user','')

        tmin=extra.get('time_min',0)
        tmax=extra.get('time_max',0)

        scenario=meta.get('crowd_uid','')

        plat_name=meta.get('plat_name','')
        cpu_name=meta.get('cpu_name','')
        os_name=meta.get('os_name','')
        gpu_name=meta.get('gpu_name','')
        gpgpu_name=meta.get('gpgpu_name','')

        plat_uid=meta.get('platform_uid','')
        cpu_uid=meta.get('cpu_uid','')
        os_uid=meta.get('os_uid','')
        gpu_uid=meta.get('gpu_uid','')
        gpgpu_uid=meta.get('gpgpu_uid','')

        te=d.get('characteristics',{}).get('run',{})

#        bgc='afffaf'
        bgc='dfffdf'
        bg=' style="background-color:#'+bgc+';"'

        h+='  <tr'+bg+'>\n'

        x=work['self_module_uid']
        if cmuoa!='': x=cmuoa
        h+='   <td '+ha+'>'+str(ix)+')&nbsp;<a href="'+url0+'&wcid='+x+':'+duid+'">'+duid+' / '+buid+'</a></td>\n'

        x=scenario
        xx=mchoices.get(ckey+'crowd_uid',{}).get(x,'')
        h+='   <td '+ha+'>'+xx+'</a></td>\n'

        # Check relative time
        xx='<b>'+('%.3f'%tmin)+'</b>&nbsp;/&nbsp;'+('%.3f'%tmax)

        if duid==hi_uid:
            if hi_uid!='':
                bgraph['0'].append([ix,None])
                bgraph['1'].append([ix,tmin])
        else:
            bgraph['0'].append([ix,tmin])
            if hi_uid!='': bgraph['1'].append([ix,None])

        h+='   <td '+ha+'>'+xx+'</a></td>\n'

        # All images
        h+='   <td '+ha+'>'+key.replace(' ','&nbsp;')+'</a></td>\n'
        h+='   <td '+ha+'>'+pred+'</a></td>\n'

        # Platform, etc ...
        x=plat_name
        if plat_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform']+':'+plat_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=cpu_name
        if cpu_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform.cpu']+':'+cpu_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=gpu_name
        if gpu_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform.gpu']+':'+gpu_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=os_name
        if os_uid!='':
            x='<a href="'+url0+'&wcid='+cfg['module_deps']['platform']+':'+os_uid+'">'+x+'</a>'
        h+='   <td '+ha+'>'+x+'</td>\n'

        x=''
        for q in mp:
            ca=q.get('correct_answer','')
            mi=q.get('mispredicted_image','')
            mr=q.get('misprediction_results','')

            if mr!='':
                j1=mr.find('\n')
                if j1>0:
                    j2=mr.find('\n',j1+1)
                    if j2>0:
                        mr=mr[j1:j2]

            xx=ca
            if mi!='':
                y=work['self_module_uid']
                if cmuoa!='': y=cmuoa
                url=url0+'action=pull&common_action=yes&cid='+y+':'+duid+'&filename='+mi

                xx='<a href="'+url+'">'+ca+'</a>'

            if x!='':
                x+='<hr>\n'

            x+='<strike>'+mr+'</strike><br>'+xx+'<br>\n'

        h+='   <td '+ha+'>'+x+'</td>\n'

        h+='   <td '+ha+'><a href="'+url0+'&action=index&module_uoa=wfe&native_action=show&native_module_uoa=experiment.user">'+user+'</a></td>\n'

        h+='  <tr>\n'

    h+='</table>\n'
    h+='</center>\n'

    if cmuoa=='':
        h+='</form>\n'

    if len(bgraph['0'])>0:
       ii={'action':'plot',
           'module_uoa':cfg['module_deps']['graph'],

           "table":bgraph,

           "ymin":0,

           "ignore_point_if_none":"yes",

           "plot_type":"d3_2d_bars",

           "display_y_error_bar":"no",

           "title":"Powered by Collective Knowledge",

           "axis_x_desc":"Experiment",
           "axis_y_desc":"Neural network recognition time per pixel (us)",

           "plot_grid":"yes",

           "d3_div":"ck_interactive",

           "image_width":"900",
           "image_height":"400",

           "wfe_url":url0}

       r=ck.access(ii)
       if r['return']==0:
          x=r.get('html','')
          if x!='':
             st+=r.get('style','')

             h+='<br>\n'
             h+='<center>\n'
             h+='<div id="ck_box_with_shadow" style="width:920px;">\n'
             h+=' <div id="ck_interactive" style="text-align:center">\n'
             h+=x+'\n'
             h+=' </div>\n'
             h+='</div>\n'
             h+='</center>\n'

    return {'return':0, 'html':h, 'style':st}

##############################################################################
# replay experiment (TBD)

def replay(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    # TBD - take params from remote/local experiment and pre-set ...
    # Run locally, i.e. do not share stats unless requested ...

    i['action']='crowdsource'
    i['module_uoa']=cfg['module_deps']['experiment.bench.caffe']

    return ck.access(i)


##############################################################################
# process raw results from mobile devices

def process(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy

#    ck.save_json_to_file({'json_file':'/tmp/xyz1.json','dict':i})

    crowd_uid=i.get('crowd_uid','')
    email=i.get('email','')
    raw_results=i.get('raw_results',{})

    features=i.get('platform_features',{})

    fplat=features.get('platform',{})
    fos=features.get('os',{})
    fcpu=features.get('cpu',{})
    fgpu=features.get('gpu',{})

    plat_name=fplat.get('name','')
    plat_uid=features.get('platform_uid','')
    os_name=fos.get('name','')
    os_uid=features.get('os_uid','')
    gpu_uid=features.get('gpu_uid','')
    cpu_name=fcpu.get('name','')
    cpu_abi=fcpu.get('cpu_abi','')
    if cpu_name=='' and cpu_abi!='': 
        cpu_name='unknown-'+fcpu.get('cpu_abi','')
    cpu_uid=features.get('cpu_uid','')
    gpu_name=fgpu.get('name','')
    gpgpu_name=''
    gpgpu_uid=''
    sn=fos.get('serial_number','')

    # Prepare high-level experiment meta
    meta={'cpu_name':cpu_name,
          'os_name':os_name,
          'plat_name':plat_name,
          'gpu_name':gpu_name,
          'gpgpu_name':gpgpu_name,
          'crowd_uid':crowd_uid}

    mmeta=copy.deepcopy(meta)

    # Extra meta which is not used to search similar case ...
    mmeta['platform_uid']=plat_uid
    mmeta['os_uid']=os_uid
    mmeta['cpu_uid']=cpu_uid
    mmeta['gpu_uid']=gpu_uid
    mmeta['gpgpu_uid']=gpgpu_uid

    # Generate behavior UID
    rx=ck.gen_uid({})
    if rx['return']>0: return rx
    buid=rx['data_uid']

    raw_results['user']=email
    raw_results['behavior_uid']=buid

    # Check if already exists
    duid=''
    ddd={}

    ii={'action':'search',
        'module_uoa':work['self_module_uid'],
        'repo_uoa':rrepo,
        'search_dict':{'meta':meta},
        'add_meta':'yes'}
    rx=ck.access(ii)
    if rx['return']>0: return rx

    lst=rx['lst']

    if len(lst)==1:
        duid=lst[0]['data_uid']
        ddd=lst[0]['meta']
    else:
        rx=ck.gen_uid({})
        if rx['return']>0: return rx
        duid=rx['data_uid']

    # Update timing in raw results (ugly temporal hack - move to list) ...
    t=[]
    tx=raw_results.get('time1',None)
    if tx!=None: t.append(tx)
    tx=raw_results.get('time2',None)
    if tx!=None: t.append(tx)
    tx=raw_results.get('time3',None)
    if tx!=None: t.append(tx)
    raw_results['time']=t

    # Process results
    results=ddd.get('all_raw_results',[])

    # Check if already exists with this image topology
    found=False
    for q in results:
        if q.get('image_height',None)==raw_results.get('image_height',None) and \
           q.get('image_width',None)==raw_results.get('image_width',None):
            t=q.get('time',[])

            for tx in raw_results.get('time',[]):
                t.append(tx)
            q['time']=t

            buid=q.get('behavior_uid','')

            found=True

    if not found:
        results.append(raw_results)

    ddd['all_raw_results']=results

    xmeta=ddd.get('meta',{})
    xmeta.update(mmeta)
    ddd['meta']=xmeta

    # Update meta
    rx=ck.access({'action':'update',
                  'module_uoa':work['self_module_uid'],
                  'data_uoa':duid,
                  'repo_uoa':rrepo,
                  'dict':ddd,
                  'substitute':'yes',
                  'sort_keys':'yes'})
    if rx['return']>0: return rx

    return {'return':0, 'status':'Results successfully added to Collective Knowledge (UID='+duid+')!', 'data_uid':duid, 'behavior_uid':buid}

##############################################################################
# record unexpected behavior

def process_unexpected_behavior(i):
    """
    Input:  {
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import os

    duid=i.get('data_uid','')
    buid=i.get('behavior_uid','')
    cuid=i.get('crowd_uid','')
    rres=i.get('raw_results','')
    ca=i.get('correct_answer','')
    file_base64=i.get('file_base64','')

    # Find data
    r=ck.access({'action':'load',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duid})
    if r['return']>0: return r
    d=r['dict']
    p=r['path']

    # Find behavior
    found=False
    arr=d.get('all_raw_results',[])
    for q in arr:
        if q.get('behavior_uid','')==buid:
            found=True
            break

    if not found:
        return {'return':1, 'error':'can\'t find behavior '+buid+' in entry '+duid}

    # Generate UID for the file with unexpected behavior
    rx=ck.gen_uid({})
    if rx['return']>0: return rx

    ff='misprediction-image-'+rx['data_uid']+'.jpg'

    pf=os.path.join(p,ff)

    mp=q.get('mispredictions',[])

    qq={}
    qq['misprediction_results']=rres
    qq['mispredicted_image']=ff
    qq['correct_answer']=ca

    mp.append(qq)

    q['mispredictions']=mp

    # Record file
    rx=ck.convert_upload_string_to_file({'file_content_base64':file_base64,
                                         'filename':pf})
    if rx['return']>0: return rx

    # Update entry (should add lock in the future for parallel processing)
    r=ck.access({'action':'update',
                 'module_uoa':work['self_module_uid'],
                 'data_uoa':duid,
                 'dict':d,
                 'sort_keys':'yes',
                 'substitute':'yes',
                 'ignore_update':'yes'})
    if r['return']>0: return r

    return {'return':0}
