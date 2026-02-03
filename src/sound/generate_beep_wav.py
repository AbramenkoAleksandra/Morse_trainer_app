"""
Генерация звука точки, тире и просто beep
"""

import math
from pathlib import Path
import numpy as np
from scipy.io.wavfile import write

BASE_DIR = Path(__file__).resolve().parent

def generate_beep(filename=BASE_DIR/ "beep.wav", durationSec = 1, frequncy = 600):
    sample_rate = 44100  # Industry standard sample rate (CD quality)
    frequency_hz = frequncy # Frequency of the beep (Hz)
    duration_seconds = durationSec # Duration of the beep (seconds)
    volume = 0.5 # Volume (0.0 to 1.0)
    output_filename = filename

    # --- Generate the sine wave ---
    # Calculate the total number of samples
    num_samples = int(duration_seconds * sample_rate)

    # Generate an array of time values (x-axis)
    # x ranges from 0 to num_samples - 1
    x = np.arange(num_samples)

    # Generate the sine wave data
    # Formula: volume * sin(2 * pi * frequency * time)
    # time = x / sample_rate
    waveform = volume * np.sin(2 * math.pi * frequency_hz * (x / sample_rate))

    # --- Convert to 16-bit integer format ---
    # WAV files often use 16-bit signed integers.
    # The maximum value for a 16-bit signed integer is 32767.
    waveform_int = np.int16(waveform * 32767)

    # --- Write to a WAV file ---
    write(output_filename, sample_rate, waveform_int)

    print(f"Successfully created '{output_filename}'")



def generate_all(duration=60, frequncy=600):
    durationSec=duration/1000
    generate_beep(frequncy=frequncy)
    generate_beep(BASE_DIR/ "beep_dot.wav", durationSec, frequncy=frequncy)
    generate_beep(BASE_DIR/ "beep_dash.wav", durationSec * 3, frequncy=frequncy)


if __name__ == "__main__":
    generate_all(duration=40, frequncy=600)