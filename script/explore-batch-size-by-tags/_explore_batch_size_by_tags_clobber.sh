#!/bin/bash
./_explore_batch_size_by_tags_clean.sh
ck rm experiment:* --tags=gpu_time
