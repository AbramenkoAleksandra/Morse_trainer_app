import io
import wave
import numpy as np


class AudioGenerator:
    @staticmethod
    def generate_sine_wave_bytes(frequncy: int = 600, durationSec: float = 1):
        """
        Generates a sine wave and returns its data in WAV format as bytes.
        """
        sample_rate = 44100             # Industry standard sample rate (CD quality)
        frequency_hz = frequncy         # Frequency of the beep (Hz)
        duration_seconds = durationSec  # Duration of the beep (seconds)
        volume = 0.5                    # Volume (0.0 to 1.0) - Keep amplitude below 1 to avoid clipping 

        # Generate the time points
        t = np.linspace(0., duration_seconds, int(sample_rate * duration_seconds), endpoint=False)
        # Generate the sine wave data
        # Formula: volume * sin(2 * pi * frequency * time)
        # time = x / sample_rate
        audio_data = volume * np.sin(2. * np.pi * frequency_hz * t)
        
        # Convert to 16-bit integers - The maximum value for a 16-bit signed integer is 32767.
        audio_data = (audio_data * 32767).astype(np.int16)

        raw_samples = audio_data.tobytes()
        
        # Write to a BytesIO buffer to get WAV formatted bytes without a physical file
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