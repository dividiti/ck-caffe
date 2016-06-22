#!/usr/bin/python

#
# Developer: Anton Lokhmomtov, anton@dividiti.com
#            Grigori Fursin, Grigori.Fursin@cTuning.org, http://fursin.net
#

import os
import sys
import json

##############################################################################
# customize installation

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
              return        - return code =  0, if successful
                                          >  0, if error
              (error)       - error text if return > 0
              (install-env) - prepare environment to be used before the install script
            }

    """

    # Get variables
    ck=i['ck_kernel']
    s=''

    hosd=i['host_os_dict']
    tosd=i['target_os_dict']

    # Check platform
    hplat=hosd.get('ck_name','')

    hproc=hosd.get('processor','')
    tproc=tosd.get('processor','')

    iv=i.get('interactive','')
    cus=i.get('customize',{})
    cfg=i.get('cfg',{})

    ie={}
    ie['CK_TEST_TEST']='abcxyz'

    return {'return':0, 'install_env':ie}

##############################################################################
def update(settings):
  # C++ compiler dependency.
  ck_cxx = os.environ.get('CK_CXX')
  if ck_cxx:
    settings['custom_cxx'] = ck_cxx
  # BLAS library dependency.
  open_blas = os.environ.get('CK_ENV_LIB_OPENBLAS')
  if open_blas:
    settings['cpu_blas'] = 'open'
    settings['cpu_blas_lib'] = os.path.join(open_blas, 'lib') 
    settings['cpu_blas_include'] = os.path.join(open_blas, 'include')
  return settings

##############################################################################
def generate(template, settings):
  config = template.format(
    cpu_only         = settings['cpu_only'        ],
    cpu_blas         = settings['cpu_blas'        ],
    cpu_blas_lib     = settings['cpu_blas_lib'    ],
    cpu_blas_include = settings['cpu_blas_include'],
    use_opencv       = settings['use_opencv'      ],
    opencv_version   = settings['opencv_version'  ],
    use_leveldb      = settings['use_leveldb'     ],
    use_lmdb         = settings['use_lmdb'        ],
    custom_cxx       = settings['custom_cxx'      ],
    debug            = settings['debug'           ]
  )
  return config

##############################################################################
def main(args):
  if len(args) != 5:
    program_cmd = args[0]
    print("ERROR: %s" % program_cmd)
    print("Called as:")
    print(args)
    print("Should be called as:")
    print("%s <in: template> <in: settings> <out: settings> <out: config>" % program_cmd)
    return

  template_path     = args[1]
  settings_in_path  = args[2]
  settings_out_path = args[3]
  config_path       = args[4]

  # Read template file.
  with open(template_path, "r") as template_file:
    template = template_file.read()

  # Read file with partial settings.
  with open(settings_in_path, "r") as settings_file:
    settings = json.load(settings_file)

  # Complete settings.
  settings = update(settings)

  # Write file with complete settings (for future reference).
  with open(settings_out_path, "w") as settings_file:
    json.dump(settings, settings_file, indent=2)

  # Generate config file.
  config = generate(template, settings)

  # Write config file.
  with open(config_path, "w") as config_file:
    config_file.write(config)

if __name__ == "__main__":
  main(sys.argv)
