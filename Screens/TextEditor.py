from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import *
from Utilities import NVRTextArea, remove_code_snippets, WorkspaceClass, populate_tree
import textual.containers as containers
from textual.containers import Container
from textual.screen import Screen
from Screens import Settings
from PluginUtilities import PluginLoader, Plugin
import os
from Config import config
from textual.widgets.tree import TreeNode
import assistant, intellimerge
from textual import work
from asyncio import to_thread
import asyncio
from datetime import datetime, timedelta
from textual.events import DescendantFocus

class ProjectSettingsScreen(Screen):
    TITLE = "Project Settings"

    PL: PluginLoader = None

    def __init__(self, name = None, id = None, classes = None, filepath:str = None):
        self.SUB_TITLE = f"Project: {os.path.basename(filepath)}"
        self.filepath = filepath.removeprefix("📄 ")
        super().__init__(name, id, classes)

    def _on_mount(self, event):
        return super()._on_mount(event)

    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        if event.radio_button.id == "pluginButton":
            if event.radio_button.data:
                data: Plugin = event.radio_button.data
                if event.radio_button.value:
                    data.enable(self.filepath)
                else:
                    data.disable(self.filepath)
            self.notify(f"Please refresh the Code Editor to reload the plugins.")

    def compose(self) -> ComposeResult:
        self.PL = PluginLoader(self.app, os.path.join(config.documentNever, "Plugins"))
        self.PL.load_plugins()
                    
        with containers.ScrollableContainer() as container:
            container.can_focus = False
            with Collapsible(title="Plugins", id="pluginsList") as pluginsContainer:
                pluginsContainer.set_styles("width: 100%; height: auto;")
                pluginsContainer.can_focus = False
                with containers.VerticalScroll() as pluginsScroll:
                    pluginsScroll.can_focus = False
                    pluginsScroll.add_class("accent")
                    pluginsScroll.set_styles("width: 100%; height: auto; padding: 0 0 0 0;")
                    pluginsPath = os.path.join(config.documentNever, "Plugins")  # Correct path joining

                    if os.path.exists(pluginsPath) and os.path.isdir(pluginsPath) and self.PL:
                        for plugin_name, plugin in self.PL.plugins.items():
                            button = RadioButton(
                                label=plugin_name,
                                value=not self.filepath in plugin.config["projectPreferences"].keys(),
                                id="pluginButton",
                            )
                            button.data = plugin
                            yield button
                    elif not self.PL:
                        yield Label("Plugin Loader had a error.")

                yield pluginsScroll

        yield Header(show_clock=True)
        yield Footer()

class MergerScreen(Screen):
    TITLE = "Choose which snippets to apply?"

    closedSnippets = 0

    def __init__(self, name = None, id = None, classes = None, snippets: list = None, mainTextArea: TextArea = None, this: Screen = None):
        if snippets:
            self.snippets = snippets
        if mainTextArea:
            self.mainTextArea = mainTextArea
        if this:
            self.this = this
        super().__init__(name, id, classes)

    def action_back(self):
        self.app.pop_screen()

    def _on_mount(self, event):
        self.app.notify("Press ESC to go back to coding!")
        return super()._on_mount(event)

    def compose(self) -> ComposeResult:
        i = 0
        for snippet in self.snippets:
            with containers.VerticalScroll() as cont3:
                yield Label(f"Snippet {i+1}").set_styles("width: 100%; height: 1; text-align: center;")
                cont3.styles.align = ("center", "middle")

                with containers.Horizontal() as cont:
                    textArea = NVRTextArea.code_editor(snippet['code'], language="python", theme=config.textAreaTheme)
                    yield textArea

                    acceptButton = Button("Accept", id=f"acceptButton", variant="primary")
                    acceptButton.textarea = textArea
                    acceptButton.container = cont3

                    denyButton = Button("Deny", id="declineButton", variant="warning")
                    denyButton.container = cont3

                    with containers.Vertical() as cont2:
                        cont2.styles.width = "auto"
                        cont2.styles.height = "auto"
                        cont2.styles.align = ("center", "middle")
                        yield acceptButton
                        yield denyButton
            i+=1

        yield Header(show_clock=True)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "acceptButton":
            self.mainTextArea.text = intellimerge.merge(self.mainTextArea.text, event.button.textarea.text)
            self.this.aiCodeHistory.append(self.mainTextArea.text)
            event.button.container.remove_children()
            event.button.container.remove()
        elif event.button.id == "declineButton":
            event.button.container.remove_children()
            event.button.container.remove()
        
        self.closedSnippets += 1
        if self.closedSnippets == len(self.snippets):
            self.app.pop_screen()

        self.refresh(repaint=True)

