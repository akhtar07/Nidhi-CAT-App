#!/bin/bash
# Serves the local model for Milestone 7 LLM generation (SPEC.md §6.3).
# Model + pip environment both live on /data (root disk only has ~7GB free
# — see PROGRESS.md). Run this, wait for "Application startup complete",
# then in another shell: python -m qagen.run_llm (from /pipeline, using the
# cat-llm env's python).
set -e

ENV=/data/Nidhi_backup_run/conda_envs/cat-llm
export HF_HOME=/data/Nidhi_backup_run/hf_cache
export VLLM_MODEL_NAME="${VLLM_MODEL_NAME:-Qwen/Qwen2.5-32B-Instruct-AWQ}"
# The conda env's own libstdc++ (new enough for vllm's deps) otherwise
# loses to this Ubuntu 20.04 box's older system one on the default search
# path — found via ImportError on CXXABI_1.3.15 during vllm's sqlite3 import.
export LD_LIBRARY_PATH="$ENV/lib:$LD_LIBRARY_PATH"

"$ENV/bin/python" -m vllm.entrypoints.openai.api_server \
  --model "$VLLM_MODEL_NAME" \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.90 \
  --port 8000
