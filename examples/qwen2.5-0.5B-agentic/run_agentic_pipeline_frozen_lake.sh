#!/bin/bash
set +x
export CUDA_VISIBLE_DEVICES=2,5


CONFIG_PATH=$(basename $(dirname $0))
python examples/start_agentic_pipeline.py --config_path $CONFIG_PATH  --config_name agent_val_frozen_lake_grpo

