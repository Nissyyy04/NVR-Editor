from textual.widgets import TextArea
from textual import events

class NVRTextArea(TextArea):
    """A subclass of TextArea with parenthesis-closing functionality."""

    def _on_key(self, event: events.Key) -> None:
        if event.character == "(":
            self.insert("()")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        if event.character == "[":
            self.insert("[]")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        if event.character == "{":
            self.insert("{}")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        if event.character == '"':
            self.insert('""')
            self.move_cursor_relative(columns=-1)
            event.prevent_default()
        
        if event.character == "'":
            self.insert("''")
            self.move_cursor_relative(columns=-1)
            event.prevent_default()

        ### WIP

        #if event.key == "backspace":
            #current_position = self.cursor_location[1]
            #text = self.text.splitlines()[self.cursor_location[0]+1]
            #self.notify(text)
            