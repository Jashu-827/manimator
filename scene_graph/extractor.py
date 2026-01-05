import ast
from .utils import extract_scene_class_name, ast_parse

class SceneGraphExtractor(ast.NodeVisitor):
    def __init__(self):
        self.objects = []
        self.animations = []
        self.current_time = 0.0
        self.object_counter = {}

    def _new_id(self, obj_type):
        count = self.object_counter.get(obj_type, 0) + 1
        self.object_counter[obj_type] = count
        return f"{obj_type}_{count}"

    def visit_Assign(self, node):
        try:
            if isinstance(node.value.func, ast.Name):
                obj_type = node.value.func.id
                if obj_type in ["Text", "Tex", "MathTex", "Circle", "Square", "Dot", "Line"]:
                    obj_id = self._new_id(obj_type)

                    # Extract content of Text / Tex
                    content = None
                    if node.value.args and isinstance(node.value.args[0], ast.Str):
                        content = node.value.args[0].s

                    self.objects.append({
                        "id": obj_id,
                        "type": obj_type,
                        "name": node.targets[0].id,
                        "content": content,
                        "position": None,
                        "animations": []
                    })
        except:
            pass
        
        self.generic_visit(node)

    def visit_Expr(self, node):
        """Capture animations like self.play(Write(obj))"""
        try:
            if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
                if node.value.func.attr == "play":
                    args = node.value.args
                    for arg in args:
                        if isinstance(arg, ast.Call):
                            anim_type = arg.func.id
                            target = arg.args[0].id if isinstance(arg.args[0], ast.Name) else "unknown"

                            start = self.current_time
                            end = self.current_time + 1.5   # default animation duration

                            self.animations.append({
                                "type": anim_type,
                                "target": target,
                                "start": start,
                                "end": end
                            })

                            # Also store inside object record
                            for obj in self.objects:
                                if obj["name"] == target:
                                    obj["animations"].append({
                                        "type": anim_type,
                                        "start": start,
                                        "end": end
                                    })

                            self.current_time = end
        except:
            pass
        
        self.generic_visit(node)

def generate_scene_graph(code):
    ast_tree = ast_parse(code)
    if ast_tree is None:
        return None

    extractor = SceneGraphExtractor()
    extractor.visit(ast_tree)

    scene_name = extract_scene_class_name(code)
    return {
        "scene_name": scene_name,
        "objects": extractor.objects,
        "timeline": extractor.animations
    }
