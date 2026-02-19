import asyncio
from random import choice as randomChoice, shuffle as randomShuffle

import flet as ft

from app.utils.progress_sync import load_progress, save_progress, Level
from app.utils.learning_program import LearningProgram, TrainingType
from controls.keyboard import Keyboard
from controls.text_field import TextFieldControl
from controls.level_controls import CenterContainer, LevelIconButton, LevelSwitcher, LevelGoButton, MainTextField, StartLevelButton
from sound.sound_player import MorseSoundPlayer
from morse_text import MorseText

lp = LearningProgram()


class MorseTrainer:
    """Страница тренажера с практикой"""
    def __init__(self, page: ft.Page, current_level=1):
        self.page = page
        self.sound_player = MorseSoundPlayer(
            audioActivate=False if page.web else True,
            # На ios в браузере большая задержка звука, если меньше 90 - точки не слышно (попробовать другой вариант для решения)
            dot_duration=100 if page.web and page.platform==ft.PagePlatform.IOS else 40
        )
        self.level = Level(current_level=current_level, last_level=current_level)
        self.setup_page()
        self.level = load_progress(self.level)
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
        self.page.window.min_width=400
        self.page.window.min_height=350

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

        self.page.on_resize = self.page_resize


    def get_size_for_keyboard(self, e = None):
        height = e.height if e else None or self.page.height or self.page.window.height
        width = e.width if e else None or self.page.width or self.page.window.width
        if not height or not width: return (None, None)
        if width/height>2:
            return (width, height*0.5)
        else:
            return (width, height*0.4)


    def page_resize(self, e):
        if self.keyboard:
            width, height = self.get_size_for_keyboard(e)
            self.keyboard.resize(maxWidth=width, maxHeight=height)
            size = self.keyboard.key_size

            if self.controlsToResize:
                self.resize_controls(self.controlsToResize, size)


    def load_level(self, level: int | None = None):
        '''Загрузка текущего уровня'''

        level = level or self.level.current_level

        if levelInfo:=lp.levels.get(level,0):
            self.level.current_level=level
            self.level.last_level=max(self.level.current_level, self.level.last_level)
            self.letters = levelInfo['letters']
            self.newLetters = levelInfo['new_letters']
            self.words = levelInfo['words']
            self.letterTrainingCount = levelInfo['letter_training_count']
            self.wordsTrainingCount = levelInfo['words_training_count']
            self.level.level_progress = Level().level_progress # Reset levelProgress
            

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


    async def key_click(self, e):
        """Функция события нажатия клавиши виртуальной клавиатуры"""

        if self.showMode:
            if self.page.web and not self.sound_player.audio_activated:
                await self.sound_player.activate_audio()

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

        width, height = self.get_size_for_keyboard()

        if update:
            self.showMode=True
            
            self.levelSwitcherRef.current.set_level_info(self.level.current_level,self.newLetters)
            self.mainTextFieldRef.current.value=''
            self.mainTextFieldRef.current.visible=False
            self.centerRef.current.resetMsgText()
            
            # Сделать обновление, а не пересоздание
            self.keyboard = Keyboard(activeKeys=self.letters,
                                     on_click=self.key_click,
                                     hintVisible=self.showMode, userProgress=self.level.user_progress,
                                     maxWidth=width, maxHeight=height)
            self.content_area.controls[1]=self.keyboard
        
            self.text_field.set_input_filter(regex_pattern)

            if not lp.levels.get(self.level.current_level-1,0):
                self.prevLevelGoRef.current.disabled=True
            else:
                self.prevLevelGoRef.current.disabled=False

            if not lp.levels.get(self.level.current_level+1,0) or self.level.last_level<=self.level.current_level:
                self.nextLevelGoRef.current.disabled=True
            else:
                self.nextLevelGoRef.current.disabled=False

            self.levelButtons.disabled=True

            self.content_area.disabled=not self.showMode
            return
        
        self.mainTextFieldRef = ft.Ref[MainTextField]()
        
        self.hintShowBtnRef = ft.Ref[LevelIconButton]()
        self.repeatSoundBtnRef = ft.Ref[LevelIconButton]()

        self.prevLevelGoRef = ft.Ref[LevelGoButton]()
        self.nextLevelGoRef = ft.Ref[LevelGoButton]()
        self.levelSwitcherRef = ft.Ref[LevelSwitcher]()

        self.centerRef = ft.Ref[CenterContainer]()

        self.textFieldRef = ft.Ref[TextFieldControl]()

        self.controlsToResize=[self.mainTextFieldRef, self.textFieldRef, self.centerRef, self.hintShowBtnRef, self.repeatSoundBtnRef, self.levelSwitcherRef]
        
        # ВЕРХНИЙ КОНТЕЙНЕР
        # Текстовое поле вверху экрана
        mainTextField = MainTextField(value='', visible=False, ref=self.mainTextFieldRef)


        # ЦЕНТРАЛЬНЫЙ КОНТЕЙНЕР
        
        # Левая часть - уровни

        levelSwitcher = LevelSwitcher(
            currentLevel=self.level.current_level, newLetters=self.newLetters,
            on_click=self.set_level,
            prevLevelRef=self.prevLevelGoRef,
            nextLevelRef=self.nextLevelGoRef,
            ref=self.levelSwitcherRef,
        )
        

        if not lp.levels.get(self.level.current_level-1,0):
            self.prevLevelGoRef.current.disabled=True

        if not lp.levels.get(self.level.current_level+1,0) or self.level.last_level<=self.level.current_level:
            self.nextLevelGoRef.current.disabled=True



        # Центральная часть - Сообщение, подсказка

        centerContainer = CenterContainer(
            btnText='Начать уровень',
            ref=self.centerRef,
            on_click=self.start_training
        )

        
        # Правая часть - кнопки показать подсказку и проиграть звук
        self.levelButtons = ft.Row([
                LevelIconButton(icon=ft.Icons.QUESTION_MARK, on_click=self.hintShowBtn_click, tooltip='Показать подсказку', ref=self.hintShowBtnRef),
                LevelIconButton(icon=ft.Icons.VOLUME_UP, on_click=self.playCurrentText, tooltip='Повторить', ref=self.repeatSoundBtnRef)
            ],
            expand=1,
            alignment=ft.MainAxisAlignment.END,
            disabled=True,
            spacing=10,
        )


        # НИЖНИЙ КОНТЕЙНЕР

        # Поле ввода
        self.text_field = TextFieldControl(on_submit=self.check_text_answer,
                                           regex_string=regex_pattern,
                                           ref=self.textFieldRef
                                           )

        self.keyboard = Keyboard(activeKeys=self.letters,
                                 on_click=self.key_click,
                                 hintVisible=self.showMode, userProgress=self.level.user_progress,
                                 maxWidth=width, maxHeight=height)

        self.content_area = ft.Column(controls=[
                self.text_field,
                self.keyboard
            ],
            alignment=ft.MainAxisAlignment.END,
            disabled=not self.showMode,
        )

        self.page.add(
            ft.Row(mainTextField, alignment=ft.MainAxisAlignment.CENTER, expand=False),
            ft.Row(
                controls=[
                    levelSwitcher,
                    centerContainer,
                    self.levelButtons
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                expand=2,
                margin=ft.Margin.symmetric(horizontal=5)
            ),
            self.content_area
        )


        size = self.keyboard.key_size

        self.resize_controls(cList=self.controlsToResize, size=size)


    def resize_controls(self, cList: list, size: int):
        for c in cList:
            if isinstance(c, ft.Ref) and c.current:
                c.current.resize(size=size)


    def change_focus(self, e=None):
        if self.text_field.visible:
            self.text_field.set_focus()
            # asyncio.create_task(self.text_field.set_focus_without_selecton())

    
    def hintShowBtn_click(self, e):
        self.hint_show()
        # self.change_focus(e)

    
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
            self.level.user_progress[key]['total']+=total
            self.level.level_progress[key]['total']+=total
        if correct:
            self.level.user_progress[key]['correct']+=correct
            self.level.level_progress[key]['correct']+=correct


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
            else:
                self.text_field.clear_text()
                self.text_field.border_color=ft.Colors.GREEN_700


            async def background_task():
                await self.sound_player.end_task()
                await asyncio.sleep(1)
                self.hint_hide()
                self.page.update()
                await self.start_training()

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
        textAfter=self.centerRef.current.msgText
        colorAfter=self.centerRef.current.msgTextField.color
        if self.hint_type==0:
            message=text
        else:
            message=f'{text}\n{textAfter}'

        self.centerRef.current.msgText = message
        if color:
            self.centerRef.current.msgTextField.color = color
        self.page.update()

        # Очистить сообщение через указанное время
        async def clear_message():
            await asyncio.sleep(1)
            if self.centerRef.current.msgText == message:  # Только если не изменилось
                self.centerRef.current.msgText = textAfter
                self.centerRef.current.msgTextField.color = colorAfter
                self.page.update()
        
        asyncio.create_task(clear_message())


    def hint_show(self):
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

        self.centerRef.current.resetMsgText()

        if self.hint_type>1:
            self.keyboard.hint_hide()
        self.hint_type = 0
    

    def show_morse_code(self, morse_text: str = None):
        """Показать код Морзе для текста"""
        if morse_text is None:
            morse_text = self.current_morse_text
        self.centerRef.current.msgText = morse_text



    def set_level(self, e=None, level: int | None = None):
        """Загрузить уровень"""

        if e:
            if not self.showMode: return
            if e.control.key=='prevLevel':
                level = self.level.current_level-1
            elif e.control.key=='nextLevel':
                level = self.level.current_level+1
                if level>self.level.last_level: return
            
        if not level:
            level = self.level.current_level
        self.load_level(level)
        self.build_ui(update=True)
        self.set_training_type(TrainingType.LETTER)


    def set_training_type(self, type: TrainingType = TrainingType.LETTER):
        """Загрузить тип тренировки в уровне"""

        self.questions = lp.questionsGenerate(self.level.current_level, type)

        if self.questions:
            match type:
                case TrainingType.LETTER:
                    self.text_field.visible=False
                    self.mainTextFieldRef.current.value='1. Тренировка букв'
                case TrainingType.WORD:
                    self.text_field.visible=True
                    self.mainTextFieldRef.current.value='2. Тренировка слов'
                case TrainingType.PHRASE:
                    self.text_field.visible=True
                    self.mainTextFieldRef.current.value='3. Тренировка фраз'
                    self.keyboard.add_space(on_click=self.space_click)
                case _:
                    return
            
        self.training_type = type
        self.page.update()    


    async def start_training(self, e = None):
        """Начать тренировку"""
        # По нажатию на кнопку Начать уровень
        if e:
            if self.page.web and not self.sound_player.audio_activated:
                await self.sound_player.activate_audio()

            
            self.centerRef.current.showMsgText()
            self.mainTextFieldRef.current.visible=True
            self.content_area.disabled=False
            self.levelButtons.disabled=False
            self.showMode = False
            self.keyboard.hide_data(hintHide=True, progressHide=True)
            
            # self.page.update()

        match self.training_type:
            case TrainingType.LETTER:
                self.start_letter_training()
            case TrainingType.WORD:
                self.start_word_training()
            case TrainingType.PHRASE:
                self.start_phrase_training()


    def end_training(self):  
        # Сделать пересчет прогресса
        self.level.last_level_progress=self.level.level_progress
        # self.msgTextField.color = ft.Colors.GREEN_700
        self.centerRef.current.showButton(text='Следующий уровень')

        self.set_level(level=self.level.current_level+1)
        save_progress(self.level)


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
            if question in self.newLetters and (self.level.level_progress.get(question,0)==0 or self.level.level_progress[question]['correct']==0):
                self.centerRef.current.msgText = question
                self.page.update()
        else:
            self.change_focus()


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




    

    


 
