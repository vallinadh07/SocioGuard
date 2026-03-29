import reflex as rx

class State(rx.State):
    message: str = ""
    result: str = ""

    def analyze(self):
        if "win" in self.message.lower():
            self.result = "⚠ Suspicious Message"
        else:
            self.result = "✅ Safe Message"


def index():
    return rx.vstack(
        rx.heading("SocioGuard", size="8"),
        rx.input(
            placeholder="Enter message...",
            on_change=State.set_message
        ),
        rx.button("Analyze", on_click=State.analyze),
        rx.text(State.result),
    )


app = rx.App()
app.add_page(index)