import ast
import re

def extract_scene_class_name(code):
    match = re.search(r"class\s+(\w+)\(.*Scene\):", code)
    return match.group(1) if match else None

def ast_parse(code):
    try:
        return ast.parse(code)
    except Exception:
        return None
