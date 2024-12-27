import subprocess
import re
import math

CHANNEL_FREQ = "193.75000"
Q_FACTOR = 1.3

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

print("Syr->Alb->Nyc")
stdout1 = run_shell_script("./syr-albgain.sh")
snr1_db = get_gsnr_from_table(stdout1, CHANNEL_FREQ)

stdout2 = run_shell_script("./alb-32gain.sh")
snr2_db = get_gsnr_from_table(stdout2, CHANNEL_FREQ)

if snr1_db and snr2_db:
    snr1_linear = 10 ** (float(snr1_db) / 10)
    snr2_linear = 10 ** (float(snr2_db) / 10)
    snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))
    snr_total_linear_esnr = snr_total_linear / Q_FACTOR
    snr_total_db = 10 * math.log10(snr_total_linear)
    snr_total_db_esnr = 10 * math.log10(snr_total_linear_esnr)
    
    print(f"Total OSNR: {snr_total_db:.2f} dB")
    print(f"Total eSNR: {snr_total_db_esnr:.2f} dB")
elif snr1_db:
    snr1_linear = 10 ** (float(snr1_db) / 10)
    snr1_linear_esnr = snr1_linear / Q_FACTOR
    snr1_db = 10 * math.log10(snr1_linear)
    snr1_db_esnr = 10 * math.log10(snr1_linear_esnr)
    
    print(f"Total OSNR: {snr1_db:.2f}")
    print(f"Total eSNR: {snr1_db_esnr:.2f}")
elif snr2_db:
    snr2_linear = 10 ** (float(snr2_db) / 10)
    snr2_linear_esnr = snr2_linear / Q_FACTOR
    snr2_db = 10 * math.log10(snr2_linear)
    snr2_db_esnr = 10 * math.log10(snr2_linear_esnr)
    
    print(f"Total OSNR: {snr2_db:.2f}")
    print(f"Total eSNR: {snr2_db_esnr:.2f}")
else:
    print("No SNR values found")
  
print()  
print("Nyc->Alb->Syr")
stdout1 = run_shell_script("./32-albgain.sh")
snr1_db = get_gsnr_from_table(stdout1, CHANNEL_FREQ)

stdout2 = run_shell_script("./alb-syrgain.sh")
snr2_db = get_gsnr_from_table(stdout2, CHANNEL_FREQ)

if snr1_db and snr2_db:
    snr1_linear = 10 ** (float(snr1_db) / 10)
    snr2_linear = 10 ** (float(snr2_db) / 10)
    snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))
    snr_total_linear_esnr = snr_total_linear / Q_FACTOR
    snr_total_db = 10 * math.log10(snr_total_linear)
    snr_total_db_esnr = 10 * math.log10(snr_total_linear_esnr)
    
    print(f"Total OSNR: {snr_total_db:.2f} dB")
    print(f"Total eSNR: {snr_total_db_esnr:.2f} dB")
elif snr1_db:
    snr1_linear = 10 ** (float(snr1_db) / 10)
    snr1_linear_esnr = snr1_linear / Q_FACTOR
    snr1_db = 10 * math.log10(snr1_linear)
    snr1_db_esnr = 10 * math.log10(snr1_linear_esnr)
    
    print(f"Total OSNR: {snr1_db:.2f}")
    print(f"Total eSNR: {snr1_db_esnr:.2f}")
elif snr2_db:
    snr2_linear = 10 ** (float(snr2_db) / 10)
    snr2_linear_esnr = snr2_linear / Q_FACTOR
    snr2_db = 10 * math.log10(snr2_linear)
    snr2_db_esnr = 10 * math.log10(snr2_linear_esnr)
    
    print(f"Total OSNR: {snr2_db:.2f}")
    print(f"Total eSNR: {snr2_db_esnr:.2f}")
else:
    print("No SNR values found")