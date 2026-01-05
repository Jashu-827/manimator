"""
frontend_app.py

Minimal Flask frontend to drive your existing app.py generate_and_render_animation pipeline
and to display:
 - generated Manim code
 - scene graph JSON
 - timeline JSON
 - scene graph diagram (png) if available
 - rendered video (mp4) if produced

Place this file in the same directory as your app.py and the scene_graph package.
"""

import os
import json
import shutil
import time
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify, send_from_directory, abort

# Import your existing backend function (app.py must be in same folder)
# app.py was provided earlier and contains generate_and_render_animation(...) function.
try:
    from backend import generate_and_render_animation  # your existing file; do not change it
except Exception as e:
    raise RuntimeError(f"Could not import generate_and_render_animation from app.py: {e}")

# scene_graph utilities (assumes scene_graph package is available next to app.py)
try:
    from scene_graph.extractor import generate_scene_graph
    from scene_graph.timeline import build_timeline
    from scene_graph.validator import validate_scene_graph
except Exception as e:
    raise RuntimeError(f"Missing scene_graph utilities. Ensure scene_graph.extractor/timeline/validator exist: {e}")

# optional visualizer (Graphviz)
VISUALIZER_AVAILABLE = True
try:
    from scene_graph.visualizer import visualize_scene_graph
except Exception:
    VISUALIZER_AVAILABLE = False

# Flask app
app = Flask(__name__, static_folder="outputs", template_folder="templates")

# Ensure outputs dir
os.makedirs("outputs", exist_ok=True)

