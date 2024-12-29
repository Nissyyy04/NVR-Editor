from textual.app import App
from textual.widgets import Label


class TestPlugin():
    def __init__(self, app:App):
        self.app = app
        self.app.mount(Label("Hello from Test Plugin").set_styles("width: 100%; text-align: center;"))