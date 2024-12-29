import os
import json
from textual.app import App
from typing import Dict

class NVRConfig:
    def __init__(self):
        self.config_path = "config.json"
        self.config = {}

        self.load()

        self.theme = self.config.get("theme", "gruvbox")
        self.textAreaTheme = self.config.get("textAreaTheme", "monokai")
        self.autoMerge: bool = self.config.get("autoMerge", False)

    def load(self):
        """Discover and load plugins from the plugins directory."""
        if not os.path.exists(self.config_path):
            open(self.config_path, "w").write(json.dumps({})).close()
        else:
            with open(self.config_path, "r") as config_file:
                self.config = json.load(config_file)

    def save(self):
        with open(self.config_path, "w") as config_file:
            json.dump(self.config, config_file, indent=4)

    def get(self, key, default=None):
        self.load()
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()

config = NVRConfig()