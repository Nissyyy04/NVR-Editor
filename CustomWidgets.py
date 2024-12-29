from textual.widgets import TextArea
from textual import events

class NVRTextArea(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    autofillWord = ""

    def __init__(self, text = "", *, language = None, theme = "css", soft_wrap = True, tab_behavior = "focus", read_only = False, show_line_numbers = False, line_number_start = 1, max_checkpoints = 50, name = None, id = None, classes = None, disabled = False, tooltip = None):
        super().__init__(text, language=language, theme=theme, soft_wrap=soft_wrap, tab_behavior=tab_behavior, read_only=read_only, show_line_numbers=show_line_numbers, line_number_start=line_number_start, max_checkpoints=max_checkpoints, name=name, id=id, classes=classes, disabled=disabled, tooltip=tooltip)
        

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

        elif event.key == "backspace":
            current_position = self.cursor_location[1] - 1

            if 0 <= self.cursor_location[0] < len(self.text.splitlines()):
                text = self.text.splitlines()[self.cursor_location[0]]
                
                if current_position >= 0:
                    if text[:current_position + 1].strip() == "" and text[:current_position + 1].endswith("    "):
                        for _ in range(4):
                            self.action_delete_left()
                        event.stop()