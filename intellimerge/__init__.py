import ast

def merge(code: str, snippet: str) -> str:
    # Step 1: Parse the existing file
    try:
        existing_tree = ast.parse(code)
    except SyntaxError:
        raise SyntaxError("Invalid Python code in 'code'")

    # Step 2: Parse the snippet
    try:
        snippet_tree = ast.parse(snippet)
    except SyntaxError:
        raise SyntaxError("Invalid Python code in 'snippet'")

    # Step 3: Categorize nodes
    existing_body = existing_tree.body
    snippet_body = snippet_tree.body

    # Separate imports, classes, functions, and other global statements
    existing_imports = [node for node in existing_body if isinstance(node, (ast.Import, ast.ImportFrom))]
    existing_functions = [node for node in existing_body if isinstance(node, ast.FunctionDef)]
    existing_classes = [node for node in existing_body if isinstance(node, ast.ClassDef)]
    existing_others = [node for node in existing_body if node not in existing_imports + existing_functions + existing_classes]

    snippet_imports = [node for node in snippet_body if isinstance(node, (ast.Import, ast.ImportFrom))]
    snippet_functions = [node for node in snippet_body if isinstance(node, ast.FunctionDef)]
    snippet_classes = [node for node in snippet_body if isinstance(node, ast.ClassDef)]
    snippet_others = [node for node in snippet_body if node not in snippet_imports + snippet_functions + snippet_classes]

    # Merge imports: Add only unique imports
    merged_imports = {ast.dump(node): node for node in existing_imports + snippet_imports}.values()

    # Merge functions: Replace or add functions
    existing_functions_dict = {node.name: node for node in existing_functions}
    for snippet_function in snippet_functions:
        existing_functions_dict[snippet_function.name] = snippet_function
    merged_functions = list(existing_functions_dict.values())

    # Merge classes: Replace or add classes
    existing_classes_dict = {node.name: node for node in existing_classes}
    for snippet_class in snippet_classes:
        if snippet_class.name in existing_classes_dict:
            # Merge class methods
            existing_class = existing_classes_dict[snippet_class.name]
            existing_methods = {method.name: method for method in existing_class.body if isinstance(method, ast.FunctionDef)}
            for method in snippet_class.body:
                if isinstance(method, ast.FunctionDef):
                    existing_methods[method.name] = method
            existing_class.body = list(existing_methods.values())
        else:
            existing_classes_dict[snippet_class.name] = snippet_class
    merged_classes = list(existing_classes_dict.values())

    # Handle global code (others): Overwrite or replace entirely
    merged_others = snippet_others if snippet_others else existing_others

    # Combine everything back together
    new_body = list(merged_imports) + merged_classes + merged_functions + merged_others
    existing_tree.body = new_body

    # Step 4: Write back the modified code
    modified_code = ast.unparse(existing_tree)
    return modified_code
