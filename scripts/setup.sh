#!/bin/bash

# Get the current working directory
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the parent folder path
parent_dir="$(dirname "$script_dir")"
cd "$parent_dir"

# sh ./scripts/create-venv.sh
# sh ./scripts/activate-venv.sh
sh ./scripts/requirements.sh