class ScreenObject(Screen):
    """Text Editor Screen."""
    
    TITLE = ""
    SUB_TITLE = ""

    textArea: TextArea
    optionList: OptionList
    collapsibleOPTL: Collapsible
    fileTree = Tree

    contentsOfFile: str = None

    selectedProcessID = None
    filePath = None
    mainDirectory = None

    aiCodeHistory = []
    thisFilePath = os.path.realpath(__file__)

    never = assistant.ArtificialIntelligence(model=config.ollamaModel, promptPath=os.path.join(thisFilePath, os.path.join(config.documentNever, ".prompts", "neverPrompt.txt")))

    currentReverts = 0
    lastExpandedNodeTime = datetime.now()

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", "Save contents of the TextArea to said file", priority=True, tooltip="Save contents of TextArea to said file"),
        Binding("ctrl+t", "focus_tree", "Focus on the File Tree", "Focus on the File Tree", priority=True, tooltip="Focus on the File Tree"),
        Binding("ctrl+b", "undo_ai", "Undo AI Changes", "Undo AI Changes", priority=False, tooltip="Undo AI Changes."),
        Binding("ctrl+shift+b", "redo_ai", "Redo AI Changes", "Redo AI Changes", priority=False, tooltip="Redo AI Changes."),
    ]

    def action_focus_tree(self):
        self.fileTree.focus()

    def action_undo_ai(self):
        self.textArea.text = self.aiCodeHistory[self.currentReverts]
        if self.currentReverts > 0:
            self.currentReverts -= 1

    def action_redo_ai(self):
        self.textArea.load_text(self.aiCodeHistory[self.currentReverts])
        if self.currentReverts < len(self.aiCodeHistory)-1:
            self.currentReverts += 1

    def action_save(self):
        try:
            open(self.filePath.strip(), 'wb').write(self.textArea.text.encode('utf-8'))
            self.contentsOfFile = self.textArea.text
            self.sub_title = str(len(self.contentsOfFile.splitlines())+1) + " Lines"
            self.title = os.path.basename(self.filePath)
            if self.filePath not in self.workspace.config['updatedFiles']:
                self.workspace.config['updatedFiles'].append(self.filePath)
                fileNode = self.workspaceTree.root.add(os.path.basename(self.filePath))
                fileNode.data = self.filePath
                self.workspace.save()

        except Exception as e:
            self.app.clear_notifications()
            self.notify(f"ERROR! {e.__class__.__name__}: {e.args[0]}", severity="error")
    
    def __init__(self, name=None, id=None, classes=None, filepath: str = None):
        self.filePath = filepath
        self.mainDirectory = os.path.dirname(filepath)
        self.contentsOfFile = open(filepath.strip(), 'rb').read().decode('utf-8')
        self.TITLE = os.path.basename(filepath)
        self.SUB_TITLE = str(len(self.contentsOfFile.splitlines()) + 1) + " Lines"

        self.workspace = WorkspaceClass(".workspace.json")

        self.aiCodeHistory = [self.contentsOfFile]

        super().__init__(name, id, classes)

    def check_for_updates(self):
        if self.contentsOfFile != open(self.filePath.strip(), 'rb').read().decode('utf-8'):
            if self.contentsOfFile == self.textArea.text:
                self.contentsOfFile = open(self.filePath.strip(), 'rb').read().decode('utf-8')
                curs = self.textArea.cursor_location
                self.textArea.text = self.contentsOfFile
                self.textArea.move_cursor(curs)
                self.notify("File was modified outside of NEVER Editor!", severity="warning")
            else:
                self.contentsOfFile = open(self.filePath.strip(), 'rb').read().decode('utf-8')
                self.notify("File was modified outside of NEVER Editor!", severity="warning")

    def _on_mount(self, event):
        self.set_interval(1, self.check_for_updates)
        return super()._on_mount(event)

    def compose(self) -> ComposeResult:
        self.PL = PluginLoader(self.app, "Plugins")
        self.PL.load_plugins(project_path=self.mainDirectory)

        with containers.ScrollableContainer() as container:
            container.styles.dock = "left"
            container.styles.width = "20%"
            container.styles.height = "100%"
            container.set_styles("padding: 1 0 1 0;")
            container.can_focus = False


            with Container().set_styles(f"width: 100%; padding: 0 0 1 0;") as innerCont2:
                self.fileTree = Tree(f"{self.mainDirectory}")
                self.fileTree.root.expand()
                populate_tree(self.fileTree.root, self.mainDirectory)

                self.workspaceTree = Tree(f"Workspace Files")
                self.workspaceTree.root.expand()

                for file in self.workspace.config['updatedFiles']:
                    fileNode = self.workspaceTree.root.add(os.path.basename(file))
                    fileNode.data = file

                self.workspaceTree.ICON_NODE = "❌ "
                self.workspaceTree.ICON_NODE_EXPANDED = "❌ "

                self.fileTree.ICON_NODE = "📁 "
                self.fileTree.ICON_NODE_EXPANDED = "📂 "
                
                yield Label("Workarea").set_styles("text-align: center; width: 100%;")

                # Start from the current directory
                with containers.Horizontal() as cont:
                    cont.set_styles("width: 100%; height: 1; align: center middle; padding: 0 1 0 1;")
                    self.newFileButton = Button("New File", id="newFileButton", variant="primary")
                    self.newFileButton.set_styles("height: 1; width: auto; min-height: 1; border: none;")
                    self.deleteFileButton = Button("Delete File", id="deleteFileButton", variant="warning")
                    self.deleteFileButton.set_styles("height: 1; width: auto; min-height: 1; border: none;")
                    
                    yield self.newFileButton
                    yield self.deleteFileButton

                yield self.fileTree
                yield self.workspaceTree

            with containers.Center() as innerCont1:
                innerCont1.styles.dock = "bottom"
                innerCont1.styles.width = "100%"
                innerCont1.styles.align = ("center", "middle")
                innerCont1.styles.content_align = ("center", "middle")
                innerCont1.styles.padding = (1, 0, 0, 0)
                innerCont1.can_focus = False
                innerCont1.add_class("accent")

                yield Button("Project Settings", id="projectSettings").set_styles("width: 90%;")
                yield Button("Settings", id="settingsButton", variant="primary").set_styles("width: 90%; margin: 0 0 1 0;")

        with containers.VerticalScroll() as container:
            container.can_focus = False
            self.textArea = NVRTextArea.code_editor(text=self.contentsOfFile, language="python", theme=config.textAreaTheme)
            yield self.textArea

            if config.ollamaModel is not None:
                with Collapsible(title=f"NEVER Coder: {config.ollamaModel}") as collapsible:
                    collapsible.styles.max_height = "50%"
                    self.aiChatCollapsible = collapsible
                    with containers.Vertical() as cont:
                        cont.can_focus = False
                        cont.styles.margin = (0, 4, 0, 0)
                        self.aiChat = NVRTextArea.code_editor("", language="python", theme=config.textAreaTheme, read_only=True)
                        yield self.aiChat
                        yield Input(placeholder="Type here...").set_styles("dock: bottom; margin: 0 0 1 0;")

        yield Header(show_clock=True)
        yield Footer()


    async def on_descendant_focus(self, event: DescendantFocus):
        inp = None
        inp2 = None

        try:
            inp = self.query_one("#newFileInput", Input)
        except Exception as e: pass
        try:
            inp2 = self.query_one("#deleteFileInput", Input)
        except Exception as e: pass

        if inp or inp2:
            if inp:
                if inp is not event.control:
                    inp.remove()
            
            if inp2:
                if inp2 is not event.control:
                    inp2.remove()

    async def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "newFileInput" and event.value != "":
            open(os.path.join(self.mainDirectory, event.value), "w").write("")
            event.input.remove()
            self.fileTree.clear()
            populate_tree(self.fileTree.root, self.mainDirectory)

        elif event.input.id == "deleteFileInput" and event.value != "":
            try:
                os.remove(os.path.join(self.mainDirectory, event.value))
                event.input.remove()
                self.fileTree.clear()
                populate_tree(self.fileTree.root, self.mainDirectory)
            except Exception as e: pass

        else:
            try:
                self.aiCodeHistory.append(self.textArea.text)
                self.auto_generate(event)
            except Exception as e: pass

    @work(exclusive=True, thread=False)
    async def auto_generate(self, event: Input.Submitted):
        while True:
            self.notify("Please wait a moment.")
            self.aiChat.set_loading(True)
            try:
                compile(self.textArea.text, '<string>', 'exec')
            except Exception as e:
                self.aiChat.load_text(self.aiChat.text + "NEVER: " + str(e) + "\n")
                self.aiChat.set_loading(False)
                break
            try:
                fullyMergedCode, response, snippets = await to_thread(
                    self.never.generate, self.textArea.text, event.value
                )
                cleanResponse = "NEVER: " + remove_code_snippets(response.message.content)
                if cleanResponse.strip() == "NEVER:":
                    cleanResponse = "NEVER: Didn't respond with an explanation."
                self.aiChat.load_text(self.aiChat.text + cleanResponse + "\n")
                event.input.value = ""
                self.aiChat.set_loading(False)
                if not config.autoMerge and snippets is not None and len(snippets) > 0:
                    self.app.push_screen(MergerScreen(snippets=snippets, mainTextArea=self.textArea, this=self))
                else:
                    self.textArea.text = fullyMergedCode
                    self.aiCodeHistory.append(fullyMergedCode)
                break
            except asyncio.CancelledError:
                self.aiChat.load_text(self.aiChat.text + "NEVER: Cancelled Generation!" + "\n")
                self.aiChat.set_loading(False)
                break

    async def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        selected_language = event.option.prompt
        syntax_name = selected_language.lower()

        # Validate the language
        supported_languages = ["python", "javascript", "html", "css", "c++", "java"]
        if syntax_name not in supported_languages:
            self.notify(f"Language '{syntax_name}' is not supported!", severity="warning")
            return

        # Update the TextArea language and refresh it
        self.textArea.language = syntax_name
        self.textArea.refresh()

        self.collapsibleOPTL.title = f"Languages - ({syntax_name})"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settingsButton":
            self.app.push_screen(Settings.ScreenObject())
        elif event.button.id == "projectSettings":
            self.app.push_screen(ProjectSettingsScreen(filepath=self.mainDirectory))

        elif event.button.id == "newFileButton":
            inp = Input(placeholder="File Name (e.g. newFile.py): ", id="newFileInput").set_styles("width: 100%;")
            inp.focus()
            self.screen.mount(inp, after=self.newFileButton.parent)
        elif event.button.id == "deleteFileButton":
            inp = Input(placeholder="File Name (e.g. fileToDelete.py): ", id="deleteFileInput").set_styles("width: 100%;")
            inp.focus()
            self.screen.mount(inp, after=self.newFileButton.parent)

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Handle lazy loading of folder contents when expanded."""
        now = datetime.now()

        if event.control is self.fileTree:
            node = event.node
            if node.data and not node.children:
                populate_tree(node, node.data)
            event.stop()  # Prevent propagation for fileTree events

        elif event.control is self.workspaceTree:
            if event.node.data and getattr(self, 'lastExpandedNodeTime', datetime.min) + timedelta(milliseconds=500) <= now:
                node = event.node
                if node.data in self.workspace.config.get('updatedFiles', []):
                    self.workspace.config['updatedFiles'].remove(node.data)
                    self.workspace.save()
                self.refresh(repaint=True, recompose=True)  # Only repaint, not full recompose
                event.stop()  # Prevent propagation for workspaceTree events

        # Update last expanded node time
        self.lastExpandedNodeTime = now

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle file or folder selection."""
        node = event.node

        if node.data:
            item_type = "File" if os.path.isfile(node.data) else "Folder"

            if item_type == "File":
                self.filePath = node.data
                self.contentsOfFile = open(self.filePath.strip(), 'rb').read().decode('utf-8')
                self.textArea.text = self.contentsOfFile
                self.title = os.path.basename(self.filePath)
                self.sub_title = str(len(self.contentsOfFile.splitlines())+1) + " Lines"

                self.aiCodeHistory = [self.contentsOfFile]

                self.refresh(repaint=True, recompose=True)
    
    async def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if config.autoSave:
            try:
                open(self.filePath.strip(), 'wb').write(self.textArea.text.encode('utf-8'))
                self.contentsOfFile = self.textArea.text
                self.sub_title = str(len(self.contentsOfFile.splitlines())+1) + " Lines"
                self.title = os.path.basename(self.filePath)
                if self.filePath not in self.workspace.config['updatedFiles']:
                    self.workspace.config['updatedFiles'].append(self.filePath)
                    fileNode = self.workspaceTree.root.add(os.path.basename(self.filePath))
                    fileNode.data = self.filePath
                    self.workspace.save()

            except Exception as e:
                self.app.clear_notifications()
                self.notify(f"ERROR! {e.__class__.__name__}: {e.args[0]}", severity="error")
        else:
            if event.text_area.text != self.contentsOfFile:
                self.title = "*" + os.path.basename(self.filePath)
            else:
                self.title = os.path.basename(self.filePath)