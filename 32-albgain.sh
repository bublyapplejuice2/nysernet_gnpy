#!/bin/bash
source .venv/bin/activate
gnpy-transmission-example gnpy/nysernet/32-albgain.json -e gnpy/nysernet/eqpt_config_gain.json --spectrum gnpy/nysernet/alb-32spectrum.json --sim-params gnpy/nysernet/sim_params.json --show-channels