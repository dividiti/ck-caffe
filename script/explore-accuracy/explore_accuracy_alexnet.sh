#!/bin/bash
ck autotune pipeline:program pipeline_from_file=_setup_program_pipeline_tmp.json @explore_accuracy_alexnet.json "$@"
