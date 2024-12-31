import os
import json
from Utilities import default_prompt




class NVRConfig:
    def __init__(self):
        self.config = {}
        self.documentNever:str = os.path.join(os.getenv("USERPROFILE"), "Documents", "NEVER Editor")
        self.config_path = os.path.join(self.documentNever, "config.json")

        if not os.path.exists(self.documentNever):
            os.makedirs(self.documentNever)
            os.makedirs(os.path.join(self.documentNever, "Plugins"))
            os.makedirs(os.path.join(self.documentNever, ".prompts"))
            with open(os.path.join(self.documentNever, ".prompts", "neverPrompt.txt"), "+w") as f:
                f.write(default_prompt)
                f.close()

        self.load()

        self.ollamaModel = self.config.get("ollamaModel", None)
        self.theme = self.config.get("theme", "dracula")
        self.textAreaTheme = self.config.get("textAreaTheme", "vscode_dark")
        self.autoMerge: bool = self.config.get("autoMerge", False)
        self.autoSave: bool = self.config.get("autoSave", False)

    def load(self):
        """Discover and load plugins from the plugins directory."""
        if not os.path.exists(self.config_path):
            file = open(self.config_path, "+w")
            file.write(json.dumps({}))
            file.close()
        else:
            with open(self.config_path, "r") as config_file:
                self.config = json.load(config_file)

    def save(self):
        with open(self.config_path, "+w") as config_file:
            json.dump(self.config, config_file, indent=4)

    def get(self, key, default=None):
        self.load()
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save()

config = NVRConfig()