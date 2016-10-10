#!/bin/bash
ck autotune pipeline:program pipeline_from_file=_setup_program_pipeline_tmp.json @dvdt_prof_cjson_alexnet_clblast.json "$@"
