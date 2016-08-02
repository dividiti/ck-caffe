#!/bin/bash
ck autotune pipeline:program pipeline_from_file=_setup_program_pipeline_tmp.json @explore_batch_size_squeezenet_1.0_clblas.json "$@"
