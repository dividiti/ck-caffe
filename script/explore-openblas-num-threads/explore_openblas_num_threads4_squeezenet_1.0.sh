#!/bin/bash
ck autotune pipeline:program pipeline_from_file=_setup_program_pipeline_tmp.json @explore_openblas_num_threads4_squeezenet_1.0.json "$@"
