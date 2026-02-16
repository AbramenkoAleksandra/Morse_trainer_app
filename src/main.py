import flet as ft

from morse_trainer import MorseTrainer


def main(page: ft.Page):
    app = MorseTrainer(page)


ft.run(
    main,
    # view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=8550
)