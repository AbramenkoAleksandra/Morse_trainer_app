import flet as ft


# Поле ввода

class TextFieldControl(ft.Row):
    def __init__(self, on_submit=None, regex_string=None):
        super().__init__()
        self.hintText="Введите текст..."
        self.textSize=16
        self.on_submit=on_submit
        self.regex_string=regex_string
        self.cursor_start=0
        self.cursor_end=0
        self.cursor_pos=0
        self.border_color=ft.Colors.GREEN_700


    def build(self):
        self.text_field = ft.TextField(
            hint_text=self.hintText,
            text_size=self.textSize,
            content_padding=ft.Padding.only(left=10, top=10, bottom=10, right=5),
            text_align=ft.TextAlign.LEFT,
            on_submit=self.on_submit, 
            suffix=ft.IconButton(
                icon=ft.Icons.CLEAR,
                tooltip="Очистить",
                on_click=self.clear_text,
                # margin=ft.Margin.all(0),
                padding=ft.Padding.all(2),
                icon_size=15,
                size_constraints=ft.BoxConstraints(max_height=20, max_width=20)
            ),
            dense=True, # Use a more compact layout
            margin=ft.Margin.all(0),
            input_filter=ft.InputFilter(regex_string=self.regex_string, allow=True, case_sensitive=False) if self.regex_string else None,
            capitalization=ft.TextCapitalization.CHARACTERS,
            autofocus=True,
            border_color=self.border_color,
            on_selection_change=self.on_selection_change,
            # on_focus=self.on_focus,
            on_blur=self.on_blur,
        )

        text_field_confirm=ft.IconButton(
            ft.Icons.CHECK,
            on_click=self.on_submit,
            icon_size=20,
            padding=ft.Padding.all(5),
            size_constraints=ft.BoxConstraints(max_height=35, max_width=35),
        )
        self.controls=[self.text_field, text_field_confirm]
        self.alignment=ft.MainAxisAlignment.CENTER
        self.margin=ft.Margin.only(bottom=15)


    def set_input_filter(self, regex_string):
        self.regex_string=regex_string
        self.text_field.input_filter = ft.InputFilter(regex_string=regex_string, allow=True, case_sensitive=False)


    def set_border_color(self, color: ft.Colors):
        self.text_field.border_color=color


    def clear_text(self, e=None):
        """Очистить текстовое поле"""
        self.text_field.value = ""
        self.update()

    
    def on_blur(self,e=None):
        # print(f'on_blur: start={self.text_field.selection.start},end={self.text_field.selection.end}')
        self.cursor_start=self.text_field.selection.start
        self.cursor_end=self.text_field.selection.end


    # def on_focus(self, e=None):
    #     print(f'on_focus: start={self.text_field.selection.start},end={self.text_field.selection.end}')
    #     # self.text_field.selection = ft.TextSelection(base_offset=self.cursor_pos,extent_offset=self.cursor_pos)



    def on_selection_change(self, e=None):
        pass
        # print(f'on_change: start={self.text_field.selection.start},end={self.text_field.selection.end}')


    def get_value(self):
        return self.text_field.value


    def add_value(self, text: str):
        """Добавить значение в текстовое поле"""
        current_text = self.text_field.value
        start=self.cursor_start
        end=self.cursor_end
        if start is not None and end is not None:
            # print(f'add_value: start={start},end={end}')

            text_added = current_text[:start] + text
            self.cursor_pos = len(text_added)

            self.text_field.value = text_added + current_text[end:]

            self.cursor_start=self.cursor_pos
            self.cursor_end=self.cursor_pos
        else:
            self.text_field.value += text



if __name__ == "__main__":
    from controls.keyboard import Keyboard

    def main(page: ft.Page):
        txtField=TextFieldControl()
        page.add(txtField)

        def btn_click(e):
            txtField.add_value(e.control.key)

        page.add(Keyboard(
            activeKeys=['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж', 'Э'],
            on_click=btn_click))

    ft.run(main)
    