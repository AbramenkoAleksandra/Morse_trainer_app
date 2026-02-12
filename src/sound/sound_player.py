import asyncio
import io
import wave

import flet_audio as fta
import numpy as np

from morse_text import MorseText

# !!! В Google Chrome загружать fta.Audio только после нажатия на какой-либо элемент страницы
class MorseSoundPlayer:
    """Класс для воспроизведения звуков Морзе"""

    def __init__(self, dot_duration=40, frequency=600, audioActivate=True):
        self.dot_duration = dot_duration
        self.frequency = frequency
        self.sound_enabled = True
        self.current_task = None
        self.audio_activated=audioActivate
        self.audio_completed_event = asyncio.Event()

        self.dotSound = self.generate_sine_wave_bytes(self.frequency, self.dot_duration/1000)
        self.dashSound = self.generate_sine_wave_bytes(self.frequency, self.dot_duration*3/1000)

        if self.audio_activated:
            self.activate_audio()
        else:
            self.audioDot = None
            self.audioDash = None
        


    def generate_sine_wave_bytes(self, frequncy = 600, durationSec = 1):
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
    

    def activate_audio(self):
        self.audioDot = fta.Audio(
            src=self.dotSound,
            autoplay=False,
            volume=1,
            balance=0,
            release_mode=fta.ReleaseMode.STOP,
            on_state_change=self.on_audio_state_changed
        )
        self.audioDash = fta.Audio(
            src=self.dashSound,
            autoplay=False,
            volume=1,
            balance=0,
            release_mode=fta.ReleaseMode.STOP,
            on_state_change=self.on_audio_state_changed
        )
        self.audio_activated=True


    def on_audio_state_changed(self, e):
        if e.state == fta.AudioState.COMPLETED:
            self.audio_completed_event.set() # Set the event when completed


    async def play_dot(self):
        """Воспроизвести звук точки"""
        if not self.sound_enabled or not self.audio_activated:
            return
            
        self.audio_completed_event.clear() # Clear event before playing again
        await self.audioDot.play()
        # Wait for the event to be set in the on_state_changed handler
        await self.audio_completed_event.wait()


    async def play_dash(self):
        """Воспроизвести звук тире"""
        if not self.sound_enabled or not self.audio_activated:
            return
            
        self.audio_completed_event.clear() # Clear event before playing again
        await self.audioDash.play()
        await self.audio_completed_event.wait()


    async def play_morse_code(self, morse_code: str):
        """Воспроизвести код Морзе"""
        if not self.sound_enabled or not self.audio_activated:
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
        if not self.sound_enabled or not self.audio_activated:
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
        if dot_duration<5 or dot_duration>200: return
        self.dot_duration = dot_duration
        self.dotSound = self.generate_sine_wave_bytes(self.frequency, self.dot_duration/1000)
        self.dashSound = self.generate_sine_wave_bytes(self.frequency, self.dot_duration*3/1000)


    async def end_task(self):
        if self.current_task and not self.current_task.done():
            # отменяем старую задачу.
            self.current_task.cancel()
            try:
                await self.current_task  # Ожидаем завершения отмены
            except asyncio.CancelledError:
                pass


if __name__ == "__main__":
    import flet as ft

    def main(page: ft.Page):
        async def play_code():
            if page.web and not sound_player.audio_activated:
                sound_player.activate_audio()
            await sound_player.play_morse_code('..- .-.')

        async def play_text():
            if page.web and not sound_player.audio_activated:
                sound_player.activate_audio()
            await sound_player.play_text('Алекс')

        def set_speed(duration_change):
            sound_player.set_speed(sound_player.dot_duration+duration_change)


        page.add(ft.Button("play_code", on_click=play_code))
        page.add(ft.Button("play_text", on_click=play_text))
        page.add(
            ft.Row(
                controls=[
                    ft.Button("Speed down", on_click=lambda _: set_speed(-5)),
                    ft.Button("Speed up", on_click=lambda _: set_speed(5)),
                ]
            ),
        )
        sound_player = MorseSoundPlayer(dot_duration=40, frequency=600, audioActivate=False if page.web else True)

                 
    ft.run(
        main,
        # view=ft.AppView.WEB_BROWSER,
    )