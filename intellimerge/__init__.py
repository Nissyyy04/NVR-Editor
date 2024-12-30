import ast

def merge(code: str, snippet: str) -> str:
    # Step 1: Parse the existing file
    try:
        existing_tree = ast.parse(code)
    except Exception:
        raise SyntaxError("Invalid Python code")

    # Step 2: Parse the snippet
    snippet_tree = ast.parse(snippet)

    # Step 3: Process top-level nodes
    existing_body = existing_tree.body
    existing_functions = {
        node.name: node for node in existing_body if isinstance(node, ast.FunctionDef)
    }
    existing_classes = {
        node.name: node for node in existing_body if isinstance(node, ast.ClassDef)
    }

    def contains_deletion_comment(node):
        """Check if the node contains a deletion comment."""
        if not hasattr(node, 'body'):
            return False
        for stmt in node.body:
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                comment = stmt.value.value
                if isinstance(comment, str) and any(keyword in comment.lower() for keyword in [
                    "#remove me", "#delete me", "#delete this", "#delete func", "#delete function"]):
                    return True
        return False

    # Remove functions or methods with deletion comments
    def filter_nodes(body):
        filtered_body = []
        for node in body:
            if isinstance(node, ast.FunctionDef):
                if not contains_deletion_comment(node):
                    filtered_body.append(node)
                else:
                    print(f"Removed: {node.name}")
            elif isinstance(node, ast.ClassDef):
                # Filter methods in the class
                node.body = filter_nodes(node.body)
                filtered_body.append(node)
            else:
                filtered_body.append(node)
        return filtered_body

    existing_body = filter_nodes(existing_body)

    for snippet_node in snippet_tree.body:
        if isinstance(snippet_node, ast.FunctionDef):

            # Handle functions
            if snippet_node.name in existing_functions:
                # Replace the existing function
                for i, node in enumerate(existing_body):
                    if isinstance(node, ast.FunctionDef) and node.name == snippet_node.name:
                        existing_body[i] = snippet_node
                        break
            else:
                # Add the new function
                existing_body.append(snippet_node)

        elif isinstance(snippet_node, ast.ClassDef):
            # Handle classes
            if snippet_node.name in existing_classes:
                # Merge methods in the class
                existing_class = existing_classes[snippet_node.name]
                existing_methods = {
                    method.name: method
                    for method in existing_class.body
                    if isinstance(method, ast.FunctionDef)
                }
                snippet_methods = {
                    method.name: method
                    for method in snippet_node.body
                    if isinstance(method, ast.FunctionDef)
                }

                for method_name, snippet_method in snippet_methods.items():
                    if method_name in existing_methods:
                        # Replace the method
                        for i, node in enumerate(existing_class.body):
                            if isinstance(node, ast.FunctionDef) and node.name == method_name:
                                existing_class.body[i] = snippet_method
                                break
                    else:
                        # Add the new method
                        existing_class.body.append(snippet_method)
            else:
                # Add the new class
                existing_body.append(snippet_node)

    # Step 4: Write back the modified code
    modified_code = ast.unparse(existing_tree)

    return modified_code
