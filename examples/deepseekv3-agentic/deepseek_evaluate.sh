#!/bin/bash

# 任何命令失败立即退出
set -e

# 退出时（无论成功/失败/中断）都关机
# trap 'echo "[$(date)] 脚本退出，10秒后关机... "; sleep 10; /bin/shutdown -h now' EXIT

# 1. 限制 OpenBLAS 线程数
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1

# 2. 增加进程限制
ulimit -u 65536
export HF_HOME=/root/autodl-tmp/hf-mirror
export HF_ENDPOINT=https://hf-mirror.com


# 3. 循环运行评估脚本, 每个环境评估三次
for file in examples/deepseekv3-agentic/run_agentic_rollout_pipeline_frozen_lake.sh 
# examples/deepseekv3-agentic/run_agentic_rollout_pipeline_simple_sokoban.sh examples/deepseekv3-agentic/run_agentic_rollout_pipeline_larger_sokoban.sh examples/deepseekv3-agentic/run_agentic_rollout_pipeline_larger_bandit_summary.sh examples/deepseekv3-agentic/run_agentic_rollout_pipeline_larger_bandit.sh 
# examples/deepseekv3-agentic/run_agentic_rollout_pipeline_simple_bandit.sh examples/deepseekv3-agentic/run_agentic_rollout_pipeline_bandit.sh 
# examples/deepseekv3-agentic/run_agentic_rollout_pipeline_frozen_lake.sh
do
    for run_id in 1 2 3
    do
        echo "[$(date)] 运行 $file (第 $run_id 次)"
        bash $file >> eval.log
        # 如果上面这行失败，脚本立即退出，触发 trap 关机
    done
done

echo "[$(date)] 所有评估完成！"
# 脚本正常结束，也会触发 trap 关机