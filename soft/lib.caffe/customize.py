#
# Collective Knowledge (individual environment - setup)
#
# See CK LICENSE.txt for licensing details
# See CK COPYRIGHT.txt for copyright details
#
# Developer: Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os

##############################################################################
# setup environment setup

def setup(i):
    """
    Input:  {
              cfg              - meta of this soft entry
              self_cfg         - meta of module soft
              ck_kernel        - import CK kernel module (to reuse functions)

              host_os_uoa      - host OS UOA
              host_os_uid      - host OS UID
              host_os_dict     - host OS meta

              target_os_uoa    - target OS UOA
              target_os_uid    - target OS UID
              target_os_dict   - target OS meta

              target_device_id - target device ID (if via ADB)

              tags             - list of tags used to search this entry

              env              - updated environment vars from meta
              customize        - updated customize vars from meta

              deps             - resolved dependencies for this soft

              interactive      - if 'yes', can ask questions, otherwise quiet
            }

    Output: {
              return       - return code =  0, if successful
                                         >  0, if error
              (error)      - error text if return > 0

              bat          - prepared string for bat file
            }

    """

    import os

    # Get variables
    ck=i['ck_kernel']
    shell_setup_script_contents = ''

    iv=i.get('interactive','')

    deps=i['deps']

    cus=i.get('customize',{})
    fp=cus.get('full_path','')

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    win=tosd.get('windows_base','')
    remote=tosd.get('remote','')
    mingw=tosd.get('mingw','')
    file_extensions = tosd.get('file_extensions',{})

    # Check platform
    tplat=tosd.get('ck_name','')
    tplat2=tosd.get('ck_name2','')
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    remote=tosd.get('remote','')
    tbits=tosd.get('bits','')

    env=i['env']

    fpr=''
    fp0=os.path.basename(fp)
    fp1=os.path.dirname(fp)
    fp2=os.path.basename(fp1)

    if fp2=='Release' or fp2=='Debug':
       fpr=fp2

    # When targeting Android, we do not create tools via Caffe, but later via CK
    # In such case, we reference .so file instead of bin when registering soft ...
    if not fp0.endswith('.so'): 
       env['CK_CAFFE_BIN']=fp0
    else:
       # Check extra .so extensions to be copied to Android device
       for y in os.listdir(fp1):
           y1=os.path.join(fp1,y)
           if y1.startswith(fp):
              if 'adb_extra_files' not in cus: 
                 cus['adb_extra_files']=[]
              cus['adb_extra_files'].append(y1)

    pi=fp
    found=False
    while True:
       if os.path.isdir(os.path.join(pi,'include')):
          found=True
          break
       pix=os.path.dirname(pi)
       if pix==pi:
          break
       pi=pix

    if not found:
       return {'return':1, 'error':'can\'t find root dir of the CAFFE installation'}

