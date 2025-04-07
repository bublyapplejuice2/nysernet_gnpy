import subprocess
import re
import math
import argparse

def run_shell_script(script_name):
    try:
        result = subprocess.run([script_name], capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        return ""

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

def get_final_roadm_effective_pch_power(stdout):
    return stdout.split("effective pch (dBm):")[-1].split("\n")[0].strip()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Calculate total OSNR for specified channel frequency.")
    parser.add_argument("channel_freq", type=float, help="Channel frequency as a float (e.g., 193.5)")
    args = parser.parse_args()
    
    # Ensure the channel frequency has 5 decimal places
    channel_freq = f"{args.channel_freq:.5f}"

    print("Syr->Alb->Nyc")
    stdout1 = run_shell_script("./syr-albgain.sh")
    snr1_db = get_gsnr_from_table(stdout1, channel_freq)

    stdout2 = run_shell_script("./alb-32gain.sh")
    snr2_db = get_gsnr_from_table(stdout2, channel_freq)

    if snr1_db and snr2_db:
        snr1_linear = 10 ** (float(snr1_db) / 10)
        snr2_linear = 10 ** (float(snr2_db) / 10)
        snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))
        snr_total_db = 10 * math.log10(snr_total_linear)
        
        print(f"Total OSNR: {snr_total_db:.2f} dB")
    elif snr1_db:
        snr1_linear = 10 ** (float(snr1_db) / 10)
        snr1_db = 10 * math.log10(snr1_linear)
        
        print(f"Total OSNR: {snr1_db:.2f}")
    elif snr2_db:
        snr2_linear = 10 ** (float(snr2_db) / 10)
        snr2_db = 10 * math.log10(snr2_linear)
        
        print(f"Total OSNR: {snr2_db:.2f}")
    else:
        print("No SNR values found")

    print()  
    print("Nyc->Alb->Syr")
    stdout1 = run_shell_script("./32-albgain.sh")
    snr1_db = get_gsnr_from_table(stdout1, channel_freq)

    stdout2 = run_shell_script("./alb-syrgain.sh")
    snr2_db = get_gsnr_from_table(stdout2, channel_freq)

    if snr1_db and snr2_db:
        snr1_linear = 10 ** (float(snr1_db) / 10)
        snr2_linear = 10 ** (float(snr2_db) / 10)
        snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))
        snr_total_db = 10 * math.log10(snr_total_linear)
        
        print(f"Total OSNR: {snr_total_db:.2f} dB")
    elif snr1_db:
        snr1_linear = 10 ** (float(snr1_db) / 10)
        snr1_db = 10 * math.log10(snr1_linear)
        
        print(f"Total OSNR: {snr1_db:.2f}")
    elif snr2_db:
        snr2_linear = 10 ** (float(snr2_db) / 10)
        snr2_db = 10 * math.log10(snr2_linear)
        
        print(f"Total OSNR: {snr2_db:.2f}")
    else:
        print("No SNR values found")

if __name__ == "__main__":
    main()