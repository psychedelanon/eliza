#!/bin/bash
# Launch AquaAgent with environment variables
set -e

# Default model settings if not already provided
export LOCAL_LARGE_MODEL="${LOCAL_LARGE_MODEL:-DeepHermes-3-Llama-3-3B-Preview-q4.gguf}"
export MODELS_DIR="${MODELS_DIR:-$HOME/.eliza/models}"

# Informational output
echo "Using LOCAL_LARGE_MODEL=$LOCAL_LARGE_MODEL"
echo "Using MODELS_DIR=$MODELS_DIR"

# Start AquaAgent via the project starter script
bun run packages/project-starter/src/launchAquaAgent.ts "$@"
