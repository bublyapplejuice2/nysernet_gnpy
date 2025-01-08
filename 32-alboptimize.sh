#!/bin/bash
source .venv/bin/activate

# Read the path to the network JSON file from the environment variable
NETWORK_JSON_PATH="$NETWORK_JSON"

# Ensure the file exists
if [[ ! -f "$NETWORK_JSON_PATH" ]]; then
    echo "Error: Network JSON file not found at $NETWORK_JSON_PATH"
    exit 1
fi

# Use the NETWORK_JSON_PATH in the gnpy-transmission-example command
gnpy-transmission-example "$NETWORK_JSON_PATH" \
    -e gnpy/nysernet/eqpt_config_gain.json \
    --spectrum gnpy/nysernet/alb-32spectrum.json \
    --sim-params gnpy/nysernet/sim_params.json \
    --show-channels