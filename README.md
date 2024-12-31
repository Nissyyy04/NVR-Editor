# NVR-Editor

NVR-Editor is a terminal-based Python code editor designed for efficient and streamlined development directly from the command line.
This tools AST merging functionality is a python implementation of the AST merging methodology from the [aiCoder project](https://github.com/mmiscool/aiCoder)

![{625BDCF7-B06B-4045-B22F-A3D3F5478386}](https://github.com/user-attachments/assets/738e10aa-7f3a-459c-a73f-cf31272ac750)
---
![{179FE8BD-E171-4955-9F5A-745951A8ED3C}](https://github.com/user-attachments/assets/b4a08b84-e2b7-4ce1-b436-0cddc7c3a359)
![{E179AAB3-8D25-4EDF-A843-0AC9DEE2B94B}](https://github.com/user-attachments/assets/b60afad8-a3c3-4e04-bf87-bdc8f627adb8)


## Features

- **AI-Driven Refactoring**: Leverages advanced Abstract Syntax Tree (AST) merging for seamless code integration and editing.
- **Terminal-Based Interface**: Operate entirely within the terminal, eliminating the need for external GUI-based editors.
- **Plugin Support**: Extend functionality through a flexible plugin system.
- **Customizable Configuration**: Adjust settings via a `config.json` file to tailor the editor to your preferences.

---

## Downloading the AI Model
To use the **granite3.1-dense** model with **Ollama**, follow these steps:

## Step 1: Install Ollama
Ensure that you have **Ollama** installed. If it's not already installed, download it from the [Ollama website](https://ollama.ai) and follow the installation instructions for your platform.

## Step 2: Download granite3.1-dense
Ollama provides a simple command-line interface to download and use models. To download the **granite3.1-dense** model:
1. Open your terminal.
2. Run the following command:

   ```bash
   ollama pull granite3.1-dense
   ```

This command will fetch the granite3.1-dense model and prepare it for use.
## Step 3: Verify Installation
To ensure the model is downloaded and available for use, run:
```bash
ollama list
```
This will display a list of models installed on your system. Ensure that **granite3.1-dense** is listed.

## Step 4 (OPTIONAL): Testing the model
To test granite3.1-dense directly from Ollama, you can run:
```bash
ollama chat granite3.1-dense
```

This opens an interactive chat with the model to verify its capabilities.

## Additional Resources
- Visit the [Ollama Documentation](https://ollama.ai/docs) for detailed instructions and troubleshooting.
- Explore the [granite3.1-dense GitHub Repository](https://github.com/openai/granite3.1-dense) (if available) for technical details and model-specific configurations.
---


## Why the AI Features Are Awesome

### AST Merging Over Line Merging

Unlike traditional editors that rely on line-by-line merging, which can introduce conflicts and inconsistencies:

- **AST Merging** understands the structure of your Python code, treating it as a logical tree rather than raw text.
- This means:
  - **Fewer Merge Conflicts**: Changes are merged at the function or block level instead of arbitrary lines.
  - **Intelligent Refactoring**: Automatically handles imports, function renaming, or structural changes.
  - **Semantic Awareness**: Ensures code remains valid and functional after edits, even in complex scenarios.
---

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/Nissyyy04/NVR-Editor.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd NVR-Editor
   ```

3. **Install Dependencies**:

   Ensure you have Python installed, then install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

Run the main script to start the editor:

```bash
python main.py
```

Upon launch, NVR-Editor will load with the default configuration specified in `config.json`.

---

## Configuration

Modify the `config.json` file to customize editor settings.

---

## Plugins

Extend NVR-Editor's functionality by adding plugins to the `Plugins` directory. Each plugin should be a Python script with a specific structure. Below is an example of a simple plugin:

### Directory Structure

```
Plugins/
└── test_plugin/
    ├── __init__.py
    └── test_plugin.py
```

### Example Code: `test_plugin.py`

```python
from textual.app import App
from textual.widgets import Label

class TestPlugin():
    def __init__(self, app: App):
        self.app = app
        self.app.mount(Label("Hello from Test Plugin").set_styles("width: 100%; text-align: center;"))
```

### Steps to Add a Plugin

1. Create a new directory under `Plugins/` with your plugin name.
2. Add your plugin script inside the directory.
3. Define the appropriate hooks like `on_startup()` and `on_keypress()` to integrate with NVR-Editor.

### TO DO (SOONISH)

---

### AI-Powered Auto-Fixes

NVR-Editor provides:
- **Context-Aware Suggestions**: Suggests improvements or fixes based on the code's purpose.
- **Error Resolution**: Identifies and proposes solutions for syntax or logical errors.
- **Code Optimization**: Recommends better practices and optimizations based on Pythonic principles.

### Integrated AI Workflows

The AI integrates seamlessly into your workflow:
- **On-the-Fly Syntax Updates**: Modify your code without worrying about structural integrity.
- **AI-Driven Snippets**: Insert pre-tested, contextually appropriate snippets for repetitive tasks.
  
---

## License

This project is licensed under the Apache License 2.0.

For more details, visit the [GitHub repository](https://github.com/Nissyyy04/NVR-Editor).
