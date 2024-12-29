from textual.app import App, ComposeResult, SystemCommand
from textual.widgets import *
from textual.containers import *
from textual.screen import Screen
from textual.events import DescendantFocus
from typing import Iterable
from Screens import TextEditor, Settings
import os, shutil
import string
from PluginUtilities import PluginLoader
from Config import config
from textual.widgets.tree import TreeNode

class NVRMain(App):
    """Application with multiple screens."""

    tree: Tree[str] = None
    driveTree: Tree[str] = None
    pluginsTree: Tree[str] = None
    PL: PluginLoader
    TITLE = "A simple Code Editor made in Python!"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("alt+b", "popScreen", "Back", "Go back to last Screen", priority=True, tooltip="Go back to last Screen"),
        Binding("ctrl+r", "refresh", "Refresh", "Refresh the screen", priority=True, tooltip="Refresh the screen"),
        Binding("escape", "back", "CD ..", "Go back one directory", priority=False, tooltip="Go back one directory"),
        Binding("ctrl+o", "openSettings", "Settings", "Open the settings screen", priority=True, tooltip="Open the settings screen"),
    ]

    async def action_popScreen(self) -> None:
        self.app.notify("YES")
        if len(self.app.screen_stack) > 1:
            self.app.pop_screen()

    async def action_back(self) -> None:
        # Go back one directory
        parent_dir = os.path.dirname(os.getcwd())
        if os.path.ismount(parent_dir):
            self.tree.root.label = f"{parent_dir}"
            self.tree.root.expand()
        else:
            self.tree.root.label = f"..\\{parent_dir}"
            self.tree.root.expand()
        os.chdir(parent_dir)  # Change to parent directory
        self.tree.root.remove_children()  # Clear existing tree nodes
        self.populate_tree(self.tree.root, parent_dir)

    async def action_refresh(self) -> None:
        """Refresh the screen."""
        if len(self.screen_stack) > 1:
            self.screen.refresh(repaint=True, layout=True, recompose=True)
        else:
            self.refresh(repaint=True, layout=True, recompose=True)
        self.notify("Refreshed.")
    
    async def action_openSettings(self) -> None:
        """Open the settings screen."""
        self.push_screen(Settings.ScreenObject())

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)  
        yield SystemCommand("Settings", "NVR Settings Screen", self.settingsScreen) 

    def settingsScreen(self):
        self.push_screen(Settings.ScreenObject())

    def on_mount(self) -> None:
        """Set up screens when the app starts."""
        self.theme = config.theme
        
    def compose(self) -> ComposeResult:
        self.PL = PluginLoader(self.app, "Plugins")
        self.PL.load_plugins()

        self.driveTree = Tree("Drives")
        driveTree = self.driveTree

        driveTree.ICON_NODE = "💿 "

        self.pluginsTree = Tree("Plugins")
        pluginsTree = self.pluginsTree

        drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        for drive in drives:
            driveNode = driveTree.root.add(drive)
            driveNode.data = drive + "\\"

        for plugin_name, plugin in self.PL.plugins.items():
            plugin.load_config()
            pluginNode = pluginsTree.root.add(f"{plugin.name}: {'ON' if plugin.is_enabled else 'OFF'}")
            pluginNode.data = plugin
        
        with Container(id="sidebar").set_styles("dock: left; width: 20%; padding: 1 0 1 0;") as sideBar:
            driveTree.root.expand()
            pluginsTree.root.expand()
            yield Label("Sidebar").set_styles("text-align: center; width: 100%;")
            yield driveTree
            yield pluginsTree

        self.tree = Tree(f"..{os.getcwd()}")
        self.tree.root.expand()
        self.tree.ICON_NODE = "📁 "
        self.tree.ICON_NODE_EXPANDED = "📂 "

        # Start from the current directory
        self.populate_tree(self.tree.root, os.getcwd())

        with Container():
            yield self.tree

        yield Header(show_clock=True)
        yield Footer()

    def populate_tree(self, node: TreeNode, path):
        """Recursively populate the self.tree with files and folders."""
        try:
            for entry in os.scandir(path):
                if entry.is_dir():
                    # Add a folder and expand it lazily
                    folder_node = node.add(entry.name, expand=False)
                    # Attach the path as data for future expansion
                    folder_node.data = entry.path
                elif entry.is_file():
                    # Add a file leaf node
                    file_node = node.add_leaf("📄 " + entry.name)
                    file_node.data = entry.path
        except PermissionError:
            # Handle directories we can't access
            node.add_leaf("[Access Denied]")

    async def on_tree_node_expanded(self, event: Tree.NodeExpanded) -> None:
        """Handle lazy loading of folder contents when expanded."""
        if event.control is self.tree or event.control is self.driveTree:
            node = event.node
            if node.data:
                # Populate the folder if it has not been populated yet
                if not node.children:
                    self.populate_tree(node, node.data)

            if node.is_expanded and not node.is_root:
                node.collapse()
        
        elif event.control is self.pluginsTree:
            node = event.node
            plugin = node.data
            if node.data:
                node.remove_children()
                node.add_leaf(f"Delete Plugin", data=(plugin, "deletePlugin"))
                node.add_leaf(f"Toggle Plugin", data=(plugin, "togglePlugin"))

    async def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle file or folder selection."""
        node = event.node
        if node is self.tree.root:
            # Go back one directory
            parent_dir = os.path.dirname(os.getcwd())
            if os.path.ismount(parent_dir):
                self.tree.root.label = f"{parent_dir}"
                self.tree.root.expand()
            else:
                self.tree.root.label = f"..\\{parent_dir}"
                self.tree.root.expand()
            os.chdir(parent_dir)  # Change to parent directory
            node.remove_children()  # Clear existing tree nodes
            self.populate_tree(node, parent_dir)
        
        elif node.parent is self.driveTree.root:
            self.tree.root.label = f"{node.data}"

            os.chdir(node.data)

            #self.notify(f"Drive opened: {node.data}")

            self.tree.root.remove_children()  # Clear existing tree nodes
            self.populate_tree(self.tree.root, os.getcwd())

        elif node.data and node.parent is self.tree.root:
            item_type = "File" if os.path.isfile(node.data) else "Folder"

            if item_type == "Folder":
                # Navigate into the selected folder
                os.chdir(node.data)

                # Clear root and repopulate tree for new path
                self.tree.root.remove_children()
                self.tree.root.label = f"..\\{node.data}"
                self.populate_tree(self.tree.root, node.data)

                #self.notify(f"Folder opened: {node.data}")
            else:
                # File handling (e.g., opening)
                self.push_screen(TextEditor.ScreenObject(filepath=node.data))
                #self.notify(f"File opened: {node.data}")
            self.clear_notifications()
        
        elif node.data is not None and node.parent.parent is self.pluginsTree.root:
            if node.data[1] == "deletePlugin":
                plugin = node.data[0]
                self.PL.plugins.pop(plugin.name)
                plugin.unload()
                node.parent.remove_children()
                node.parent.remove()
                shutil.rmtree(plugin.plugin_path)
                self.notify(f"Plugin '{plugin.name}' deleted.")
            if node.data[1] == "togglePlugin":
                plugin = node.data[0]
                if plugin.is_enabled:
                    plugin.disable()
                else:
                    plugin.enable()
                node.parent.label = f"{plugin.name}: {'ON' if plugin.is_enabled else 'OFF'}"


if __name__ == "__main__":
    NVRMain().run()