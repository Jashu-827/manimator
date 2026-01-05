import os
import re
import subprocess
# from groq import Groq
from openai import OpenAI
from langchain_core.prompts import PromptTemplate
import requests
import json
from scene_graph.extractor import generate_scene_graph
from scene_graph.validator import validate_scene_graph
from scene_graph.timeline import build_timeline
from pathlib import Path
# from scene_graph.visualizer import visualize_scene_graph


from dotenv import load_dotenv

# Load the .env file
load_dotenv()

api_key = os.getenv("open_api_key")

if not api_key:
    raise ValueError("❌ open_api_key not found in .env file!")


os.environ["open_api_key"] = api_key


# Initialize Groq client using your API key from environment
# api_key = os.getenv("GROQ_API")
if not api_key:
    raise ValueError("API key not found. Set it using: setx GROQ_API 'your_api_key_here'")

# client = Groq(api_key=api_key)
client = OpenAI(base_url="https://openrouter.ai/api/v1",
                api_key=api_key)
# Prompt Template
prompt_template = PromptTemplate(
    input_variables=["user_prompt"],
    template="""
You are an expert Python programmer specialized in creating animations with the Manim library.

Task: Generate a complete Python script using Manim that visualizes the mathematical concept described by the user.

REQUIREMENTS:
1. Use `Scene` class
2. Include explanatory text using `Text` or `Tex` objects
3. Position text so it does NOT overlap with main objects (use .to_edge(), .next_to(), .shift())
4. Add mathematical formulas using `MathTex` when appropriate
5. Animate both visualization AND explanatory text
6. Title should appear at top of screen
7. Use proper timing with self.wait()
8. Make the animation clear and educational
9. Output ONLY the Python code
10. To prevent text overflow:
   - Use `.scale_to_fit_width(config.frame_width * 0.8)`
   - Position text at bottom using `.to_edge(DOWN)`

User input: {user_prompt}

Generate the complete Manim script:
"""
)

def extract_python_code(text):
    """Extract Python code from LLM response"""
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    if code_blocks:
        return code_blocks[0].strip()
    else:
        return text.strip()

# def generate_and_render_animation(user_prompt):
#     """Generate and render Manim animation from user prompt"""
#     print(f"🎬 Generating animation for: {user_prompt}")
#     formatted_prompt = prompt_template.format(user_prompt=user_prompt)

#     try:
#         chat_completion = client.chat.completions.create(
#             messages=[{"role": "user", "content": formatted_prompt}],
#             model="qwen/qwen3-235b-a22b:free"
#         )
#         response = chat_completion.choices[0].message.content
#     except Exception as e:
#         print(f"Error getting LLM response: {e}")
#         return None

#     code_only = extract_python_code(response)
#     script_filename = "generated_manim_animation.py"

#     with open(script_filename, "w", encoding="utf-8") as f:
#         f.write(code_only)

#     print(f"✅ Manim code generated and saved as {script_filename}")

#     # Extract the Scene class name
#     match = re.search(r"class\s+(\w+)\(.*Scene\):", code_only)
#     scene_name = match.group(1) if match else None
#     if not scene_name:
#         print("❌ Could not detect a scene class name.")
#         return None

#     print(f"🎥 Rendering scene: {scene_name}")
#     try:
#         subprocess.run(["manim", "-pqm", script_filename, scene_name], check=True)
#         print("✅ Rendering complete!")
#     except subprocess.CalledProcessError as e:
#         print(f"Rendering failed: {e}")
#         return None

#     # Find the video
#     base_name = script_filename.replace(".py", "")
#     search_path = f"media/videos/{base_name}/720p30/"
#     if os.path.exists(search_path):
#         mp4_files = [os.path.join(search_path, f) for f in os.listdir(search_path) if f.endswith(".mp4")]
#         if mp4_files:
#             print(f"🎬 Video ready: {mp4_files[0]}")
#             return mp4_files[0]
#     print("❌ No video file found.")
#     return None

def generate_and_render_animation(user_prompt):
    import uuid
    run_id = str(uuid.uuid4())[:8]

    """Generate and render Manim animation from user prompt"""
    print(f"🎬 Generating animation for: {user_prompt}")
    formatted_prompt = prompt_template.format(user_prompt=user_prompt)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "qwen/qwen3-coder:free",
        "messages": [
            {"role": "system", "content": "You are an expert Manim animation generator."},
            {"role": "user", "content": formatted_prompt}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        response_text = data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error getting LLM response: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Response text:", e.response.text)
        return None

    code_only = extract_python_code(response_text)
    
    script_filename = "generated_manim_animation.py"

    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(code_only)

    print(f"✅ Manim code generated and saved as {script_filename}")
    scene_graph = generate_scene_graph(code_only)
    timeline = build_timeline(scene_graph["timeline"])
    errors = validate_scene_graph(scene_graph)

    print("\n📌 Generated Scene Graph:")
    print(json.dumps(scene_graph, indent=4))

    print("\n📌 Timeline Mapping:")
    print(json.dumps(timeline, indent=4))

    if errors:
        print("\n❌ Scene Graph Validation Errors:")
        for e in errors:
            print(" -", e)
    else:
        print("\n✅ Scene Graph is valid!")
    
    # ─────────────────────────────
    # SAVE GRAPH + TIMELINE AS JSON
    # ─────────────────────────────
    # os.makedirs("outputs", exist_ok=True)

    # with open("outputs/scene_graph.json", "w") as f:
    #     json.dump(scene_graph, f, indent=4)

    # with open("outputs/timeline.json", "w") as f:
    #     json.dump(timeline, f, indent=4)

    # print("\n💾 Scene Graph JSON saved to outputs/scene_graph.json")
    # print("💾 Timeline JSON saved to outputs/timeline.json")

    # # ─────────────────────────────
    # # VISUALIZE SCENE GRAPH (GRAPHVIZ)
    # # ─────────────────────────────
    # try:
    #     diagram_path = visualize_scene_graph(scene_graph)
    #     print(f"\n🖼 Scene Graph diagram generated at: {diagram_path}")
    # except Exception as e:
    #     print("\n⚠ Could not generate Scene Graph diagram. Install Graphviz:")
    #     print("   pip install graphviz")
    #     print("Error:", e)



    match = re.search(r"class\s+(\w+)\(.*Scene\):", code_only)
    
    scene_name = match.group(1) if match else None
    if not scene_name:
        print("❌ Could not detect a scene class name.")
        return None

    print(f"🎥 Rendering scene: {scene_name}")
    try:
        output_dir = f"media/videos/run_{run_id}"
        # subprocess.run(["manim", "-pqm", script_filename, scene_name], check=True)
        cmd = ["manim", "-qm", "--media_dir", output_dir,script_filename, scene_name]
        subprocess.run(cmd, check=True)

        print("✅ Rendering complete!")
    except subprocess.CalledProcessError as e:
        print(f"Rendering failed: {e}")
        return None

    # Look ONLY inside this run's output directory
    mp4_files = list(Path(output_dir).rglob("*.mp4"))

    if not mp4_files:
        print("❌ No video generated in this run")
        return None

    video_path = str(mp4_files[0])
    print("🎬 Video generated at:", video_path)
    return video_path



if __name__ == "__main__":
    user_input = input("🧮 Enter the topic for animation: ")
    video_path = generate_and_render_animation(user_input)
    if video_path:
        print(f"\n✅ Success! Video saved at: {video_path}")
    else:
        print("\n❌ Failed to generate video. Check errors above.")
