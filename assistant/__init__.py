from ollama import chat
from ollama import ChatResponse
import re, time
import intellimerge

# RUN IN TERMINAL: ollama run granite3.1-dense

class ArtificialIntelligence():
    history = []

    def __init__(self, model = "granite3.1-dense", promptPath = None):
        if not promptPath:
            raise Exception("No prompt path provided!")

        self.prompt = open(promptPath, "r").read()
        self.promptPath = promptPath
        self.model = model

        self.history = [
            {
                'role': 'system',
                'content': self.prompt
            }
        ]

    def generate(self, code:str, userPrompt:str):
        self.history.append({
                'role': 'user',
                'content': code
            })

        self.history.append({
                'role': 'user',
                'content': userPrompt,
            })

        response: ChatResponse = chat(model=self.model, messages=self.history)

        self.history.append({
            'role': 'assistant',
            'content': response.message.content
        })

        snippets = self._extractCode(response.message.content)

        mergedOutput: str = code


        for snippet in snippets:
            mergedOutput = intellimerge.merge(mergedOutput, snippet["code"])

        return mergedOutput, response, snippets

    def _extractCode(self, text:str) -> list:
        # Regex pattern for fenced code blocks
        code_block_pattern = r"```(\w+)?\n(.*?)```"

        # Find all code blocks
        matches = re.findall(code_block_pattern, text, re.DOTALL)

        # Add snippets to the list
        snippet_list = []
        for language, code in matches:
            snippet_list.append({
                "language": language.strip() if language else None,
                "code": code.strip()
            })

        return snippet_list