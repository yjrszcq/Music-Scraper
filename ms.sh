#!/usr/bin/env bash

CONDA_ENV="music-scraper"
PY_SCRIPT="/path/to/music-scraper.py"

if ! command -v conda >/dev/null 2>&1; then
    echo "Error: conda command not found."
    exit 1
fi

eval "$(conda shell.bash hook)"

if [ "$CONDA_DEFAULT_ENV" != "$CONDA_ENV" ]; then
    if ! conda activate "$CONDA_ENV"; then
        echo "Error: Failed to activate Conda environment: $CONDA_ENV"
        exit 1
    fi
fi

exec python "$PY_SCRIPT" "$@"
