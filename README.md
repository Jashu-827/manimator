# Manimator — Manim animation generator

Lightweigh project that generates Manim animations from short prompts using an LLM backend, renders them with Manim, and extracts a scene graph + timeline for inspection.

**Repository Contents**
- **`backend.py`**: Core pipeline. Sends prompt to the LLM, writes `generated_manim_animation.py`, renders with Manim, and returns the produced video path.
- **`frontend_app.py`**: Minimal Flask frontend to drive generation, display generated code, scene graph, timeline, diagram, and rendered video.
- **`generated_manim_animation.py`**: Example/generated Manim script produced by the backend.
- **`scene_graph/`**: Utilities to extract, validate, build, and visualize a simple scene graph from generated Manim code.
- **`requirements.txt`**: Python packages required to run the project.

**Prerequisites**
- Python 3.10+ (or the version you normally use with Manim)
- `git` (optional)
- Manim Community Edition installed and available on PATH (see notes)
- (Optional) Graphviz for scene graph visualization

**Quick setup (Windows PowerShell)**
1. Create and activate a virtual environment (recommended):

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
```

2. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI / OpenRouter API key (used by the backend):

```
open_api_key=your_api_key_here
```

Notes:
- If you use the official OpenAI package, ensure the key name and usage in `backend.py` match your provider.
- If you plan to use Graphviz to generate diagrams, install Graphviz from https://graphviz.org/download/ and ensure `dot` is on your PATH.

**Running the project**

- Run the backend script directly (CLI):

```powershell
python backend.py
```

- Run the Flask frontend (opens server at `http://127.0.0.1:5000`):

```powershell
python frontend_app.py
```

Use the frontend to enter a short prompt (e.g., `show y = x^2 and explain vertex shift`) — the backend will generate Manim code, attempt to render it, and return the produced artifacts.

**Outputs**
- Generated artifacts are written to `outputs/` (code, scene_graph.json, timeline.json, optional diagram, and copied video files when available).
- Manim rendering outputs are written to `media/` by default (Manim's own media directory). The backend copies or references produced MP4 files for the frontend to serve.

**Troubleshooting**
- If rendering fails: check that `manim` is on your PATH and runnable from the activated virtual environment. Try a simple Manim example to verify installation.
- If Graphviz visualization fails: ensure Graphviz is installed and `dot` is in PATH; otherwise the project will skip diagram generation.
- If LLM requests fail: ensure `open_api_key` is set in `.env` and network access to your chosen LLM endpoint is allowed.

**Extending**
- You can replace the LLM client in `backend.py` (currently using `requests` to call OpenRouter) with your preferred integration.
- Improve `scene_graph` extractors for more complete Manim command coverage.


