import asyncio
from collections import defaultdict
from datetime import datetime
import json
import os
from pathlib import Path
from random import choice as randomChoice, shuffle as randomShuffle
import sys

import flet as ft

from controls.keyboard import Keyboard
from controls.text_field import TextFieldControl
from sound.sound_player import MorseSoundPlayer
from learning_program import LearningProgram, TrainingType
from morse_text import MorseText

lp = LearningProgram()

if getattr(sys, 'frozen', False):
    # Если приложение запущено через PyInstaller
    BASE_DIR = os.path.dirname(sys.executable)
    progress_file = os.path.join(BASE_DIR, 'morse_progress.json')
else:
    # Если приложение запущено через python
    # basedir = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = Path(__file__).resolve().parent
    progress_file = BASE_DIR / 'morse_progress.json'


class MorseTrainer:
    """Страница тренажера с практикой"""
    def __init__(self, page: ft.Page, current_level=1):
        self.page = page
        self.sound_player = MorseSoundPlayer()
        self.current_level = current_level
        self.last_level = current_level
        self.setup_page()
        self.user_progress = {}
        self.load_progress()
        self.load_level()
        self.showMode = True
        self.build_ui()
        self.current_text=None
        self.current_morse_text=None
        self.training_type = None
        self.questions = []
        self.hint_type=0
        self.errorCount=0
        self.set_training_type(TrainingType.LETTER)


    def setup_page(self):
        """Настройка страницы"""
        self.page.title = "Азбука Морзе - тренажер"
        self.page.window.min_width=800
        self.page.window.min_height=550

        # self.page.theme=ft.Theme(color_scheme_seed=ft.Colors.GREEN_400)

        
        # При закрытии приложения

        def window_event(e: ft.WindowEvent):
            if e.type == ft.WindowEventType.CLOSE:
                asyncio.create_task(self.sound_player.end_task())
                self.page.show_dialog(confirm_dialog)
                self.page.update()

        # Предотвращаем закрытие по нажатию "X"
        self.page.window.prevent_close = True
        self.page.window.on_event = window_event


        async def handle_yes_click(e: ft.Event[ft.Button]):
            await self.page.window.destroy()


        def handle_no_click(e: ft.Event[ft.OutlinedButton]):
            self.page.pop_dialog()
            self.page.update()


        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Подтвердите, пожалуйста"),
            content=ft.Text("Вы действительно хотите выйти из программы?"),
            actions=[
                ft.Button(content="Да", on_click=handle_yes_click),
                ft.OutlinedButton(content="Нет", on_click=handle_no_click),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )


        # При закрытии браузера

        def handle_disconnect(e):
            print("User disconnected (browser tab closed or refreshed).")
            asyncio.create_task(self.sound_player.end_task())
            

        self.page.on_disconnect = handle_disconnect



    def load_level(self, level=None):
        '''Загрузка текущего уровня'''

        level = level or self.current_level

        if levelInfo:=lp.levels.get(level,0):
            self.current_level=level
            self.last_level=max(self.current_level, self.last_level)
            self.letters = levelInfo['letters']
            self.newLetters = levelInfo['new_letters']
            self.words = levelInfo['words']
            self.letterTrainingCount = levelInfo['letter_training_count']
            self.wordsTrainingCount = levelInfo['words_training_count']
            self.level_progress = defaultdict(lambda: {'total': 0, 'correct': 0})
            

    def load_progress(self):
        """Загрузка прогресса пользователя"""
        try:
            with open(progress_file, 'r', encoding='utf8') as f:
                data = json.load(f)
                self.current_level = data.get('current_level', self.current_level)
                self.last_level = data.get('last_level', self.last_level)
                self.user_progress = defaultdict(
                    lambda: {'total': 0, 'correct': 0},
                    data.get('user_progress', {})
                )
                self.last_level_progress = defaultdict(
                    lambda: {'total': 0, 'correct': 0},
                    data.get('last_level_progress', {})
                )
        except FileNotFoundError:
            self.user_progress = defaultdict(lambda: {'total': 0, 'correct': 0})


    def save_progress(self):
        """Сохранение прогресса пользователя"""

        data = {
            'current_level': self.current_level,
            'last_level': self.last_level,
            'user_progress': self.user_progress,
            'last_level_progress': self.last_level_progress,
            'last_saved': datetime.now().isoformat()
        }
        with open(progress_file, 'w', encoding='utf8') as f:
            json.dump(data, f, indent=2)


    async def playCurrentText(self):
        """Проиграть морзянку текущего текста"""
        if self.current_text is None: return

        asyncio.create_task(self.sound_player.play_text(self.current_text))


    async def playMorseSound(self, text):
        """Проиграть морзянку указанного текста"""
        asyncio.create_task(self.sound_player.play_text(text))


    # Можно перенести в key_click
    def space_click(self, e):
        if self.training_type == TrainingType.PHRASE:
            # Добавляем пробел к текущему тексту
            self.text_field.add_value(' ')


    def key_click(self, e):
        """Функция события нажатия клавиши виртуальной клавиатуры"""

        if self.showMode:
            asyncio.create_task(self.playMorseSound(e.control.key))
            return

        match self.training_type:
            case TrainingType.LETTER:
                self.check_text_answer(e)
            case TrainingType.WORD | TrainingType.PHRASE:
                # Добавляем символ клавиши к текущему тексту
                self.text_field.add_value(e.control.key)

        # self.page.update()


    def build_ui(self, update=False):
        """Построение пользовательского интерфейса"""

        # Паттерн для текстового поля
        regex_pattern = r"^[" + "".join(self.letters) + ' ' + r"]*$"

        if update:
            self.showMode=True
            
            self.levelInfo.value=f'Уровень {self.current_level}:\n{', '.join(self.newLetters)}'
            self.mainTextField.value=''
            self.mainTextField.visible=False
            self.msgTextField.value='?'

            self.keyboard = Keyboard(activeKeys=self.letters, on_click=self.key_click, hintVisible=self.showMode, userProgress=self.user_progress)
            self.content_area.controls[1]=self.keyboard
        
            self.text_field.set_input_filter(regex_pattern)

            if not lp.levels.get(self.current_level-1,0):
                self.prevLevelGo.disabled=True
            else:
                self.prevLevelGo.disabled=False

            if not lp.levels.get(self.current_level+1,0) or self.last_level<=self.current_level:
                self.nextLevelGo.disabled=True
            else:
                self.nextLevelGo.disabled=False

            self.levelButtons.disabled=True

            self.content_area.disabled=not self.showMode
            return
        
        # ВЕРХНИЙ КОНТЕЙНЕР
        # Текстовое поле вверху экрана
        self.mainTextField = ft.Text(value='', size=18, weight=ft.FontWeight.W_400, text_align=ft.TextAlign.CENTER, visible=False)


        # ЦЕНТРАЛЬНЫЙ КОНТЕЙНЕР
        
        # Левая часть - уровни
        self.levelInfo = ft.Text(
            value=f'Уровень {self.current_level}:\n{', '.join(self.newLetters)}',
            size=14,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.CENTER,
            expand=1
        )

        self.prevLevelGo = ft.IconButton(
            icon=ft.Icons.ARROW_LEFT,
            key='prevLevel',
            padding=ft.padding.all(2),
            margin=ft.margin.all(0),
            icon_size=20,
            size_constraints=ft.BoxConstraints(max_height=30, max_width=30),
            alignment=ft.Alignment.CENTER,
            on_click=self.set_level
        )

        self.nextLevelGo = ft.IconButton(
            icon=ft.Icons.ARROW_RIGHT,
            key='nextLevel',
            padding=ft.padding.all(2),
            margin=ft.margin.all(0),
            icon_size=20,
            size_constraints=ft.BoxConstraints(max_height=30, max_width=30),
            alignment=ft.Alignment.CENTER,
            on_click=self.set_level
        )

        if not lp.levels.get(self.current_level-1,0):
                self.prevLevelGo.disabled=True

        if not lp.levels.get(self.current_level+1,0) or self.last_level<=self.current_level:
            self.nextLevelGo.disabled=True

        self.levelContainer = ft.Row(
            controls=ft.Row([
                    self.prevLevelGo,
                    self.levelInfo,
                    self.nextLevelGo
                ],
                expand=False,
                alignment=ft.MainAxisAlignment.START
            ),
            alignment=ft.MainAxisAlignment.START,
            expand=1
        )



        # Центральная часть - Сообщение, подсказка
        self.msgTextField = ft.Text(value='?', size=24, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER, expand=1)
        self.startLevelButton = ft.FilledButton(
            content='Начать уровень',
            on_click=self.start_training,
            style=ft.ButtonStyle(
                padding=ft.Padding.only(left=20, right=20, top=20, bottom=20),
                text_style=ft.TextStyle(
                    size=19,
                    weight=ft.FontWeight.BOLD
                ),
                # shape=ft.RoundedRectangleBorder(radius=14)
            )
        )
        self.CenterContainer = ft.Row(controls=[self.startLevelButton], alignment=ft.MainAxisAlignment.CENTER, expand=2)


        # Правая часть - кнопки показать подстказку и проиграть звук
        self.levelButtons = ft.Row([
                ft.FilledIconButton(ft.Icons.QUESTION_MARK, on_click=self.hint_show, tooltip='Показать подсказку'),
                ft.FilledIconButton(ft.Icons.VOLUME_UP, on_click=self.playCurrentText, tooltip='Повторить')
            ],
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            disabled=True
        )


        # НИЖНИЙ КОНТЕЙНЕР

        # Поле ввода
        self.text_field = TextFieldControl(on_submit=self.check_text_answer, regex_string=regex_pattern)

        self.keyboard = Keyboard(activeKeys=self.letters, on_click=self.key_click, hintVisible=self.showMode, userProgress=self.user_progress)

        self.content_area = ft.Column(controls=[
                self.text_field,
                self.keyboard
            ],
            alignment=ft.MainAxisAlignment.END,
            # expand=3,
            disabled=not self.showMode,
        )

        self.page.add(
            ft.Row(self.mainTextField, alignment=ft.MainAxisAlignment.CENTER, expand=False),
            ft.Row(
                controls=[
                    self.levelContainer,
                    self.CenterContainer,
                    self.levelButtons
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=2
            ),
            self.content_area
        )

    
    def change_key_progress(self, e, num):
        if not self.letterTrainingCount: return

        res = e.control.progress.value
        res +=num/self.letterTrainingCount
        if res > 1:
            res = 1
        if res < 0:
            res = 0
        e.control.progress.value = res

    
    def add_progress(self, key, total: int=0, correct: int=0):
        if total:
            self.user_progress[key]['total']+=total
            self.level_progress[key]['total']+=total
        if correct:
            self.user_progress[key]['correct']+=correct
            self.level_progress[key]['correct']+=correct



    def check_text_answer(self, e, text: str | None = None, morse_text: str | None = None):
        """Проверка ответа"""

        if text is None:
            text = self.current_text
        if morse_text is None:
            morse_text = self.current_morse_text

        if text is None or morse_text is None:
            return
        
        if self.training_type == TrainingType.LETTER:
            checked_text = e.control.key
            self.add_progress(e.control.key, total=1)
            # self.level_progress[e.control.key]['total']+=1
        if self.training_type == TrainingType.WORD or self.training_type == TrainingType.PHRASE:
            checked_text = self.text_field.value.strip()


        # При правильном ответе
        if checked_text.lower()==text.lower():

            self.show_message('Правильно', color=ft.Colors.GREEN_700)
            
            if self.training_type == TrainingType.LETTER:
                if self.errorCount:
                    # Добавить текущую букву к questions
                    self.questions.append(e.control.key)
                    randomShuffle(self.questions)
                    self.errorCount=0
                else:
                    self.change_key_progress(e, 1)
                    self.add_progress(e.control.key, correct=1)
                    # self.level_progress[e.control.key]['correct']+=1
            else:
                self.text_field.clear_text()
                self.text_field.border_color=ft.Colors.GREEN_700


            async def background_task():
                await self.sound_player.end_task()
                await asyncio.sleep(1)
                self.hint_hide()
                self.page.update()
                self.start_training()

            self.page.run_task(background_task)
        # При неправильном ответе
        else:
            if self.training_type == TrainingType.LETTER:
                # Убрать прогресс на нажатую кнопку
                self.change_key_progress(e, -1)
                self.errorCount+=1

                # Добавить нажатую букву к questions
                self.questions.append(e.control.key)
                randomShuffle(self.questions)
            else:
                self.text_field.border_color=ft.Colors.ERROR

            self.show_message('Попробуйте еще...', ft.Colors.ERROR)
            
            self.page.update()

            async def background_task():
                await self.sound_player.end_task()
                await asyncio.sleep(1)
                asyncio.create_task(self.playMorseSound(text))

            self.page.run_task(background_task)
    

    def textToMorse(self, text: str):
        return ' '.join(MorseText.symbolToCode[char] for char in text.lower())
    

    def show_message(self, text, color: ft.Colors | None = None):
        textAfter=self.msgTextField.value
        colorAfter=self.msgTextField.color
        if self.hint_type==0:
            message=text
        else:
            message=f'{text}\n{textAfter}'

        self.msgTextField.value = message
        if color:
            self.msgTextField.color = color
        self.page.update()

        # Очистить сообщение через указанное время
        async def clear_message():
            await asyncio.sleep(1)
            if self.msgTextField.value == message:  # Только если не изменилось
                self.msgTextField.value = textAfter
                self.msgTextField.color = colorAfter
                self.page.update()
        
        asyncio.create_task(clear_message())


    def hint_show(self, firstLetter):
        """Показать подсказку (код Морзе)"""
        match self.hint_type:
            case 0:
                self.show_morse_code()
                self.hint_type=1
            case 1:
                self.keyboard.hint_show()
                self.hint_type=2
            case 2:
                self.hint_hide()


    def hint_hide(self):
        """Убрать подсказку (код Морзе)"""

        self.msgTextField.value = '?'

        if self.hint_type>1:
            self.keyboard.hint_hide()
        self.hint_type = 0
    

    def show_morse_code(self, morse_text: str = None):
        """Показать код Морзе для текста"""
        if morse_text is None:
            morse_text = self.current_morse_text
        self.msgTextField.value = morse_text



    def set_level(self, e=None, level=None):
        """Загрузить уровень"""

        if e:
            if not self.showMode: return
            if e.control.key=='prevLevel':
                level = self.current_level-1
            elif e.control.key=='nextLevel':
                level = self.current_level+1
                if level>self.last_level: return
            
        if not level:
            level = self.current_level
        self.load_level(level)
        self.build_ui(update=True)
        self.set_training_type(TrainingType.LETTER)



    def set_training_type(self, type: TrainingType = TrainingType.LETTER):
        """Загрузить тип тренировки в уровне"""

        self.questions = lp.questionsGenerate(self.current_level, type)

        if self.questions:
            match type:
                case TrainingType.LETTER:
                    self.text_field.visible=False
                    self.mainTextField.value='1. Тренировка букв'
                case TrainingType.WORD:
                    self.text_field.visible=True
                    self.mainTextField.value='2. Тренировка слов'
                case TrainingType.PHRASE:
                    self.text_field.visible=True
                    self.mainTextField.value='3. Тренировка фраз'
                    self.keyboard.add_space(on_click=self.space_click)
                case _:
                    return
            
        self.training_type = type
        self.page.update()    


    def start_training(self, e = None):
        """Начать тренировку"""
        # По нажатию на кнопку Начать уровень
        if e:
            self.CenterContainer.controls = self.msgTextField
            self.mainTextField.visible=True
            self.content_area.disabled=False
            self.levelButtons.disabled=False
            self.showMode = False
            self.keyboard.hide_data(hintHide=True, progressHide=True)
            self.page.update()

        match self.training_type:
            case TrainingType.LETTER:
                self.start_letter_training()
            case TrainingType.WORD:
                self.start_word_training()
            case TrainingType.PHRASE:
                self.start_phrase_training()


    def end_training(self):  
        # Сделать пересчет прогресса
        self.last_level_progress=self.level_progress
        # self.msgTextField.color = ft.Colors.GREEN_700
        self.startLevelButton.content='Следующий уровень'
        self.CenterContainer.controls = [
            self.startLevelButton
        ]
        self.set_level(level=self.current_level+1)
        self.save_progress()


    def start_input_training(self, trainingType: TrainingType = TrainingType.LETTER):
        """Начать тренировку на прием сигнала"""

        # Выбираем случайный вопрос
        if self.questions:
            question = self.questions.pop()
        else:
            match self.training_type:
                case TrainingType.LETTER:
                    self.start_word_training()
                case TrainingType.WORD:
                    self.start_phrase_training()
                case TrainingType.PHRASE:
                    self.end_training()
                case _:
                    self.end_training()
            return

        morse_question = self.textToMorse(question)

        self.current_text = question
        self.current_morse_text = morse_question

        # Показываем подсказку на новую букву (только при тренировке букв)

        if self.training_type == TrainingType.LETTER:
            if question in self.newLetters and (self.level_progress.get(question,0)==0 or self.level_progress[question]['correct']==0):
                self.msgTextField.value = question
                self.page.update()
        else:
            self.text_field.set_focus()


        asyncio.create_task(self.playMorseSound(question))



    def start_letter_training(self):
        """Начать тренировку букв"""

        self.start_input_training(TrainingType.LETTER)


    def start_word_training(self):
        """Начать тренировку слов"""
        if self.training_type != TrainingType.WORD:
            self.set_training_type(TrainingType.WORD)

        self.start_input_training(TrainingType.WORD)


    def start_phrase_training(self):
        """Начать тренировку фраз"""
        if self.training_type != TrainingType.PHRASE:
            self.set_training_type(TrainingType.PHRASE)

        self.start_input_training(TrainingType.PHRASE)




    

    


 
