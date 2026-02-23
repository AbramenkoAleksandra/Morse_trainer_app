import flet as ft


class MainTextField(ft.Text):
    """Текстовое поле вверху страницы"""

    def __init__(self, value: str, size = None, visible: bool = False, ref: ft.Ref | None = None):
        super().__init__(
            value=value,
            size=18,
            weight=ft.FontWeight.W_400,
            text_align=ft.TextAlign.CENTER,
            visible=visible,
            ref=ref
        )
        if size:
            self.resize(size=size)
    
    def resize(self, size):
        self.size = size * 0.35


class LevelGoButton(ft.IconButton):
    """Кнопки слева со стрелками - перейти на предыдущий или на следующие уровень"""
    def __init__(self, icon: ft.Icon, key: str,
                 on_click=None, ref: ft.Ref | None = None,
                 disabled=False):
        super().__init__(
            icon=icon,
            key=key,
            padding=ft.Padding.all(2),
            margin=ft.Margin.all(0),
            icon_size=20,
            alignment=ft.Alignment.CENTER,
            on_click=on_click,
            ref=ref,
            disabled=disabled
        )

    def resize(self, size):
        size=max(size, 40)
        self.icon_size=size * 0.4
        self.width=size*0.6
        self.height=size*0.6
        


class LevelSwitcher(ft.Row):
    """Контейнер с информацией об уровне и кнопками переключения на соседние уровни"""
    def __init__(self, currentLevel: int, newLetters: list,
                 on_click=None,
                 prevLevelRef: ft.Ref | None = None,
                 nextLevelRef: ft.Ref | None = None,
                 ref: ft.Ref | None = None,
                 size: int | None = None,
                 ):
        super().__init__(ref=ref)
        self.textValue = f'Уровень {currentLevel}:\n{', '.join(newLetters)}'
        self.on_click=on_click

        self.levelInfo = ft.Text(
            value=self.textValue,
            size=size * 0.3 if size else 14,
            weight=ft.FontWeight.W_600,
            text_align=ft.TextAlign.CENTER,
            expand=1,
            margin=ft.Margin.all(0),
        )

        self.prevLevelGo = LevelGoButton(
            icon=ft.Icons.ARROW_LEFT,
            key='prevLevel',
            on_click=self.on_click,
            ref=prevLevelRef,
        )

        self.nextLevelGo = LevelGoButton(
            icon=ft.Icons.ARROW_RIGHT,
            key='nextLevel',
            on_click=self.on_click,
            ref=nextLevelRef,
        )

        self.controls=ft.Row(controls=[
                self.prevLevelGo,
                self.levelInfo,
                self.nextLevelGo,
            ],
            spacing=5,
            expand=False,
            alignment=ft.MainAxisAlignment.START,
        )

        self.alignment=ft.MainAxisAlignment.START
        self.expand=1

    
    def set_level_info(self, currentLevel: int, newLetters: list):
        self.textValue = f'Уровень {currentLevel}:\n{', '.join(newLetters)}'
        self.levelInfo.value = self.textValue

        
    def resize(self, size):
        self.levelInfo.size = size * 0.3
        self.prevLevelGo.resize(size)
        self.nextLevelGo.resize(size)
        
        

class StartLevelButton(ft.FilledButton):
    """Кнопка в центре - начать уровень"""

    def __init__(self, content: str, on_click=None, size = None):
        super().__init__(
            content=content,
            on_click=on_click,
        )
        self.style=ft.ButtonStyle(
            padding=ft.Padding.all(20),
            text_style=ft.TextStyle(
                size=19,
                weight=ft.FontWeight.BOLD
            ),
        )
        if size:
            self.resize(size)

    def resize(self, size):
        self.style.text_style.size=size*0.4
        self.style.padding=ft.Padding.all(size*0.4)


class CenterContainer(ft.Row):
    """Контейнер в центре - показывает либо кнопку Начать уровень либо текст уровеня (подсказки, сообщения)"""

    def __init__(self, btnText: str, msgText: str = '?', size=None, ref: ft.Ref | None = None, on_click=None):
        super().__init__(ref=ref)
        self._msgText = msgText
        self.msgTextField = ft.Text(value=msgText, size=24, weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER, expand=1)

        self.startLevelButton=StartLevelButton(
            content=btnText,
            on_click=on_click,
        )

        self.controls=self.startLevelButton

        self.expand=2
        self.alignment=ft.MainAxisAlignment.CENTER

        if size:
            self.resize(size)


    @property
    def msgText(self):
        return self._msgText
    
    @msgText.setter
    def msgText(self, value: str):
        self._msgText = value
        self.msgTextField.value = value


    def resetMsgText(self):
        self.msgText='?'
        self.msgTextField.color=None
        self.update()


    def showMsgText(self):
        self.controls=self.msgTextField
        

    def showButton(self, text: str | None = None):
        if text:
            self.startLevelButton.content = text
        self.controls=self.startLevelButton


    def resize(self, size):
        self.startLevelButton.resize(size)
        self.msgTextField.size=size*0.5



class LevelIconButton(ft.FilledIconButton):
    """Кнопки справа - показать подсказку, проиграть звук"""

    def __init__(self, icon: ft.Icon, on_click = None, tooltip: str = '', size: int | None = None, ref: ft.Ref | None = None):
        super().__init__(
            icon = icon,
            on_click=on_click,
            tooltip=tooltip,
            ref=ref,
            margin=ft.Margin.all(0),
        )

        if size:
            self.resize(size)

    def resize(self, size):
        self.width=size
        self.height=size
        self.icon_size = size*0.5
        self.padding=ft.Padding.all(size*0.2)


        