"""User interface for the chat application."""

import flet as ft
from pyee import EventEmitter

#
ee = EventEmitter()
BOT_NAME = "Bionic"

#


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class ChatMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "start"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Text(message.user_name, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name: str) -> str:
        if user_name:
            return user_name[:1].capitalize()
        return "Unknown"  # or any default value you prefer

    def get_avatar_color(self, user_name: str) -> str:
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


def main(page: ft.Page) -> None:
    page.horizontal_alignment = "stretch"
    page.title = "Bionic Chat: User"

    def bot_thread() -> None:
        from lg.bot import Bot

        @ee.on("user_message")
        def on_user_message(message: Message) -> None:
            bot = Bot(page.session.get("user_name"))
            response = bot.user_says(message.text)
            on_message(
                Message(
                    BOT_NAME,
                    response,
                    message_type="chat_message",
                )
            )

    def on_message(message: Message) -> None:
        print(f"Message: {message}")
        if message.message_type == "chat_message":
            m = ChatMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, size=12)
        chat.controls.append(m)
        page.update()
        if message.user_name != BOT_NAME:
            ee.emit("user_message", message)

    def join_chat_click(e) -> None:
        if not join_user_name.value:
            join_user_name.error_text = "Name cannot be blank!"
            join_user_name.update()
        else:
            page.session.set("user_name", join_user_name.value)
            page.dialog.open = False
            new_message.prefix = ft.Text(f"{join_user_name.value}: ")
            on_message(
                Message(
                    user_name=join_user_name.value,
                    text=f"{join_user_name.value} has joined the chat.",
                    message_type="login_message",
                )
            )
            page.run_thread(bot_thread)

    def send_message_click(e) -> None:
        if new_message.value != "":
            message_text = new_message.value
            new_message.value = ""
            new_message.focus()
            on_message(
                Message(
                    page.session.get("user_name"),
                    message_text,
                    message_type="chat_message",
                )
            )

    # A dialog asking for a user display name
    join_user_name = ft.TextField(
        label="Enter your name to join the chat",
        autofocus=True,
        on_submit=join_chat_click,
    )
    page.dialog = ft.AlertDialog(
        open=True,
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([join_user_name], width=300, height=70, tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_chat_click)],
        actions_alignment="end",
    )

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
    )

    # Add everything to the page
    page.add(
        ft.Container(
            content=chat,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [
                new_message,
                ft.IconButton(
                    icon=ft.icons.SEND_ROUNDED,
                    tooltip="Send message",
                    on_click=send_message_click,
                ),
            ]
        ),
    )


ft.app(port=2791, target=main, use_color_emoji=True, view=ft.WEB_BROWSER)
