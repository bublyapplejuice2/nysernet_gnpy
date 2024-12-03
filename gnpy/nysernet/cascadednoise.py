import math

snr1_db = 18.3
snr2_db = 14.6

snr1_linear = 10 ** (snr1_db / 10)
snr2_linear = 10 ** (snr2_db / 10)

snr_total_linear = 1 / ((1 / snr1_linear) + (1 / snr2_linear))

snr_total_db = 10 * math.log10(snr_total_linear)
print(f"Total SNR: {snr_total_db:.2f} dB")