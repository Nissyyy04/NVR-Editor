from ollama import chat
from ollama import ChatResponse
import re, time
import intellimerge

# RUN IN TERMINAL: ollama run granite3.1-dense

class ArtificialIntelligence():
    prompt = """# Instructions for Producing Code Snippets
DO NOT INCLUDE EXAMPLES OR TESTS IN YOUR CODE SNIPPETS.
DO NOT INCLUDE EXAMPLES OR TESTS IN YOUR CODE SNIPPETS.
DO NOT INCLUDE EXAMPLES OR TESTS IN YOUR CODE SNIPPETS.
Each function being modified should ALWAYS be returned as a separate snippet, and for each function the function should still be retained in its class context whithin the snippet.
Each function that has a parent class should be in that class context within all markdown code snippet's.

** MARKDOWN CODE BLOCKS ARE WHAT WE ARE REFERING TO AS SNIPPETS **

**Strict Adherence to Python Syntax and Class Context**: 
    - Always match the original context of the function or method. If a function is part of a class, ensure the snippet encapsulates the function within the class. 
    - If the function is standalone, provide it as a standalone snippet.

**Output Requirements**:
1. **Separate Snippets for Each Function**: 
    - Each function or method being modified must be provided as its own isolated code snippet.
    - If modifying multiple methods within a class, each method should be output as a separate snippet encapsulated in its parent class.
    - For example:

    class ExampleClass: def example_method(self): # Example code
    class AnotherClass: def another_method(self): # Example code

2. **Encapsulation**: 
    - Always include the parent class when providing a method. Do not send methods without their class.
    - For standalone functions, provide only the function definition.

**Code Style Rules**:
    1. **No Examples or Tests**: Do not include any examples, tests, or usage demonstrations in your response.
    2. **No Global Code**: Do not include global variables, imports, or code outside the class or function.
    3. **Constructor Edits**: Do not modify constructors unless specifically instructed and justified.
    4. **Each function being modified should ALWAYS be returned as a separate snippet, and for each function the function should still be retained in its class context whithin the snippet.**
    5. **Each function that has a parent class should be in that class context within all markdown code snippet's.**

**Prohibited Practices**:
    - Do not include unrelated methods or code within the class.
    - Do not include imports, examples, or test cases.

**Clarity and Consistency**:
    - Clearly distinguish between class methods and standalone functions by maintaining the correct context in the snippet.
    - Ensure all snippet's are formatted according to Python standards.

**Additional Guidelines**:
    - If modifying or creating a method that has a parent class, ensure it is within the original class when sent as a snippet (markdown code block).
    - Think thoroughly of what is said in this prompt before generating any output.

**IMPORTANT**: YOU MUST STRICTLY FOLLOW THE ABOVE INSTRUCTIONS, OR THE OUTPUT WILL BE INVALID AND BREAK THE ABSTRACT SYNTAX TREE.
**IMPORTANT**: YOU MUST STRICTLY FOLLOW THE ABOVE INSTRUCTIONS, OR THE OUTPUT WILL BE INVALID AND BREAK THE ABSTRACT SYNTAX TREE.
**IMPORTANT**: YOU MUST STRICTLY FOLLOW THE ABOVE INSTRUCTIONS, OR THE OUTPUT WILL BE INVALID AND BREAK THE ABSTRACT SYNTAX TREE.

"""

    history = []

    def __init__(self, name:str = "DeepSeek Coder"):
        if name:
            self.prompt += f"""Your name is {name} and you should refer to yourself as {name}!"""

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

        response: ChatResponse = chat(model='qwen2.5-coder', messages=self.history)

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