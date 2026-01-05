def validate_scene_graph(graph):
    errors = []

    # 1. Check for missing scene name
    if not graph.get("scene_name"):
        errors.append("Scene name not found")

    # 2. Check for animations targeting missing objects
    object_names = {obj["name"] for obj in graph["objects"]}
    for anim in graph["timeline"]:
        if anim["target"] not in object_names:
            errors.append(f"Animation targets undefined object: {anim['target']}")

    # 3. Check invalid time intervals
    for anim in graph["timeline"]:
        if anim["end"] <= anim["start"]:
            errors.append(f"Invalid animation timing: {anim}")

    return errors
