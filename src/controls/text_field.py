import flet as ft


# Поле ввода

class TextFieldControl(ft.Row):
    def __init__(self, on_submit=None, regex_string=None, ref: ft.Ref | None = None):
        super().__init__(ref=ref)
        self.hintText="Введите текст..."
        self._textSize=16
        self.on_submit=on_submit
        self.regex_string=regex_string
        self.cursor_start=0
        self.cursor_end=0
        self.cursor_pos=0
        self._focused=False
        self._border_color=ft.Colors.GREEN_700


    def build(self):
        self.clearBtn = ft.IconButton(
                icon=ft.Icons.CLEAR,
                tooltip="Очистить",
                on_click=self.clear_text,
                # margin=ft.Margin.all(0),
                padding=ft.Padding.all(2),
                icon_size=15,
                width=20,
                height=20,
            )
        self.text_field = ft.TextField(
            hint_text=self.hintText,
            text_size=self._textSize,
            content_padding=ft.Padding.only(left=10, top=10, bottom=10, right=5),
            text_align=ft.TextAlign.LEFT,
            on_submit=self.on_submit, 
            suffix=self.clearBtn,
            dense=True, # Use a more compact layout
            margin=ft.Margin.all(0),
            input_filter=ft.InputFilter(regex_string=self.regex_string, allow=True, case_sensitive=False) if self.regex_string else None,
            capitalization=ft.TextCapitalization.CHARACTERS,
            autofocus=False,
            border_color=self.border_color,
            on_selection_change=self.on_selection_change,
            on_focus=self.on_focus,
            on_blur=self.on_blur,
        )

        self.text_field_confirm=ft.IconButton(
            ft.Icons.CHECK,
            on_click=self.on_submit,
            icon_size=20,
            padding=ft.Padding.all(5),
            width=35,
            height=35,
        )
        self.controls=[self.text_field, self.text_field_confirm]
        self.alignment=ft.MainAxisAlignment.CENTER
        self.margin=ft.Margin.only(bottom=15)


    def resize(self, size):
        size=max(30, size)
        s1=size*0.1
        s2=size*0.2
        s3=size*0.3
        s4=size*0.4
        s7=size*0.7
        self.text_field.width=size*5.5
        self.text_size = s3
        self.text_field.content_padding=ft.Padding.only(left=s2, top=s2, bottom=s2, right=s1)
        self.clearBtn.width=s4
        self.clearBtn.height=s4
        self.clearBtn.icon_size=size*0.25
        self.text_field_confirm.icon_size=s4
        self.text_field_confirm.width=s7
        self.text_field_confirm.height=s7
        self.text_field_confirm.padding=ft.Padding.all(s1)
        self.margin=ft.Margin.only(bottom=s3)
        if size<40:
            self.text_field.focused_border_width=1.5
        else:
            self.text_field.focused_border_width=2


    @property
    def focused(self):
        return self._focused


    @property
    def text_size(self):
        return self._textSize
    
    @text_size.setter
    def text_size(self, value: int):
        value=max(5,min(100, value))
        self._textSize=value
        self.text_field.text_size=value

    
    @property
    def border_color(self):
        return self._border_color

    @border_color.setter
    def border_color(self, color: ft.Colors):
        self._border_color=color
        self.text_field.border_color=color


    @property
    def value(self):
        return self.text_field.value

    @value.setter
    def value(self, text: str):
        self.text_field.value=text


    def add_value(self, text: str):
        """Добавить значение в текстовое поле"""
        if text=='': return

        current_text = self.value
        start=self.cursor_start
        end=self.cursor_end
        if start is not None and end is not None:
            # print(f'add_value: start={start},end={end}')

            text_added = current_text[:start] + text
            self.cursor_pos = len(text_added)

            self.value = text_added + current_text[end:]

            self.cursor_start=self.cursor_pos
            self.cursor_end=self.cursor_pos
        else:
            self.value += text


    def delete_value(self):
        "Backspace"
        if not self.value: return

        current_text = self.value
        start=self.cursor_start
        end=self.cursor_end
        if start is not None and end is not None:
            if start == end:
                text1 = current_text[:(start-1)]
            else:
                text1 = current_text[:(start)]

            self.cursor_pos = len(text1)

            self.value = text1 + current_text[end:]

            self.cursor_start=self.cursor_pos
            self.cursor_end=self.cursor_pos
        else:
            self.value = current_text[:-1]


    def clear_text(self):
        """Очистить текстовое поле"""
        self.value = ""
        self.update()


    def set_input_filter(self, regex_string):
        self.regex_string=regex_string
        self.text_field.input_filter = ft.InputFilter(regex_string=regex_string, allow=True, case_sensitive=False)


    def set_focus(self):
        self.page.run_task(self.text_field.focus)


    async def set_focus_without_selecton(self):
        start=self.cursor_start
        end=self.cursor_end
        await self.text_field.focus()
        # print(start, end, self.text_field.selection.start, self.text_field.selection.end)
        if self.value and self.text_field.selection.start != self.text_field.selection.end:
            self.text_field.selection = ft.TextSelection(base_offset=start,extent_offset=end)
            self.text_field.update()
            # print(self.cursor_start, self.cursor_end, self.text_field.selection.start, self.text_field.selection.end)

    
    def on_blur(self,e=None):
        # print(f'on_blur: start={self.text_field.selection.start},end={self.text_field.selection.end}')
        self.cursor_start=self.text_field.selection.start
        self.cursor_end=self.text_field.selection.end

        self._focused=False


    def on_focus(self, e=None):
        self._focused=True
    #     print(f'on_focus: start={self.text_field.selection.start},end={self.text_field.selection.end}')
    #     # self.text_field.selection = ft.TextSelection(base_offset=self.cursor_pos,extent_offset=self.cursor_pos)


    def on_selection_change(self, e=None):
        pass
        # print(f'on_change: start={self.text_field.selection.start},end={self.text_field.selection.end}')




if __name__ == "__main__":
    from controls.keyboard import Keyboard

    def main(page: ft.Page):
        async def set_focus(e):
            await txtField.set_focus_without_selecton()

        txtField=TextFieldControl(on_submit=set_focus)
        page.add(ft.Column([txtField],alignment=ft.MainAxisAlignment.END, expand=1))


        async def btn_click(e):
            txtField.add_value(e.control.key)
            await txtField.set_focus_without_selecton()

        keyboard = Keyboard(activeKeys=None, maxWidth=page.width, maxHeight=page.height/2, on_click=btn_click)
        txtField.resize(keyboard.key_size)


        page.add(keyboard)

        def page_resize(e):
            height = e.height if e else page.height
            width = e.width if e else page.width
            keyboard.resize(maxWidth=width, maxHeight=height/2)
            txtField.resize(keyboard.key_size)

        page.on_resize = page_resize

    ft.run(main)
    