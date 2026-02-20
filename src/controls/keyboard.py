import flet as ft

from text_converter import ConvertionType, TextConverter

class KeyboardButtonBasic(ft.TextButton):
    def __init__(self, text: str, key: str | None = None,
                 width: int | None = None, height: int | None = None,
                 expand: bool | int = False,
                 disabled: bool = False,
                 on_click = None,
                ):
        super().__init__()
        self.key = key or text
        self.data = text
        self.text = ft.Row([ft.Text(text, align=ft.Alignment.CENTER)], alignment=ft.MainAxisAlignment.CENTER)
        # self._strokeWidth = strokeWidth
        self.width = width or 50
        self.height = height or 50
        self._maxStrokeWidth = 6
        self.disabled = disabled
        self.expand = expand
        self.content = self.text
        self.style=ft.ButtonStyle(
            padding=ft.Padding.all(0),
            side=ft.BorderSide(
                width=min(self._maxStrokeWidth, self.height * 0.09),
                color=ft.Colors.SURFACE_CONTAINER_LOW if not self.disabled else ft.Colors.TRANSPARENT,
                stroke_align=ft.BorderSideStrokeAlign.INSIDE,
                style=ft.BorderStyle.SOLID
            ),
            text_style=ft.TextStyle(
                size=self.height * 0.3,
                weight=ft.FontWeight.W_500
            )
        )
        self.margin=ft.Margin.all(self.height * 0.1)
        self.on_click=on_click
        # print(self.style.text_style.size)


    @property
    def _textSize(self):
        return self.style.text_style.size
    
    @_textSize.setter
    def _textSize(self, value: int):
        self.style.text_style.size = value
        

    @property
    def _strokeWidth(self):
        return self.style.side.width
    
    @_strokeWidth.setter
    def _strokeWidth(self, value: int):
        self.style.side.width = min(self._maxStrokeWidth, value)

    
    def resize(self, size):
        self.width=size*self.width/self.height
        self.height=size
        self._strokeWidth = self.height * 0.09
        self.update()

    
    def update(self):
        self._textSize = self.height * 0.3
        self.margin=ft.Margin.all(self.height * 0.1)
        super().update()


class KeyboardButtonLetter(KeyboardButtonBasic):
    def __init__(self, text: str,
                 size: int | None = None,
                 hintText: str = '', hintVisible=False,
                 progressValue=0,
                 on_click = None,
                 disabled: bool = False,
                 ):
        super().__init__(text=text, on_click=on_click, disabled=disabled, width=size, height=size)

        self.hintVisible=hintVisible
        self.progress = ft.ProgressRing(
            value=progressValue, 
            stroke_width=self._strokeWidth,
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
                self.text,
                self.hint,
            ],
            expand=True,
            alignment=ft.Alignment(0,0),
            margin=0,
        )
    
    def update(self):
        self.progress.stroke_width=self._strokeWidth
        super().update()

        


class SpaceButton(KeyboardButtonBasic):
    def __init__(self, on_click, height=None):
        super().__init__(key='Space', text='Пробел', on_click=on_click, height=height)
        self.width = self.height * 6


keys = [
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'],
        ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ'],
        ['Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
        ['Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', '.'],
    ]


class Keyboard(ft.Column):
    def __init__(self, keys=keys, activeKeys: list | None = [],
                 on_click=None,
                 hintVisible=False, userProgress: dict | None = None,
                 maxWidth=None, maxHeight=None,
                 withSpace = False
                 ):
        super().__init__()
        self.keys = keys
        self._withSpace = withSpace
        self.spaceButton = None
        self.hintVisible=hintVisible
        self.maxWidth=maxWidth
        self.maxHeight=maxHeight
        self.activeKeysButtons: dict[str:KeyboardButtonLetter] = {}
        keyboard_rows = []
        for row in self.keys:
            row_buttons = []

            for key in row:
                progressValue=0
                if userProgress and userProgress.get(key):
                    if stats:=userProgress.get(key):
                        progressValue=stats.get('correct', 0) / stats.get('total', 1)

                isActive = activeKeys is None or key in activeKeys

                btn = KeyboardButtonLetter(
                    text=key,
                    on_click=on_click,
                    disabled=False if isActive else True,
                    hintText=TextConverter.convert(key,ConvertionType.SYMBOL_MORSE),
                    hintVisible=self.hintVisible,
                    progressValue=progressValue,
                    size=self.key_size,
                ) 
                if isActive:
                    self.activeKeysButtons[key]=btn

                row_buttons.append(btn)

            keyboard_rows.append(
                ft.Row(
                    row_buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=0,
                )
            )
      
        self.controls=keyboard_rows
        if self._withSpace:
            self.add_space()
        self.alignment=ft.MainAxisAlignment.END
        self.expand=True
        self.spacing = 0
        self.margin=ft.Margin.only(bottom=int(self.key_size*0.1))


    @property
    def key_size(self):
        if self.maxHeight is None or self.maxWidth is None or not keys: return 50
        addRows = 1 if self.spaceButton or self._withSpace else 0
        rowsCnt = len(self.keys) + addRows
        colsCnt = max(len(r) for r in self.keys)
        minSize = 20
        return int(max(minSize, min(self.maxWidth/colsCnt, self.maxHeight/rowsCnt))*0.8)
    

    def resize(self, maxWidth, maxHeight):
        self.maxWidth=maxWidth
        self.maxHeight=maxHeight
        size=self.key_size
        self.margin=ft.Margin.only(bottom=int(size*0.1))
        for r in self.controls:
            for btn in r.controls:
                if isinstance(btn, KeyboardButtonBasic):
                    btn.resize(size)



    def add_space(self, on_click=None):
        if self.spaceButton: return
        self.spaceButton=SpaceButton(on_click=on_click, height=self.key_size)
        self.controls.append(
            ft.Row(
                [self.spaceButton],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        # self.margin=ft.Margin.only(bottom=5)


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


    def change_key_progress(self, key: str, num: float):
        if btn:= self.activeKeysButtons.get(key):
            res = btn.progress.value
        res +=num
        if res > 1:
            res = 1
        if res < 0:
            res = 0
        btn.progress.value = res


    def hide_data(self, hintHide=False, progressHide=False):
        if not hintHide and not progressHide: return
        for btn in self.activeKeysButtons.values():
            if hintHide:
                btn.hint.visible = False
            if progressHide:
                btn.progress.value=0



        
if __name__ == "__main__":

    def main(page: ft.Page):
        def on_click(e):
            e.control.progress.value+=0.1
            e.control.update()


        keyboard = Keyboard(activeKeys=None, maxWidth=page.width, maxHeight=page.height/2, withSpace=False, hintVisible=True, on_click=on_click)
        page.add(keyboard)

        def page_resize(e):
            height = e.height if e else page.window.height
            width = e.width if e else page.window.width
            keyboard.resize(maxWidth=width, maxHeight=height/2)

        page.on_resize = page_resize

    ft.run(
        main,
        # view=ft.AppView.WEB_BROWSER, host='0.0.0.0', port=8550,
    )