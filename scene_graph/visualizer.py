from graphviz import Digraph
import os

def visualize_scene_graph(graph, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)

    dot = Digraph(comment="Scene Graph", format="png")
    dot.attr(rankdir="LR")

    # Add nodes
    for obj in graph["objects"]:
        label = f"{obj['id']}\n({obj['type']})"
        dot.node(obj["id"], label, shape="box", style="filled", color="lightblue")

    # Add edges for animations
    for anim in graph["timeline"]:
        src = anim["target"]
        anim_label = f"{anim['type']}\n{anim['start']}→{anim['end']}"
        dot.edge(src, src, label=anim_label, color="black")

    path = os.path.join(output_dir, "scene_graph")
    dot.render(path, cleanup=True)

    return f"{path}.png"
