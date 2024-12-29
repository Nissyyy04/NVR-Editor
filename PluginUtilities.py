import os
import json
import importlib
from textual.app import App
from typing import Dict

class Plugin:
    def __init__(self, name: str, plugin_path: str, app: App):
        self.name = name
        self.plugin_path = os.path.abspath(plugin_path)  # Ensure full directory path
        self.config_path = os.path.join(self.plugin_path, "config.json")
        self.is_enabled = False
        self.config = {}
        self.is_loaded = False
        self.app = app
        self.load_config()

        if not self.config.get("projectPreferences", None):
            self.config["projectPreferences"] = {}
            self.save_config()

    def load(self):
        """Load the plugin and its entry point."""
        try:
            entry_point = self.config.get("entry_point", "").split(".")
            if not entry_point:
                raise ValueError("Entry point not defined in config.")
            
            module_name, class_name = ".".join(entry_point[:-1]), entry_point[-1]
            module_path = os.path.join(self.plugin_path, module_name + ".py")
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            plugin_class = getattr(module, class_name, None)
            if not plugin_class:
                raise ImportError(f"Class {class_name} not found in module {module_name}.")
            
            self.instance = plugin_class(self.app)
            self.is_enabled = True
            self.is_loaded = True
        except Exception as e:
            print(f"Error loading plugin '{self.name}': {e}")

    def unload(self):
        """Unload the plugin."""
        self.is_enabled = False
        self.instance = None
        #self.app.notify(f"Plugin '{self.name}' unloaded.")

    def enable(self, project_path: str = None):
        """Enable the plugin using its config."""
        if project_path:
            if "projectPreferences" in self.config:
                self.config["projectPreferences"].pop(project_path, None)
        else:
            self.is_enabled = True
            self.config["enabled"] = True
        self.save_config()
        #self.app.notify(f"Plugin '{self.name}' enabled.")

    def disable(self, project_path: str = None):
        """Disable the plugin using its config."""
        if project_path:
            if "projectPreferences" not in self.config:
                self.config["projectPreferences"] = {}
            self.config["projectPreferences"][project_path] = True
        else:
            self.is_enabled = False
            self.config["enabled"] = False
        self.save_config()
        #self.app.notify(f"Plugin '{self.name}' disabled.")


    def load_config(self):
        """Load plugin configuration from file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as config_file:
                self.config = json.load(config_file)
                self.is_enabled = self.config.get("enabled", False)

    def save_config(self):
        """Save the current configuration to file."""
        with open(self.config_path, "w") as config_file:
            json.dump(self.config, config_file, indent=4)

class PluginLoader:
    def __init__(self, app: App, plugins_directory: str):
        self.app = app
        self.plugins_directory = os.path.abspath(plugins_directory)  # Ensure full directory path
        self.plugins: Dict[str, Plugin] = {}

    def load_plugins(self, project_path: str = None):
        """Discover and load plugins from the plugins directory."""
        if not os.path.exists(self.plugins_directory):
            os.makedirs(self.plugins_directory)

        for folder in os.listdir(self.plugins_directory):
            plugin_path = os.path.join(self.plugins_directory, folder)
            if os.path.isdir(plugin_path):
                plugin = self._initialize_plugin(folder, plugin_path)
                if plugin:
                    self.plugins[plugin.name] = plugin
                    plugin.load_config()

                    if plugin.is_enabled and not plugin.is_loaded:
                        if project_path:
                            if not project_path in plugin.config["projectPreferences"]:
                                plugin.load()
                        elif not plugin.is_loaded:
                            plugin.load()

    def _initialize_plugin(self, folder: str, plugin_path: str) -> Plugin:
        """Initialize a plugin from its configuration."""
        config_path = os.path.join(plugin_path, "config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as config_file:
                    config = json.load(config_file)
                    return Plugin(name=config["name"], plugin_path=plugin_path, app=self.app)
            except Exception as e:
                print(f"Error initializing plugin '{folder}': {e}")
        return None
