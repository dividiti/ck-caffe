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
              (local)            - if 'yes', local crowd-benchmarking, instead of public
              (user)             - force different user ID/email for demos
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0
            }

    """

    import copy

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

    # Check target device
    target=i.get('target','')

    if target=='':
        # Check and possibly select target machines
        r=ck.search({'module_uoa':cfg['module_deps']['machine'], 'data_uoa':target, 'add_meta':'yes'})
        if r['return']>0: return r

        dlst=r['lst']

        # Prune search by only required devices
        rdat=['wa_linux', 'wa_android']

        xlst=[]

        if len(rdat)==0:
            xlst=dlst
        else:
            for q in dlst:
                if q.get('meta',{}).get('access_type','') in rdat:
                    xlst.append(q)

        if len(xlst)==0:
            return {'return':1, 'error':'no suitable target devices found (use "ck add machine" to register new target device)'}
        elif len(xlst)==1:
            target=xlst[0]['data_uoa']
        else:
            # SELECTOR *************************************
            ck.out('')
            ck.out('Please select target device to run your workloads on:')
            ck.out('')
            r=ck.select_uoa({'choices':xlst})
            if r['return']>0: return r
            target=r['choice']

    if target=='':
        return {'return':1, 'error':'--target machine is not specified (see "ck list machine")'}

    ck.out('')
    ck.out('Selected target machine: '+target)
    ck.out('')

    i['target']=target

    # Initialize local environment for program optimization ***********************************************************
    pi=i.get('platform_info',{})
    if len(pi)==0:
       ii=copy.deepcopy(i)
       ii['action']='initialize'
       ii['module_uoa']=cfg['module_deps']['program.optimization']
       ii['exchange_repo']=er
       ii['exchange_subrepo']=esr
       ii['skip_welcome']='yes'
       ii['skip_log_wait']='yes'
       ii['crowdtuning_type']='wa-crowd-benchmarking'
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

    # Start preparing input to run WA ...
    ii=copy.deepcopy(i)

    ii['action']='run'
    ii['module_uoa']=cfg['module_deps']['wa']

    ii['host_os']=hos
    ii['target']=target
    ii['target_os']=tos
    ii['target_device_id']=tdid

    ii['scenario_module_uoa']=work['self_module_uid']

    ii['exchange_repo']=er
    ii['exchange_subrepo']=esr
    ii['share']='yes'
    ii['scenario_module_uoa']=work['self_module_uid']

    ii['user']=user

    rr=ck.access(ii)

    return rr
