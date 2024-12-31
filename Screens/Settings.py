from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import *
from textual.widget import Widget
import textual.containers as containers
import main
from textual.screen import Screen
import rich, re, os
from Config import config
from textual.widgets.selection_list import Selection
import ollama
from CustomWidgets import ReactiveLabel

class ScreenObject(Screen):
    """Text Editor Screen."""
    
    TITLE = f"Settings"
    SUB_TITLE = f"{os.getenv('username')}"

    contentsOfFile: str = None

    selectedProcessID = None

    def __init__(self, name = None, id = None, classes = None):
        super().__init__(name, id, classes)

    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_list.id == "themesList":
            config.set("theme", event.option.prompt)
            config.theme = event.option.prompt
            self.app.theme = event.option.prompt
            self.themeCollapsible.title = f"Themes - ({event.option.prompt})"
            self.refresh(repaint=True, layout=False, recompose=False)

        elif event.option_list.id == "textAreaThemesList":
            config.set("textAreaTheme", event.option.prompt)
            config.textAreaTheme = event.option.prompt
            self.textAreaThemeCollapsible.title = f"TextArea Theme - ({event.option.prompt})"
            self.refresh(repaint=True, layout=False, recompose=False)

        elif event.option_list.id == "ollamaList":
            config.set("ollamaModel", event.option.prompt)
            config.ollamaModel = event.option.prompt
            self.modelLabel.text = f"Local Models: {config.ollamaModel}"

    
    async def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        if event.radio_button.id == "pluginButton":
            if event.radio_button.value:
                event.radio_button.data.enable()
            else:
                event.radio_button.data.disable()
            event.radio_button.data.enabled = event.radio_button.data.is_enabled

        elif event.radio_button.id == "autoMergeButton":
            config.set("autoMerge", event.radio_button.value)
            config.autoMerge = event.radio_button.value


    def compose(self) -> ComposeResult:
        self.PL = main.PluginLoader(self.app, os.path.join(config.documentNever, "Plugins"))
        self.PL.load_plugins()

        self.themes = [
            "textual-dark", "textual-light", "nord", "gruvbox", "catppuccin-mocha",
            "dracula", "tokyo-night", "monokai", "flexoki", "catppuccin-latte",
            "solarized-light"
        ]

        self.themes.sort()

        with containers.VerticalScroll().set_styles("dock: top; width: 100%; height: 100%; padding: 1 0 1 0; content-align: center top;") as scroll:
            scroll.can_focus = False

            self.themeCollapsible = Collapsible(OptionList(*self.themes, id="themesList"), title=f"Themes - ({config.theme})")

            self.textAreaThemeCollapsible = Collapsible(OptionList(*TextArea().available_themes, id="textAreaThemesList"), title=f"TextArea Theme - ({config.textAreaTheme})")

            yield self.themeCollapsible
            yield self.textAreaThemeCollapsible

            with Collapsible(title="AI Assistant"):
                with containers.VerticalScroll() as aiScroll:
                    aiScroll.can_focus = False
                    aiScroll.add_class("accent")
                    aiScroll.set_styles("width: 100%; height: auto; padding: 1 1 1 1;")
                    yield RadioButton(
                        label="Auto AST Merge",
                        value=config.autoMerge,
                        id="autoMergeButton"
                    )

                    modelNames = []
                    for tup in ollama.list():
                        tup2 = tup[1]
                        for assistant in tup2:
                            modelNames.append(assistant.model)

                    with containers.Vertical() as cont:
                        cont.can_focus = False
                        cont.set_styles("width: auto; height: auto;")
                        self.modelLabel = ReactiveLabel(f"Local Models: {config.ollamaModel}").set_styles("width: auto; margin: 1 2 0 1;")
                        yield self.modelLabel
                        yield OptionList(*modelNames, id="ollamaList").set_styles("width: auto; padding: 0 2 0 2;")

            with Collapsible(title="Plugins"):
                with containers.VerticalScroll() as pluginsScroll:
                        pluginsScroll.can_focus = False
                        pluginsScroll.add_class("accent")
                        pluginsScroll.set_styles("width: 100%; height: auto; padding: 0 0 0 0;")
                        nvrDirectory = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
                        pluginsPath = os.path.join(nvrDirectory, "Plugins")  # Correct path joining

                        if os.path.exists(pluginsPath) and os.path.isdir(pluginsPath) and self.PL:
                            for plugin_name, plugin in self.PL.plugins.items():
                                plugin.load_config()
                                button = RadioButton(
                                    label=plugin_name,
                                    value=plugin.config["enabled"],
                                    id="pluginButton"
                                )
                                button.data = plugin
                                yield button
                        elif not self.PL:
                            yield Label("Plugin Loader had a error.")

                yield pluginsScroll


        yield Header(show_clock=True)
        yield Footer()

