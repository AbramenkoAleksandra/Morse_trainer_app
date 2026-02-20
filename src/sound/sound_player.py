import asyncio

import flet_audio as fta

from sound.audio_generator import AudioGenerator
from text_converter import ConvertionType, TextConverter

# !!! В Google Chrome загружать fta.Audio только после нажатия на какой-либо элемент страницы
class MorseSoundPlayer:
    """Класс для воспроизведения звуков Морзе"""

    def __init__(self, dot_duration: int = 40, frequency: int = 600, audioActivate: bool = True, dot_audio_duration: int | None = None):
        self.dot_duration = dot_duration
        self.dot_audio_duration = dot_audio_duration or self.dot_duration
        self.frequency = frequency
        self._volume = 1
        self.sound_enabled = True
        self.current_task = None
        self.audio_activated=audioActivate
        self.audio_completed_event = asyncio.Event()
        self.audio_loaded_event = asyncio.Event()

        self.sounds = {}
        self.audioDict: dict[str, fta.Audio] = {}

        self.generate_audio('dot', frequency=self.frequency, duration_sec=self.dot_audio_duration/1000)
        self.generate_audio('dash', frequency=self.frequency, duration_sec=self.dot_audio_duration*3/1000)

        if self.audio_activated:
            asyncio.create_task(self.activate_audio())


    def generate_audio(self, name: str, frequency=None, duration_sec=1):
        if frequency is None: frequency=self.frequency
        sound = AudioGenerator.generate_sine_wave_bytes(frequency, duration_sec)
        self.sounds[name]=sound
        return sound
    

    def audio_set(self, name: str, src):
        audio = fta.Audio(
            src=src,
            autoplay=False,
            volume=self.volume,
            balance=0,
            release_mode=fta.ReleaseMode.STOP,
            on_state_change=self.on_audio_state_changed,
            on_loaded=self.on_audio_loaded,
            data=name,
            key=name,
        )
        self.audioDict[name]=audio
        return audio
    

    async def activate_audio(self):
        self.audio_loaded_event.clear()
        self.audio_set('dot', self.sounds.get('dot'))
        await self.audio_loaded_event.wait()
        self.audio_loaded_event.clear()
        self.audio_set('dash', self.sounds.get('dash'))
        await self.audio_loaded_event.wait()

        self.audio_activated=True


    def set_speed(self, dot_audio_duration: int=None, dot_duration: int=None, equal=True):
        """Установить скорость (длительность точки в мс)"""
        if equal:
            dot_duration=dot_duration or dot_audio_duration
            dot_audio_duration=dot_audio_duration or dot_duration
        if dot_duration and dot_duration>=5 and dot_duration<=200:
            self.dot_duration = dot_duration
        if dot_audio_duration and dot_audio_duration>=5 and dot_audio_duration<=200:
            self.dot_audio_duration = dot_audio_duration
            if dot:=self.audioDict.get('dot'):
                dot.src = self.generate_audio('dot', frequency=self.frequency, duration_sec=self.dot_audio_duration/1000)
            if dash:=self.audioDict.get('dash'):
                dash.src = self.generate_audio('dash', frequency=self.frequency, duration_sec=self.dot_audio_duration*3/1000)


    @property
    def volume(self):
        return self._volume


    @volume.setter
    def volume(self, volume: float):
        if volume<0 or volume>1: return
        for a in self.audioDict.values():
            a.volume = volume
        self._volume=volume


    def on_audio_loaded(self, e):
        audio: fta.Audio = e.control
        print(f"on load {audio.key}: {e}")
        self.audio_loaded_event.set()


    def on_audio_state_changed(self, e):
        if e.state == fta.AudioState.COMPLETED:
            self.audio_completed_event.set() # Set the event when completed


    async def play_audio(self, audio: fta.Audio):
        if not self.sound_enabled or not self.audio_activated:
            return
        
        self.audio_completed_event.clear() # Clear event before playing again
        await audio.play()
        await self.audio_completed_event.wait()


    async def play_dot(self):
        """Воспроизвести звук точки"""
        if audio:= self.audioDict.get('dot'):
            await self.play_audio(audio=audio)


    async def play_dash(self):
        """Воспроизвести звук тире"""
        if audio:= self.audioDict.get('dash'):
            await self.play_audio(audio=audio)


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
        
        morse_string=TextConverter.convert(text, ConvertionType.SYMBOL_MORSE)

        await self.end_task()
        self.current_task = asyncio.create_task(self.play_morse_code(morse_string))

    
    def toggle_sound(self, enabled: bool):
        """Включить/выключить звук"""
        self.sound_enabled = enabled
    

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
        speedText = ft.Ref[ft.Text]()
        speedDotText = ft.Ref[ft.Text]()
        async def play_code():
            if page.web and not sound_player.audio_activated:
                await sound_player.activate_audio()
            await sound_player.play_morse_code('..- .-.')

        async def play_text():
            if page.web and not sound_player.audio_activated:
                await sound_player.activate_audio()
            await sound_player.play_text('Алекс')

        def set_speed(duration_change):
            speed=int(speedText.current.value)+duration_change
            sound_player.set_speed(speed)
            speedText.current.value = sound_player.dot_audio_duration
            speedDotText.current.value = sound_player.dot_duration


        def set_dot_duration(duration_change):
            speed=int(speedDotText.current.value)+duration_change
            sound_player.set_speed(dot_duration=speed, equal=False)
            speedDotText.current.value = sound_player.dot_duration


        page.add(ft.Button("play_code", on_click=play_code))
        page.add(ft.Button("play_text", on_click=play_text))
        page.add(ft.Row(controls=[ft.Text(value="Длительность аудио точки (мс): "),ft.Text(ref=speedText)]))
        page.add(
            ft.Row(
                controls=[
                    ft.Button("Speed down", on_click=lambda _: set_speed(-5)),
                    ft.Button("Speed up", on_click=lambda _: set_speed(5)),
                ]
            ),
        )
        page.add(ft.Row(controls=[ft.Text(value="Длительность точки (мс): "),ft.Text(ref=speedDotText)]))
        page.add(
            ft.Row(
                controls=[
                    ft.Button("Speed down", on_click=lambda _: set_dot_duration(-5)),
                    ft.Button("Speed up", on_click=lambda _: set_dot_duration(5)),
                ]
            ),
        )
        sound_player = MorseSoundPlayer(dot_duration=40, frequency=600, audioActivate=False if page.web else True)
        speedText.current.value = sound_player.dot_duration
        speedDotText.current.value = sound_player.dot_duration

                 
    ft.run(
        main,
        # view=ft.AppView.WEB_BROWSER, host='0.0.0.0', port=8550,
    )