#    path_bin=os.path.dirname(fp)
    path_bin=os.path.join(pi,'bin')

    cus['path_bin']=path_bin

    path_lib = os.path.join(pi,'lib')
    if fpr!='': path_lib = os.path.join(path_lib,fpr)

    if not os.path.isdir(path_lib):
       path_lib = os.path.join(pi,'lib')
       if not os.path.isdir(path_lib):
          path_lib = os.path.join(pi,'.build_release','lib')
          if not os.path.isdir(path_lib):
             return {'return':1, 'error':'can\'t find lib dir of the CAFFE installation'}

    ep=cus.get('env_prefix','')

    cus['path_lib'] = path_lib
    cus['path_include']=os.path.join(pi,'include')

    sext = file_extensions.get('lib','')
    dext = file_extensions.get('dll','')

    if hplat=='win':
       fp5=os.path.dirname(pi)
       fp6=os.path.join(fp5,'libraries','libraries')
       fp7=os.path.join(fp6,'bin')
       fp7l=os.path.join(fp6,'lib')
       fp7l1=os.path.join(fp6,'x64','vc14','bin')
       fp8=''
       if os.path.isdir(fp7):
          fp8=';'+fp7+';'+fp7l+';'+fp7l1

       if remote=='yes' or mingw=='yes': 
          sext='.a'
          dext='.so'

          shell_setup_script_contents += 'set LD_LIBRARY_PATH="'+path_lib+'":$LD_LIBRARY_PATH\n'

       else:
          env['CK_CAFFE_CLASSIFICATION_BIN']='classification.exe'

       shell_setup_script_contents += 'set PATH='+path_bin+fp8+';%PATH%\n'

    else:

       path_example_classification=os.path.join(os.path.dirname(path_bin),'examples','cpp_classification')

       for ppx in ['classification.bin', 'classification']:
           ppy=os.path.join(path_bin,ppx)
           if os.path.isfile(ppy):
              env['CK_CAFFE_CLASSIFICATION_BIN']=ppx
              break

       shell_setup_script_contents += 'export PATH='+path_bin+':'+path_example_classification+':$PATH\n'
       if path_lib:
            r = ck.access({ 'action': 'lib_path_export_script',
                            'module_uoa': 'os',
                            'host_os_dict': hosd,
                            'lib_path': path_lib })
            if r['return']>0: return r
            shell_setup_script_contents += r['script']

    lib_prefix = '' if win=='yes' else 'lib'
    cus['static_lib']  = lib_prefix +'caffe' + sext
    cus['dynamic_lib'] = lib_prefix +'caffe' + dext

    env[ep+'_STATIC_NAME']=cus.get('static_lib','')
    env[ep+'_DYNAMIC_NAME']=cus.get('dynamic_lib','')

    env[ep]=pi

    env[ep+'_EXTRA_INCLUDE']=os.path.join(pi,'.build_release','src')

    env['CAFFE_INSTALL_DIR']=pi

    # Check if compiled with Python
    ppy=os.path.join(pi,'python')
    ppy1=os.path.join(ppy,'caffe')
    if tplat2!='android' and os.path.isdir(ppy) and os.path.isdir(ppy1):
       env[ep+'_PYTHON']=ppy
       if hplat=='win':
          shell_setup_script_contents += '\n\nset PYTHONPATH='+ppy+';%PYTHONPATH%\n\n'
       else:
          shell_setup_script_contents += '\n\nexport PYTHONPATH='+ppy+':$PYTHONPATH\n\n'

    if tplat=='win':
       env[ep+'_CFLAGS']='/D CMAKE_WINDOWS_BUILD'
       env[ep+'_CXXFLAGS']='/D CMAKE_WINDOWS_BUILD'

       env[ep+'_LFLAG']=os.path.join(path_lib,'caffe.lib')

       x=os.path.join(path_lib,'proto.lib')
       if not os.path.isfile(x):
          x=os.path.join(path_lib,'caffeproto.lib')

       env[ep+'_LFLAG_PROTO']=x

       # WAS A HACK - need to check BOOST version and vc ...
       # x='/link /NODEFAULTLIB:libboost_date_time-vc140-mt-1_62.lib /NODEFAULTLIB:libboost_filesystem-vc140-mt-1_62.lib /NODEFAULTLIB:libboost_system-vc140-mt-1_62.lib /NODEFAULTLIB:libboost_date_time-vc140-mt-1_64.lib /NODEFAULTLIB:libboost_filesystem-vc140-mt-1_64.lib /NODEFAULTLIB:libboost_system-vc140-mt-1_64.lib'
       x='/link'
       all_vc=['120','140','141']
       all_boost=['1_60','1_62','1_64','1_65','1_66']
       all_lb=['boost_date_time', 'boost_filesystem', 'boost_system']

       x1=deps.get('compiler',{}).get('dict',{}).get('env',{}).get('CK_ENV_COMPILER_MVSC_VC_MSBUILD','')
       if x1!='':
          all_vc=[x1]
          x2=deps.get('lib-boost',{})

          x3=x2.get('dict',{}).get('env',{}).get('CK_ENV_LIB_BOOST_VER','')
          if x3=='':
             x2uoa=x2.get('uoa','')
             if x2uoa!='':
                # Load deps
                rx=ck.access({'action':'load',
                              'module_uoa':'env',
                              'data_uoa':x2uoa})
                if rx['return']==0:
                   x2d=rx['dict']
                   x3=x2d.get('env',{}).get('CK_ENV_LIB_BOOST_VER','')
                   if x3=='':
                      x3=x2d.get('env',{}).get('CK_ENV_LIB_BOOST_SHORT_VER','')

          if x3=='':
             x4=x2.get('version_from',[])
             if len(x4)>1:
                x3=str(x4[0])+'.'+str(x4[1])

          if x3!='':
             x3=x3.replace('.','_')

             all_boost=[x3]

       for q1 in all_lb:
           for q2 in all_boost:
               for q3 in all_vc:
                   x+=' /NODEFAULTLIB:lib'+q1+'-vc'+q3+'-mt-'+q2+'.lib'
                   if tbits=='64':
                      x+=' /NODEFAULTLIB:lib'+q1+'-vc'+q3+'-mt-x64-'+q2+'.lib'

       if cus.get('extra_link_win','')!='':
          x+=' '+cus['extra_link_win']

       env[ep+'_LINK_FLAGS']=x

    return {'return':0, 'bat':shell_setup_script_contents}
