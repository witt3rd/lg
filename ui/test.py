"""User interface for the chat application."""

import flet as ft


def main(page: ft.Page) -> None:
    page.horizontal_alignment = "stretch"
    page.title = "Bionic Chat: User"

    page.add(
        ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment="start",
            controls=[
                ft.Row(
                    vertical_alignment="start",
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text("B"),
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text("Bob says:", weight="bold"),
                                ft.Text(
                                    "You are a `digital double` of the user.  You are an extension and reflection of the user. You should interact tersely with them to try to figure out how you can route their message: - User understanding: learn about the user, inform them of what you have learned about them, adapt to their styles and preferences. Call the router with `user` -Workflows: your main job is to offload tasks from the user.  You do this with workflows.  If the user is asking about creating, updating, performing, or the status of a task or workflow, then call the router with `workflow` Ask youself: is the user message about the user?  something the like, something they've done or want to do (aspirations), dreams, experiences, preferences, etc.?  If so, then route to user understanding ('user').Otherwise, if the user message is not about themselves (user understanding) or about tasks (workflows), then respond directing them to one of these topics.",
                                    selectable=True,
                                    width=800,
                                ),
                            ]  # type: ignore
                        ),
                    ],
                ),
                ft.Text("10:00 AM", color=ft.colors.AMBER),
            ],
        ),
    )
    page.update()


ft.app(port=2791, target=main, use_color_emoji=True, view=ft.WEB_BROWSER)
