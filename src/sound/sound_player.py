import asyncio
import math
from pathlib import Path
import winsound  # Для Windows
import platform
import subprocess
import tempfile
import os

from morse_text import MorseText


BASE_DIR = Path(__file__).resolve().parent

dotSound = BASE_DIR / 'beep_dot.wav'
dashSound = BASE_DIR / 'beep_dash.wav'

class MorseSoundPlayer:
    """Класс для воспроизведения звуков Морзе"""
    
    def __init__(self, dot_duration=40, frequency=600):
        self.dot_duration = dot_duration
        self.frequency = frequency
        self.system = platform.system()
        self.sound_enabled = True
        self.current_task = None
    
    async def play_dot(self):
        """Воспроизвести звук точки"""
        if not self.sound_enabled:
            return
            
        duration = self.dot_duration
        if self.system == "Windows":
            # winsound.Beep(self.frequency, duration)
            winsound.PlaySound(dotSound, winsound.SND_FILENAME)
        elif self.system == "Darwin":  # macOS
            self._play_macos_beep(duration)
        else:  # Linux
            self._play_linux_beep(duration)
        await asyncio.sleep(duration / 1000)
    
    async def play_dash(self):
        """Воспроизвести звук тире"""
        if not self.sound_enabled:
            return
            
        duration = self.dot_duration * 3  # Тире в 3 раза длиннее точки
        if self.system == "Windows":
            # winsound.Beep(self.frequency, duration)
            winsound.PlaySound(dashSound, winsound.SND_FILENAME)
        elif self.system == "Darwin":  # macOS
            self._play_macos_beep(duration)
        else:  # Linux
            self._play_linux_beep(duration)
        await asyncio.sleep(duration / 1000)
    
    def _play_macos_beep(self, duration):
        """Воспроизведение звука на macOS"""
        try:
            # Создаем временный файл с тоном
            import wave
            import struct
            
            sample_rate = 44100
            duration_sec = duration / 1000.0
            t = [i / sample_rate for i in range(int(sample_rate * duration_sec))]
            wave_data = [int(32767 * 0.5 * math.sin(2 * math.pi * self.frequency * x)) for x in t]
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_file = f.name
                
                with wave.open(temp_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    
                    for sample in wave_data:
                        data = struct.pack('<h', sample)
                        wav_file.writeframes(data)
                
                # Воспроизводим через afplay
                subprocess.run(['afplay', temp_file], check=False)
                
                # Удаляем временный файл
                os.unlink(temp_file)
        except:
            # Fallback: печать символа бип
            print('\a')
    
    def _play_linux_beep(self, duration):
        """Воспроизведение звука на Linux"""
        try:
            # Пытаемся использовать beep или speaker-test
            subprocess.run(['beep', '-f', str(self.frequency), '-l', str(duration)], 
                         check=False, capture_output=True)
        except:
            try:
                # Альтернатива через speaker-test
                duration_sec = duration / 1000.0
                subprocess.run(['speaker-test', '-t', 'sine', '-f', str(self.frequency), 
                              '-l', '1'], timeout=duration_sec, check=False)
            except:
                # Последний вариант
                print('\a')
    
    async def play_morse_code(self, morse_code: str):
        """Воспроизвести код Морзе"""
        if not self.sound_enabled:
            return
            
        for char in morse_code:
            if char == '.':
                await self.play_dot()
                await asyncio.sleep(self.dot_duration / 1000)  # Пауза между символами
            elif char == '-':
                await self.play_dash()
                await asyncio.sleep(self.dot_duration / 1000)  # Пауза между символами
            elif char == ' ':
                # Пауза между буквами (3 точки)
                await asyncio.sleep(3 * self.dot_duration / 1000)
            elif char == '/':
                # Пауза между словами (7 точек)
                await asyncio.sleep(7 * self.dot_duration / 1000)
    
    async def play_text(self, text: str):
        """Воспроизвести текст в азбуке Морзе"""
        if not self.sound_enabled:
            return
            
        morse_sequence = []
        for char in text.lower():
            if char == ' ':
                morse_sequence.append('/')
            elif char in MorseText.symbolToCode:
                morse_sequence.append(MorseText.symbolToCode[char])
                morse_sequence.append(' ')
        
        morse_string = ' '.join(morse_sequence)

        await self.end_task()
        self.current_task = asyncio.create_task(self.play_morse_code(morse_string))

    
    def toggle_sound(self, enabled: bool):
        """Включить/выключить звук"""
        self.sound_enabled = enabled
    
    def set_speed(self, dot_duration: int):
        """Установить скорость (длительность точки в мс)"""
        self.dot_duration = dot_duration


    async def end_task(self):
        if self.current_task and not self.current_task.done():
            # отменяем старую задачу.
            self.current_task.cancel()
            try:
                await self.current_task  # Ожидаем завершения отмены
            except asyncio.CancelledError:
                pass



if __name__ == "__main__":
    sound_player = MorseSoundPlayer(dot_duration=40, frequency=600)
    # sound_player.play_morse_code('-.--')
    sound_player.play_text('Александра')