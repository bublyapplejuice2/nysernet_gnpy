#!/bin/bash
source .venv/bin/activate
gnpy-transmission-example gnpy/nysernet/alb-syrgain.json -e gnpy/nysernet/eqpt_config_gain.json --spectrum gnpy/nysernet/syr-albspectrum.json --sim-params gnpy/nysernet/sim_params.json --show-channels
echo "193.8: 17.9 alb->syr"