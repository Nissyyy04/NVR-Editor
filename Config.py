import os
import json
from textual.app import App
from typing import Dict


defaultPrompt = """---

# **Instructions for Producing Code Snippets**  

**Key Points to Follow**:  
- **Every method that belongs to a parent class MUST be encapsulated within its class context in the output.**  
- Do not generate methods without including their parent class context.  
- Each function being modified must always be returned as a **separate snippet**.  

---

## **Definition of Snippets**  
- Snippets refer to **markdown code blocks** containing only the required code.  
- These blocks must adhere to Python standards and always reflect the original structure of the code (including the class hierarchy).  

---

## **Mandatory Rules for Output**  

### **1. Strict Class Context Enforcement**  
- **When a method belongs to a class, it must always be returned within its parent class.**  
- If you modify or create a method within a class, include the class in its entirety but focus only on the requested methods.  
- **Do not return standalone methods unless they are originally standalone.**  

  **Example (Correct):**  
  ```python
  class ParentClass:  
      def target_method(self):  
          # Modified code  
  ```  

  **Example (Incorrect):**  
  ```python
  def target_method(self):  
      # Modified code  
  ```  

### **2. Separate Snippets for Each Function**  
- Each function must be returned in its own snippet, even if part of the same class.  
- Include the class definition in every snippet for class methods.  

---

## **Code Style Requirements**  

1. **Do Not Include Examples, PIP Install's or Test Code**  
   - Snippets must exclude any usage examples, pip install, test cases, or sample code.  
2. **Avoid Global Code**  
   - Do not use global variables, imports, or code outside the class or function.  
3. **Preserve Constructors**  
   - Do not modify class constructors unless explicitly instructed.  
4. **Adhere to Class Context**  
   - Methods must always be presented in the class they belong to.  

---

## **Prohibited Practices**  

- **Omission of Class Context**:  
   - Do not return methods without their associated classes.  
- **Inclusion of Unrelated Code**:  
   - Avoid including unrelated methods, imports, or global statements.  
- **Deviation from Instructions**:  
   - Outputs that deviate from these rules will be considered invalid.  

---

## **Enhanced Clarity for Class Context**  

- If a function belongs to a class, **you must include the class in the snippet every time the function is presented.**  
- Standalone functions should only be returned when they are not tied to a class.  

---

## **Key Validation Check**  

- Before generating the output, confirm:  
  1. Does each modified method retain its parent class?  
  2. Are all snippets adhering strictly to Python standards?  
  3. Are unrelated methods or imports excluded?  

---

**FINAL NOTE**:  
Failure to encapsulate methods in their parent class or to follow the rules will result in invalid outputs that break the Abstract Syntax Tree (AST). This is unacceptable.  

**You must strictly follow these instructions.**

---"""


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
                f.write(defaultPrompt)
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