# Simple HTML template (minimal, light theme). The textarea auto-resizes.
INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Manim Animator — Frontend</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    html, body {
      overflow-x: hidden;
    }

    pre {
      overflow-x: hidden;
      overflow-y: auto;
      max-height: 320px;
      white-space: pre-wrap;
      word-break: break-word;
    }

    video {
      width: 100%;
      max-width: 100%;
      height: auto;
    }

    :root{
      --bg: #f7fbff;
      --card: #ffffff;
      --muted: #556;
      --accent: #4b8cff;
      --ok: #1f9d74;
      --danger: #d9534f;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    body{ background:var(--bg); margin:0; color:var(--muted); }
    .wrap{ max-width:980px; margin:28px auto; padding:20px; }
    .card{ background:var(--card); border-radius:12px; box-shadow:0 6px 18px rgba(60,80,100,0.06); padding:18px; margin-bottom:16px; }
    h1{ margin:0 0 8px 0; color:#1d3557; font-size:20px; }
    p.lead{ margin:0 0 14px 0; color:#3b4b62; }
    label{ display:block; font-size:13px; margin-bottom:6px; color:#374151; }
    textarea{ width:100%; min-height:64px; resize:none; padding:12px; border-radius:8px; border:1px solid #e6eefb; font-size:14px; outline:none; box-sizing:border-box; background:#fbfdff;}
    button{ background:var(--accent); color:white; border:0; padding:10px 14px; border-radius:8px; cursor:pointer; font-weight:600; }
    button:disabled{ opacity:0.6; cursor:default; }
    .row{ display:flex; gap:12px; align-items:flex-start; }
    .col{ flex:1; }
    pre, code{ background:#f3f6fb; padding:12px; border-radius:8px; overflow:auto; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace; font-size:13px; }
    .meta{ font-size:13px; color:#5b6b7e; margin-top:8px; }
    img.diagram{ max-width:100%; border-radius:8px; border:1px solid #eef6ff; }
    video{ max-width:100%; border-radius:8px; background:black; display:block; margin-top:8px; }
    .small{ font-size:13px; color:#6b7280; }
    .flex-between{ display:flex; justify-content:space-between; align-items:center; gap:12px; }
    a.link{ color:var(--accent); text-decoration:none; font-weight:600; }
    .outputs-grid{ display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:12px; }
    @media (max-width:820px){ .outputs-grid{ grid-template-columns: 1fr; } .row{ flex-direction:column; } }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div class="flex-between">
        <div>
          <h1>Manim Animator</h1>
          <p class="lead">Enter a short prompt describing the animation you'd like. The backend will generate Manim code, extract a scene graph & timeline, render a video, and display all outputs here.</p>
        </div>
        <div class="small">Status: <span id="status">idle</span></div>
      </div>

      <form id="promptForm">
        <label for="prompt">Animation prompt</label>
        <textarea id="prompt" name="prompt" placeholder="e.g., Show the graph of y = x^2 and explain vertex transformation..." oninput="autoResize(this)"></textarea>
        <div style="margin-top:10px; display:flex; gap:8px;">
          <button id="generateBtn" type="submit">Generate & Render</button>
          <button id="clearBtn" type="button">Clear</button>
        </div>
        <div class="meta">Note: Rendering a full Manim animation may take some time — the page will wait while the backend runs the pipeline.</div>
      </form>
    </div>

    <div id="outputs" class="card" style="display:none;">
      <div class="flex-between">
        <h2 style="font-size:16px; margin:0;">Outputs</h2>
        <div class="small">You can download any file from the links below.</div>
      </div>

      <div class="outputs-grid" style="margin-top:12px;">
        <div>
          <h3 style="font-size:14px; margin-bottom:6px;">Generated Manim Code</h3>
          <pre id="codeBlock">No code yet.</pre>
          <div style="margin-top:6px;"><a id="downloadCode" class="link" href="#">Download code</a></div>
        </div>

        <div>
          <h3 style="font-size:14px; margin-bottom:6px;">Scene Graph (JSON)</h3>
          <pre id="graphJSON">No scene graph yet.</pre>
          <div style="margin-top:6px;">
            <a id="downloadGraph" class="link" href="#">Download scene_graph.json</a>
          </div>
        </div>

        <div>
          <h3 style="font-size:14px; margin-bottom:6px;">Timeline (JSON)</h3>
          <pre id="timelineJSON">No timeline yet.</pre>
          <div style="margin-top:6px;">
            <a id="downloadTimeline" class="link" href="#">Download timeline.json</a>
          </div>
        </div>

        <div>
          <h3 style="font-size:14px; margin-bottom:6px;">Scene Graph Diagram</h3>
          <div id="diagramWrap">
            <div class="small" id="diagramInfo">Diagram not generated.</div>
            <img id="diagramImg" class="diagram" src="" style="display:none;" />
            <div style="margin-top:6px;">
              <a id="downloadDiagram" class="link" href="#">Download diagram</a>
            </div>
          </div>
        </div>

        <div style="grid-column: 1 / -1;">
          <h3 style="font-size:14px; margin-bottom:6px;">Rendered Video</h3>
          <div id="videoWrap" style="min-height:120px;">
            <div class="small" id="videoInfo">No video yet.</div>
            <video id="resultVideo" controls style="display:none;"></video>
            <div style="margin-top:6px;">
              <a id="downloadVideo" class="link" href="#">Download video</a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div style="margin-top:12px;" class="small card">
      <strong>Tips</strong>
      <ul>
        <li>Use short prompts first to test (<code>y = x^2</code>, <code>circle & tangent</code>).</li>
        <li>If Graphviz is not installed, the diagram will be skipped.</li>
        <li>To change backends or debug, inspect the Flask logs in the terminal.</li>
      </ul>
    </div>
  </div>

<script>
function autoResize(el){
  el.style.height = 'auto';
  el.style.height = (el.scrollHeight) + 'px';
}

document.getElementById('promptForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  if(!prompt){ alert('Please enter a prompt'); return; }

  // UI state
  document.getElementById('status').textContent = 'running';
  document.getElementById('generateBtn').disabled = true;
  document.getElementById('outputs').style.display = 'none';

  try {
    const resp = await fetch('/generate', {
      method: 'POST',
      headers:{ 'Content-Type':'application/json' },
      body: JSON.stringify({ prompt })
    });

    if(!resp.ok){
      const text = await resp.text();
      throw new Error(text || 'Server error');
    }
    const data = await resp.json();

    // Fill outputs
    document.getElementById('outputs').style.display = 'block';
    document.getElementById('codeBlock').textContent = data.code || 'No code';
    document.getElementById('graphJSON').textContent = JSON.stringify(data.scene_graph || {}, null, 2);
    document.getElementById('timelineJSON').textContent = JSON.stringify(data.timeline || {}, null, 2);

    // links
    document.getElementById('downloadCode').href = data.code_url || '#';
    document.getElementById('downloadGraph').href = data.scene_graph_url || '#';
    document.getElementById('downloadTimeline').href = data.timeline_url || '#';

    // diagram
    if(data.diagram_url){
      document.getElementById('diagramImg').src = data.diagram_url;
      document.getElementById('diagramImg').style.display = 'block';
      document.getElementById('diagramInfo').textContent = 'Diagram generated';
      document.getElementById('downloadDiagram').href = data.diagram_url;
    } else {
      document.getElementById('diagramImg').style.display = 'none';
      document.getElementById('diagramInfo').textContent = 'Diagram not available (Graphviz missing).';
      document.getElementById('downloadDiagram').href = '#';
    }

    // video
    if(data.video_url){
      const video = document.getElementById('resultVideo');
      video.src = data.video_url;
      video.style.display = 'block';
      document.getElementById('videoInfo').textContent = 'Rendered video:';
      document.getElementById('downloadVideo').href = data.video_url;
    } else {
      document.getElementById('resultVideo').style.display = 'none';
      document.getElementById('videoInfo').textContent = data.video_message || 'No video produced.';
      document.getElementById('downloadVideo').href = '#';
    }

  } catch(err){
    alert('Error: ' + err.message);
    console.error(err);
  } finally {
    document.getElementById('status').textContent = 'idle';
    document.getElementById('generateBtn').disabled = false;
  }
});

document.getElementById('clearBtn').addEventListener('click', ()=> {
  document.getElementById('prompt').value = '';
  autoResize(document.getElementById('prompt'));
});
</script>
</body>
</html>
"""

# Create template file (so that Flask's render_template_string works reliably across environments)
TEMPLATE_PATH = Path("templates")
TEMPLATE_PATH.mkdir(parents=True, exist_ok=True)
with open(TEMPLATE_PATH / "index.html", "w", encoding="utf-8") as f:
    f.write(INDEX_HTML)


def safe_relpath_for_send(path):
    # ensure path exists and is within project
    p = Path(path).resolve()
    base = Path.cwd().resolve()
    try:
        p.relative_to(base)
    except Exception:
        return None
    return str(p)


@app.route("/", methods=["GET"])
def index():
    return render_template_string(INDEX_HTML)


@app.route("/generate", methods=["POST"])
def generate():
    """
    Synchronous endpoint:
    - Calls your existing generate_and_render_animation(prompt)
    - After generation, reads generated_manim_animation.py
    - Extracts scene graph + timeline
    - Saves outputs to outputs/
    - Attempts to create diagram if visualizer available
    - Returns JSON with file URLs (served by Flask static)
    """
    data = request.get_json(force=True)
    prompt = data.get("prompt", "").strip()
    if not prompt:
        return jsonify({"error": "prompt required"}), 400

    # Run generation (this will run your backend pipeline)
    try:
        # The backend function prints logs; it also writes generated_manim_animation.py
        video_path = generate_and_render_animation(prompt)
    except Exception as e:
        return jsonify({"error": f"Backend generation failed: {e}"}), 500

    # Read generated code
    code_file = Path("generated_manim_animation.py")
    code_text = ""
    if code_file.exists():
        code_text = code_file.read_text(encoding="utf-8")
    else:
        code_text = "# generated_manim_animation.py not found."

    # Build scene graph from the generated code (re-run extractor)
    try:
        scene_graph = generate_scene_graph(code_text) or {}
        timeline = build_timeline(scene_graph.get("timeline", []))
        errors = validate_scene_graph(scene_graph)
    except Exception as e:
        scene_graph = {}
        timeline = []
        errors = [str(e)]

    # Save outputs
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)
    scene_graph_path = outputs_dir / "scene_graph.json"
    timeline_path = outputs_dir / "timeline.json"
    code_out_path = outputs_dir / "generated_manim_animation.py"

    try:
        scene_graph_path.write_text(json.dumps(scene_graph, indent=4), encoding="utf-8")
        timeline_path.write_text(json.dumps(timeline, indent=4), encoding="utf-8")
        code_out_path.write_text(code_text, encoding="utf-8")
    except Exception as e:
        return jsonify({"error": f"Failed to save outputs: {e}"}), 500

    # Attempt to visualize (if available)
    diagram_file = outputs_dir / "scene_graph.png"
    diagram_url = None
    if VISUALIZER_AVAILABLE:
        try:
            img_path = visualize_scene_graph(scene_graph, output_dir=str(outputs_dir))
            # visualize_scene_graph usually returns path like outputs/scene_graph.png
            if Path(img_path).exists():
                diagram_file = Path(img_path)
                diagram_url = "/outputs/" + diagram_file.name
        except Exception as e:
            # ignore visualization error; continue
            diagram_url = None

    # Video: if backend returned a video path, map it to a url if it exists inside project
    video_url = None
    video_message = ""
    if video_path:
        v = Path(video_path)
        if v.exists():
            # if video is inside media/videos/... we attempt to create a copy to outputs for simple serving
            dest = outputs_dir / v.name
            try:
                shutil.copy2(str(v), str(dest))
                video_url = "/outputs/" + dest.name
            except Exception:
                # fallback: if video path is accessible inside project root we attempt to serve it directly
                rel = safe_relpath_for_send(str(v))
                if rel:
                    video_url = "/" + rel.replace("\\", "/")
                else:
                    video_message = "Video was generated but cannot be served from this server."
        else:
            video_message = "Video path returned by backend but file not found."
    else:
        video_message = "Backend did not produce a video file."

    response = {
        "code": code_text,
        "code_url": "/outputs/" + code_out_path.name,
        "scene_graph": scene_graph,
        "scene_graph_url": "/outputs/" + scene_graph_path.name,
        "timeline": timeline,
        "timeline_url": "/outputs/" + timeline_path.name,
        "diagram_url": diagram_url,
        "video_url": video_url,
        "video_message": video_message,
        "validation_errors": errors
    }

    return jsonify(response), 200


# Serve files from outputs directory
@app.route("/outputs/<path:filename>", methods=["GET"])
def serve_outputs(filename):
    p = Path("outputs") / filename
    if not p.exists():
        abort(404)
    return send_from_directory("outputs", filename, as_attachment=False)


if __name__ == "__main__":
    print("Starting frontend server at http://127.0.0.1:5000 (no reloader)")
    # debug=False and use_reloader=False prevents the server from restarting automatically when files change.
    app.run(debug=False, use_reloader=False, port=5000)

