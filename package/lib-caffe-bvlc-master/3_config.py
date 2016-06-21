#!/usr/bin/python

import os
import sys
import json

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
