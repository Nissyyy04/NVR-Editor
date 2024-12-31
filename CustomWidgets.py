from textual.widgets import TextArea, Label
from textual import events
from textual.reactive import reactive

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
