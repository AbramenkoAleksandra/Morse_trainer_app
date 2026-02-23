import io
import math
import struct
import wave


class AudioGenerator:
    @staticmethod
    def generate_sine_wave_bytes(frequncy: int = 600, durationSec: float = 1):
        """
        Generates a sine wave and returns its data in WAV format as bytes.
        """
        # Configuration
        sample_rate = 44100             # Industry standard sample rate (CD quality) Hz
        frequency_hz = frequncy         # Frequency of the beep (Hz)
        duration_seconds = durationSec  # Duration of the beep (seconds)
        volume = 0.5                    # Volume (0.0 to 1.0) - Keep amplitude below 1 to avoid clipping 
        MAX_AMP = 32767.0               # Max value for signed 16-bit integer

        # 1. Generate audio samples (as floats in -1.0 to 1.0 range)
        samples = []
        for i in range(int(sample_rate * duration_seconds)):
            # Calculate the time at this sample index
            t = i / sample_rate
            # Generate the sine wave data
            # Formula: volume * sin(2 * pi * frequency * time)
            # time = x / sample_rate
            amplitude = volume * math.sin(2 * math.pi * frequency_hz * t)
            samples.append(amplitude)

        # 2. Scale samples to signed 16-bit integers and pack into bytes
        raw_samples = b''
        for sample in samples:
            # Scale float to 16-bit integer range
            int_sample = int(sample * MAX_AMP)
            # Clip to ensure no overflow
            if int_sample > MAX_AMP:
                int_sample = int(MAX_AMP)
            elif int_sample < -MAX_AMP - 1: # -32768 is the min value
                int_sample = int(-MAX_AMP - 1)
            
            # Pack the signed short integer 'h' into bytes in little-endian '<' format
            raw_samples += struct.pack('<h', int_sample)

        # 3. Write to a BytesIO buffer to get WAV formatted bytes without a physical file
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_samples)
            
        # Get the complete WAV data from the start of the BytesIO object
        return buffer.getvalue()
     

if __name__ == "__main__":
    import winsound
    beepSound=AudioGenerator.generate_sine_wave_bytes()
    winsound.PlaySound(beepSound, winsound.SND_MEMORY)