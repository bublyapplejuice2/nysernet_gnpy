import json
import re
import math
import subprocess
import optuna
from optuna.storages import RDBStorage
import multiprocessing
import tempfile
import os
import shutil

# File paths
EQPT_CONFIG_FILE = "gnpy/nysernet/eqpt_config_gain.json"
NETWORK_JSON = "gnpy/nysernet/32-albgain.json"
DIRECTION = "nyc-alb-syr"

# Load equipment config
with open(EQPT_CONFIG_FILE, 'r') as f:
    eqpt_config = json.load(f)

def get_gain_limits(type_variety):
    for edfa in eqpt_config["Edfa"]:
        if edfa["type_variety"] == type_variety:
            return edfa["gain_min"], edfa["gain_flatmax"]
    raise ValueError(f"Unknown type_variety: {type_variety}")

def simulate_network(direction, segment, json_file_path):
    script_mapping = {
        ("nyc-alb-syr", "segment1"): "./32-alboptimize.sh",
        ("nyc-alb-syr", "segment2"): "./alb-syrgain.sh",
        ("syr-alb-nyc", "segment1"): "./syr-albgain.sh",
        ("syr-alb-nyc", "segment2"): "./alb-32optimize.sh",
    }

    script_name = script_mapping.get((direction, segment))
    if not script_name:
        raise ValueError(f"No script found for direction '{direction}' and segment '{segment}'")

    # Set the JSON file path as an environment variable for the shell script
    env = os.environ.copy()
    env["NETWORK_JSON"] = json_file_path  # Pass the temporary file path to the shell script

    try:
        result = subprocess.run([script_name], capture_output=True, text=True, env=env, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error running script '{script_name}': {e}")

# Extract GSNR from shell output
def get_gsnr_from_table(stdout, channel_freq):
    table_regex = r"^\s*(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$"
    lines = stdout.split("The GSNR per channel at the end of the line is:")[1].split("\n")
    
    for line in lines:
        match = re.match(table_regex, line)
        if match:
            ch_id = match.group(2)  # Channel ID
            gsnr = match.group(6)  # GSNR (signal bw, dB)
            if ch_id == channel_freq:
                return gsnr

    return None

# Calculate OSNR for the specified direction
def calculate_osnr(direction, channel_freq, json_file_path):
    # Simulate the first segment
    stdout1 = simulate_network(direction, segment="segment1", json_file_path=json_file_path)
    snr1_db = get_gsnr_from_table(stdout1, channel_freq)

    # Simulate the second segment
    stdout2 = simulate_network(direction, segment="segment2", json_file_path=json_file_path)
    snr2_db = get_gsnr_from_table(stdout2, channel_freq)

    # Calculate total OSNR
    if snr1_db and snr2_db:
        snr1_linear = 10 ** (float(snr1_db) / 10)
        snr2_linear = 10 ** (float(snr2_db) / 10)
        snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))
        return 10 * math.log10(snr_total_linear)
    elif snr1_db:
        return float(snr1_db)
    elif snr2_db:
        return float(snr2_db)
    else:
        raise ValueError("No SNR values found in simulation outputs")

# Objective function for Optuna
def objective(trial):
    # Create a temporary file in /dev/shm for the worker (RAM-backed filesystem)
    with tempfile.NamedTemporaryFile(mode="w+", dir="/dev/shm", suffix=".json", delete=False) as temp_json:
        temp_json_path = temp_json.name
        shutil.copyfile(NETWORK_JSON, temp_json_path)  # Copy original JSON to temp file

        try:
            # Update the temp JSON with trial-specific gain targets
            with open(temp_json_path, "r") as f:
                network_data = json.load(f)

            gain_targets = []
            for element in network_data["elements"]:
                if element["type"] == "Edfa":
                    type_variety = element["type_variety"]
                    gain_min, gain_max = get_gain_limits(type_variety)
                    gain_target = trial.suggest_float(f"gain_target_{element['uid']}", gain_min, gain_max, step=0.5)
                    element["operational"]["gain_target"] = gain_target  # Update JSON
                    gain_targets.append(gain_target)

            # Write updated network data back to temp JSON
            with open(temp_json_path, "w") as f:
                json.dump(network_data, f, indent=4)

            # Run the simulation and calculate OSNR
            osnr = calculate_osnr(DIRECTION, channel_freq="193.50000", json_file_path=temp_json_path)

        finally:
            # Ensure the temp file is removed after use
            os.remove(temp_json_path)

        return osnr  # Maximize OSNR

# Function for worker processes
def optimize_worker(storage_url, study_name):
    study = optuna.load_study(study_name=study_name, storage=storage_url)
    study.optimize(objective, n_trials=10)  # Each worker runs a subset of trials

if __name__ == "__main__":
    # Set up the shared storage
    storage_url = "sqlite:///optuna_study.db"  # SQLite for simplicity
    study_name = "osnr_optimization"

    # Create the study
    optuna.create_study(study_name=study_name, direction="maximize", storage=storage_url, load_if_exists=True)

    # Number of worker processes
    n_workers = multiprocessing.cpu_count()

    # Start worker processes
    processes = []
    for _ in range(n_workers):
        p = multiprocessing.Process(target=optimize_worker, args=(storage_url, study_name))
        processes.append(p)
        p.start()

    # Wait for all workers to finish
    for p in processes:
        p.join()

    # Output the best results
    study = optuna.load_study(study_name=study_name, storage=storage_url)
    print("Best gain_target values:", study.best_params)
    print("Best OSNR:", study.best_value)
