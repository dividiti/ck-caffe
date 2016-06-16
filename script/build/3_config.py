#!/usr/bin/python

import os
import sys
import json


def update(settings):
  # CLBlast dependency.
  ck_env_lib_clblast = os.environ.get('CK_ENV_LIB_CLBLAST')
  if ck_env_lib_clblast:
    settings['use_clblast'    ] = 1
    settings['clblast_include'] = os.path.join(ck_env_lib_clblast, 'include') 
    settings['clblast_lib'    ] = os.path.join(ck_env_lib_clblast, 'lib')

  return settings

def generate(template, settings):
  config = template.format(
    use_index_64    = settings['use_index_64'   ],
    cpu_only        = settings['cpu_only'       ],
    use_cuda        = settings['use_cuda'       ],
    use_cudnn       = settings['use_cudnn'      ],
    use_greentea    = settings['use_greentea'   ],
    use_libdnn      = settings['use_libdnn'     ],
    viennacl_dir    = settings['viennacl_dir'   ],
    viennacl_debug  = settings['viennacl_debug' ],
    use_clblas      = settings['use_clblas'     ],
    clblas_include  = settings['clblas_include' ],
    clblas_lib      = settings['clblas_lib'     ],
    use_clblast     = settings['use_clblast'    ],
    clblast_include = settings['clblast_include'],
    clblast_lib     = settings['clblast_lib'    ],
    use_isaac       = settings['use_isaac'      ],
    use_opencv      = settings['use_opencv'     ],
    opencv_version  = settings['opencv_version' ],
    use_leveldb     = settings['use_leveldb'    ],
    use_lmdb        = settings['use_lmdb'       ],
    use_fft         = settings['use_fft'        ],
    blas            = settings['blas'           ],
    blas_include    = settings['blas_include'   ],
    blas_lib        = settings['blas_lib'       ],
    debug           = settings['debug'          ]
  )
  return config

def main(args):
  if len(args) != 5:
    program_cmd = args[0]
    print("ERROR: %s" % program_cmd)
    print("Called as:")
    print args
    print("Should be called as:")
    print("%s <in: template> <in: settings> <out: settings> <out: config>" % program_cmd)
    return

  template_path     = args[1]
  settings_in_path  = args[2]
  settings_out_path = args[3]
  config_path       = args[4]

  with open(template_path, "r") as template_file:
    template = template_file.read()

  with open(settings_in_path, "r") as settings_file:
    settings = json.load(settings_file)

  settings = update(settings)

  with open(settings_out_path, "w") as settings_file:
    json.dump(settings, settings_file, indent=2)

  config = generate(template, settings)

  with open(config_path, "w") as config_file:
    config_file.write(config)

if __name__ == "__main__":
  main(sys.argv)
