from textual.widgets import TextArea, Label
from textual import events
from textual.reactive import reactive
from textual.widgets.tree import TreeNode
import os, re, json

default_css = """#welcome-message {
    margin: 1 0 1 2;
    padding: 0;
    border-bottom: wide $primary;
    width: auto;
}

.accent {
    background: $panel;            /* Textual variable */
}

Screen{
    align: center middle;
}

Button{
    padding: 0 2 0 2;
}
"""

default_prompt = """---

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

class ReactiveLabel(Label):
    text = reactive("")

    def __init__(
        self, 
        renderable="", 
        *, 
        variant=None, 
        expand=False, 
        shrink=False, 
        markup=True, 
        name=None, 
        id=None, 
        classes=None, 
        disabled=False
    ):
        super().__init__(renderable, variant=variant, expand=expand, shrink=shrink, markup=markup, name=name, id=id, classes=classes, disabled=disabled)
        self.text = renderable  # Initialize reactive text

    def watch_text(self, new_value: str):
        """Automatically update the label content when `text` changes."""
        self.update(new_value)

    def render(self):
        """Define how the label is rendered."""
        return self.text

class NVRTextArea(TextArea):
    """A subclass of TextArea with enhanced functionality."""

    def __init__(
        self, 
        text="", 
        *, 
        language=None, 
        theme="css", 
        soft_wrap=True, 
        tab_behavior="focus", 
        read_only=False, 
        show_line_numbers=False, 
        line_number_start=1, 
        max_checkpoints=50, 
        name=None, 
        id=None, 
        classes=None, 
        disabled=False, 
        tooltip=None
    ):
        super().__init__(
            text, 
            language=language, 
            theme=theme, 
            soft_wrap=soft_wrap, 
            tab_behavior=tab_behavior, 
            read_only=read_only, 
            show_line_numbers=show_line_numbers, 
            line_number_start=line_number_start, 
            max_checkpoints=max_checkpoints, 
            name=name, 
            id=id, 
            classes=classes, 
            disabled=disabled, 
            tooltip=tooltip
        )

    def _on_key(self, event: events.Key) -> None:
        if event.character == "(":
            self.insert("()")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        elif event.character == "[":
            self.insert("[]")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        elif event.character == "{":
            self.insert("{}")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        elif event.character == '"':
            self.insert('""')
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        elif event.character == "'":
            self.insert("''")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()

        elif event.key == "enter":
            # Determine the current line's indentation
            cursor_line = self.cursor_location[0]
            lines = self.text.splitlines()
            if 0 <= cursor_line < len(lines):
                current_line = lines[cursor_line]
                leading_whitespace = len(current_line) - len(current_line.lstrip())
                indentation = current_line[:leading_whitespace]

                # Insert a newline with the same indentation
                self.insert("\n" + indentation)
                event.prevent_default()

        elif event.key == "tab":
            if self.selection:
                start_line = self.selection[0][0]
                end_line = self.selection[1][0]

                # Ensure the order of selection (start -> end)
                if start_line > end_line:
                    start_line, end_line = end_line, start_line

                # Insert a tab at the beginning of each selected line
                for y in range(start_line, end_line + 1):
                    self.insert("\t", (y, 0))

                event.prevent_default()

        elif event.key == "backspace":
            current_position = self.cursor_location[1] - 1

            if 0 <= self.cursor_location[0] < len(self.text.splitlines()):
                text = self.text.splitlines()[self.cursor_location[0]]
                
                if current_position >= 0:
                    if text[:current_position + 1].strip() == "" and text[:current_position + 1].endswith("    "):
                        for _ in range(4):
                            self.action_delete_left()
                        event.prevent_default()

class WorkspaceClass:
    def __init__(self, path):
        self.config_path = path

        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as f:
                f.write(json.dumps({'updatedFiles': []}))
                f.close()

        self.config = {}

        self.load()


    def load(self):
        """Discover and load plugins from the plugins directory."""
        if not os.path.exists(self.config_path):
            open(self.config_path, "w").write(json.dumps({})).close()
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

def populate_tree(node: TreeNode, path):
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

def remove_code_snippets(markdown_text):
    """
    Removes code snippets from a Markdown string and leaves only the text.

    Parameters:
        markdown_text (str): The Markdown content.

    Returns:
        str: The Markdown content with code snippets removed.
    """
    # Regex pattern for fenced code blocks
    code_block_pattern = r"```.*?\n(.*?)```"
    
    # Remove code snippets
    text_without_code = re.sub(code_block_pattern, '', markdown_text, flags=re.DOTALL)
    
    # Remove extra blank lines left behind by the removal
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', text_without_code).strip()

    return cleaned_text
