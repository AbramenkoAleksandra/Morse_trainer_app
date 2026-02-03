import flet as ft

from morse_text import MorseText

class KeyboardButton(ft.TextButton):
    def __init__(self, text, hintText='', hintVisible=False, on_click=None, disabled=True, progressValue=0, strokeWidth=4):
        super().__init__()
        self.disabled=disabled
        self.key=text
        self.data=text
        self.strokeWidth=strokeWidth
        self.hintVisible=hintVisible
        self.progress = ft.ProgressRing(
            value=progressValue, 
            stroke_width=self.strokeWidth,
            color=ft.Colors.INVERSE_PRIMARY,
            expand=True,
            padding=ft.Padding.all(0),
            margin=0,
            stroke_cap=ft.StrokeCap.ROUND,
            visible=not self.disabled,
            stroke_align=-1,
        )
        self.hint = ft.Row(
            [ft.Text(
                value=hintText,
                align=ft.Alignment.BOTTOM_CENTER,
                style=ft.TextStyle(weight=ft.FontWeight.W_400),
            )],
            alignment=ft.MainAxisAlignment.CENTER,
            margin=4,
            visible=not self.disabled and self.hintVisible,
        )
        self.content = ft.Stack(
            fit=ft.StackFit.EXPAND,
            controls=[
                self.progress,
                ft.Row(
                    [ft.Text(text, expand=True, align=ft.Alignment.CENTER)],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                self.hint,
            ],
            expand=True,
            alignment=ft.Alignment(0,0),
            margin=0,
        )
        self.style=ft.ButtonStyle(
            padding=ft.Padding.all(0),
            side=ft.BorderSide(
                width=self.strokeWidth,
                color=ft.Colors.SURFACE_CONTAINER_LOW if not self.disabled else ft.Colors.TRANSPARENT,
            )
        )
        self.margin=ft.Margin.only(left=1, right=1)
        self.on_click=on_click
        self.width=50
        self.height=50


keys = [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ'],
        ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
        ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '.'],
    ]

class Keyboard(ft.Column):
    def __init__(self, keys=keys, activeKeys=[], on_click=None, hintVisible=False, userProgress=None):
        super().__init__()
        self.keys = keys
        self.spaceButton = None
        self.keyboard_rows = []
        self.hintVisible=hintVisible
        self.activeKeysButtons: dict[str:KeyboardButton] = {}
        for row in self.keys:
            self.row_buttons = []

            for key in row:
                progressValue=0
                if userProgress and userProgress.get(key):
                    if stats:=userProgress.get(key):
                        progressValue=stats.get('correct', 0) / stats.get('total', 1)

                btn = KeyboardButton(
                    text=key,
                    on_click=on_click,
                    disabled=False if key in activeKeys else True,
                    hintText=MorseText.symbolToCode.get(key.lower()),
                    hintVisible=self.hintVisible,
                    progressValue=progressValue,
                ) 
                if key in activeKeys:
                    self.activeKeysButtons[key]=btn

                self.row_buttons.append(btn)

            self.keyboard_rows.append(
                ft.Row(
                    self.row_buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            )
                
        self.controls=self.keyboard_rows
        self.alignment=ft.MainAxisAlignment.END
        self.expand=True
        self.margin=ft.Margin.only(bottom=20, top=0)


    def add_space(self, on_click=None):
        if self.spaceButton: return
        self.spaceButton=ft.TextButton(
            key='Space',
            content='ПРОБЕЛ',
            style=ft.ButtonStyle(
                padding=ft.Padding.all(0),
                side=ft.BorderSide(
                    width=4,            # !!! Сделать переменную
                    color=ft.Colors.SURFACE_CONTAINER_LOW if not self.disabled else ft.Colors.TRANSPARENT,
                )
            ),
            height=50,
            width=300,
            on_click=on_click
        )
        self.controls.append(
            ft.Row(
                self.spaceButton,
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        self.margin=ft.Margin.only(bottom=5)



    def hint_show(self):
        for btn in self.activeKeysButtons.values():
            btn.hint.visible = True


    def hint_hide(self):
        self.hide_data(hintHide=True)


    def progress_show(self, userProgress: dict):
        if not userProgress: return
        for btn in self.activeKeysButtons.values():
            # stats = self.user_progress.get(btn.key)
            if stats:= userProgress.get(btn.key):
                btn.progress.value=stats.get('correct', 0) / stats.get('total', 1)


    def hide_data(self, hintHide=False, progressHide=False):
        if not hintHide and not progressHide: return
        for btn in self.activeKeysButtons.values():
            if hintHide:
                btn.hint.visible = False
            if progressHide:
                btn.progress.value=0



        
