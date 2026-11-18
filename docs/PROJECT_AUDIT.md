# PromptForge AI: Complete Codebase Audit, Architecture Review & Repair Plan

**Date**: 2026-11-18  
**Auditor**: Senior Full-Stack & AI Systems Architect  
**Hardware Target**: Windows 11, NVIDIA GeForce RTX 2050 Laptop GPU (4 GB VRAM, GA107 Ampere), 16 GB RAM  
**Project Base**: Existing PromptForge AI Repository (`https://github.com/Ganesh-Aroda-C/PromptForge`)

---

## 1. Executive Summary & Audit Scope

This audit provides a comprehensive, ground-truth inspection of the PromptForge AI codebase, runtime dependencies, hardware configuration, neural pipeline, vector synthesis engine, and frontend-backend architecture.

No feature has been assumed functional simply because it was documented. Every claim in the existing documentation (`README.md`, `IEEE_PAPER_PREPARATION.md`, `docs/research-analysis.md`) has been cross-referenced with the actual source code, unit tests, and runtime behavior.

---

## 2. Hardware & Installation Environment Audit

A thorough runtime scan of the host environment was conducted:

| Component | Detected Specification | Verification Status | Operational Implication |
| :--- | :--- | :--- | :--- |
| **Operating System** | Windows 11 Home 64-bit | Verified via PowerShell host | Standard Win32 paths, `.bat` script runner |
| **CPU / System RAM** | 16 GB Physical RAM (16,328 MB) | Verified | Sufficient for running backend, ComfyUI, and browser concurrently |
| **Dedicated GPU** | NVIDIA GeForce RTX 2050 Laptop GPU | Verified via `torch.cuda.get_device_name(0)` | 4,096 MB dedicated VRAM (Ampere GA107 architecture) |
| **NVIDIA Driver / CUDA** | CUDA 12.4 runtime supported | Verified (`torch.cuda.is_available() == True`) | Native GPU tensor acceleration enabled |
| **Python Environment** | Python 3.11.9 (`v3.11.9:de54cf5`) | Verified in PATH | Fully compatible with PyTorch 2.6.0+cu124 |
| **PyTorch & CUDA Build** | PyTorch 2.6.0+cu124 | Verified | Native CUDA tensor execution confirmed on Device 0 |
| **Model Weights** | `v1-5-pruned-emaonly.safetensors` (4.26 GB) | Verified at `comfyui/models/checkpoints/` | Pre-downloaded, zero download required |
| **ComfyUI Installation** | Complete ComfyUI repo in `comfyui/` | Verified (`import comfy` executes cleanly) | Ready for local execution with `--lowvram` flag |
| **Node.js & npm** | Node.js v18+ & npm in PATH | Verified (`npm run build` succeeds in 1.72s) | Frontend build system fully functional |
| **Python Packages** | FastAPI, uvicorn, pydantic, Pillow, numpy, scikit-learn, motor, pymongo, requests, torchvision, transformers | Verified installed in active environment | Zero new package installations required |

### Strict Preservation Guarantee:
- No existing virtual environments will be deleted or overridden.
- No model checkpoints will be re-downloaded (4.26 GB SD 1.5 weights are preserved).
- Low-VRAM optimizations (`--lowvram`, FP16, 512x512 latent dimensions) must be strictly enforced to prevent OOM errors on the 4 GB RTX 2050.

---

## 3. Codebase Structure & Architecture Inspection

```
PromptForge/
├── backend/
│   ├── .env & .env.example       # Backend environment configuration
│   ├── requirements.txt          # Python requirements
│   ├── app/
│   │   ├── main.py               # FastAPI entry point, CORS, static mounts
│   │   ├── core/
│   │   │   ├── config.py         # Settings & paths
│   │   │   └── database.py       # Motor MongoDB + Local persistent JSON fallback
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic v2 domain schemas
│   │   ├── services/
│   │   │   └── comfyui_service.py # REST API client for local ComfyUI (8188)
│   │   ├── agents/
│   │   │   ├── task_understanding.py  # Agent 1: Polysemy disambiguation & entity extraction
│   │   │   ├── prompt_refinement.py   # Agent 2: Macro/micro prompt structuring
│   │   │   ├── prompt_optimization.py # Agent 3: Genetic evolutionary prompt search
│   │   │   ├── visual_framework.py    # Agent 4: Edge/scribble/depth conditioning
│   │   │   ├── image_generation.py    # Agent 5: Vector + ComfyUI dispatch
│   │   │   └── image_evaluation.py    # Agent 6: VQA & semantic reflection
│   │   └── api/routes/
│   │       ├── projects.py       # CRUD for user projects
│   │       ├── prompts.py        # Endpoints for Agents 1, 2, 3
│   │       ├── generation.py     # Endpoints for Agent 4 & 5
│   │       ├── evaluation.py     # Endpoints for Agent 6
│   │       ├── datasets.py       # Benchmark prompt datasets
│   │       └── settings.py       # System health & hardware probe
│   ├── data/storage/             # Persistent JSON & generated PNG outputs
│   └── tests/
│       ├── test_agents.py        # Unit tests for agents
│       └── test_end_to_end_generation.py # E2E generation tests
├── comfyui/                      # Local ComfyUI engine with SD 1.5 weights
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # App routing and layout
│   │   ├── components/           # Sidebar, TopNav, ImageModal
│   │   ├── pages/                # Explore, CreateStudio, Projects, Settings, etc.
│   │   └── services/api.ts       # Axios API client
│   └── package.json              # React 18, Vite, TailwindCSS, Lucide
├── Reasearchpapers/ (symlink: researchpapers/) # 17 foundational research papers (PDFs)
├── docs/
│   └── research-analysis.md      # Methodological mapping of all 17 papers
├── IEEE_PAPER_PREPARATION.md     # IEEE manuscript draft
├── setup.bat                     # Installation & initialization script
├── start.bat                     # Multi-service Windows launch script
└── stop.bat                      # Graceful process termination script
```

---

## 4. Identified Bugs, Deficiencies & Root Causes

### Bug 1: Smartwatch Prompt Generated an Unrelated Image
- **Root Cause**:
  1. In `image_generation.py`, when ComfyUI was not responding or took longer than expected, the system silently invoked `_generate_dynamic_free_image()` which targeted external unauthenticated endpoints (`image.pollinations.ai`), which frequently rate-limited or timed out, triggering `_render_local_procedural_design()` with simplistic fallback drawings.
  2. In `prompt_optimization.py`, the mutation operator injected `engineering_modifiers` (`"aerodynamic NACA duct profiling"`, `"exposed carbon fiber monocoque weave"`, `"recessed stainless steel hex fasteners"`) regardless of whether the prompt was an electronics item, nature scene, or furniture piece, polluting the diffusion cross-attention maps and generating automotive/chassis elements instead of a smartwatch.

### Bug 2: Circle Prompt Generated Unrelated Textures and Objects
- **Root Cause**:
  1. In `task_understanding.py`, geometric requests were only recognized if exact single words appeared without attributes; compound geometry with sub-elements (e.g. `"A solid red circle with a small black dot exactly at its center on a pure white background"`) failed to parse the nested dot element.
  2. In `image_generation.py::_render_pure_vector_graphic()`, only a single outer primitive was drawn. The nested `"small black dot exactly at its center"` was completely ignored by the drawer!
  3. When passed to Stable Diffusion instead of the vector engine, diffusion models naturally add lighting spheres, room backgrounds, and textures unless strictly constrained by negative prompts and vector routing.

### Bug 3: Vector Generation Attempt Produced Blank White Images
- **Root Cause**:
  1. There was no real SVG generator: the code only used PIL to rasterize hardcoded primitives. When white background and default or mismatched color variables collided, or when dimension bounds failed, it produced a blank white canvas.
  2. There was zero SVG markup generation (`<svg ...><circle ...></svg>`), no SVG XML validation, no viewBox validation, and no proper SVG-to-PNG rendering pipeline.
  3. No validation check existed before saving to verify that pixels were drawn, resulting in blank images being saved and returned as "successful".

### Bug 4: Fabricated / Hardcoded Evaluation Metrics in Code
- **Root Cause**:
  1. In `image_generation.py`:
     ```python
     clip_score = 0.98 if is_geometric else round(random.uniform(0.89, 0.95), 3)
     ```
     CLIP scores were randomly generated numbers rather than actual computed metrics.
  2. In `image_evaluation.py`:
     VQA answers and probe alignment were hardcoded to return `"yes"` and `"stealth black"` / `"aluminum / carbon fiber"` for all requests regardless of the actual image or prompt content.
  3. In `README.md`, lines 79-82 claimed "CLIP > 0.89, VQA 100% adherence" for benchmark tests without empirical execution logs.
  - **Resolution**: Replace simulated values with honest heuristic/feature-based or CLIP-based evaluators where supported, clearly distinguishing actual measurements from placeholders, and strictly obeying the prompt's instruction: *"Never invent experimental data, accuracy, CLIP scores, VQA scores or performance improvements."*

### Bug 5: Backend Test Failures
- Running `pytest backend/tests/` revealed 3 out of 5 tests failing:
  - `test_task_understanding_agent`: Assertion mismatch (`'automotive_design' != 'industrial_product_design'`).
  - `test_prompt_refinement_agent`: Expected 3 alternatives, got 2.
  - `test_end_to_end_generation`: Category mismatch (`'vehicle' != 'electric_motorcycle'`) and network timeout on unmocked image retrieval.

### Bug 6: Windows Startup & Process Lifecycle Issues
- In `start.bat`:
  - `ping 127.0.0.1 -n 3` was used as an arbitrary blind timer without checking if ports 8188, 8000, or 5173 were actually listening.
  - If ComfyUI took 15 seconds to load weights, the browser opened to a blank or error screen.
  - `stop.bat` used blunt `taskkill /f /im cmd.exe` patterns which could kill unrelated command windows.

---

## 5. Architectural Repair Plan

### Phase 2: Fix Critical Backend & Frontend Integration
1. Standardize category definitions across schemas, frontend dropdowns, and agent analyzers (`consumer_electronics`, `furniture`, `vehicle`, `landscape_nature`, `architecture`, `geometric_shape`, `general_concept`).
2. Fix backend test assertions in `test_agents.py` and `test_end_to_end_generation.py`.
3. Ensure all API error responses return clear JSON structures with actionable details.

### Phase 3: Fix Prompt Understanding & Image Generation Pipeline
1. **Task Understanding Agent (`task_understanding.py`)**:
   - Accurately extract subjects, primary objects, child objects (e.g. "black dot" inside "red circle"), counts, colors, materials, background specifications, and spatial relations.
   - Disambiguate technical terms without turning non-industrial requests into machines.
   - Retain the raw user prompt intact alongside optimized prompts.
2. **Prompt Refinement Agent (`prompt_refinement.py`)**:
   - Progressive prompt structuring: Macro-level framing + Micro-level surface/lighting.
   - Context-aware negative prompt synthesis preventing attribute bleeding, duplicate objects, and hallucinated objects.
   - Respect user category and visual style preferences.
3. **Evolutionary Optimization Engine (`prompt_optimization.py`)**:
   - Domain-sensitive mutations: only apply automotive modifiers to vehicles, electronics modifiers to gadgets, natural modifiers to landscapes, etc.
   - Multi-metric fitness scoring respecting semantic preservation, clarity, and structural coherence.
4. **ComfyUI Service & Generation Agent (`comfyui_service.py`, `image_generation.py`)**:
   - Robust local ComfyUI API communication (queue prompt, monitor history, fetch output image).
   - Dynamic prompt construction using checkpoint `v1-5-pruned-emaonly.safetensors` on 4GB VRAM with FP16 and `--lowvram`.
   - Distinct random seeds for generating two genuinely different candidate images.
   - Resilient local offline synthesis when ComfyUI is unavailable, ensuring high semantic fidelity without external network flakiness.

### Phase 4: Precision Vector / SVG Engine Implementation
1. True SVG markup generation supporting:
   - Circles (single and nested concentric / offset circles, e.g. dot in circle)
   - Squares and rectangles
   - Triangles and polygons
   - Basic geometric diagrams with labeled attributes
   - Simple icons with clean geometric paths
2. Validated SVG generation: viewBox, xmlns, width, height, fill, stroke, stroke-width.
3. SVG to PNG rasterization with high-quality anti-aliasing via Pillow/Cairo/resizing.
4. Validation check ensuring rasterized PNG is not blank/monochrome before returning.
5. Save both `.svg` and `.png` assets in `backend/data/storage/generations/`.

### Phase 5: Honest Research-Grounded Evaluation & Feedback Loop
1. Implement genuine image-prompt evaluation:
   - Existence check: detects pixel presence of specified colors and contours.
   - Color alignment: analyzes histogram/dominant RGB clusters vs requested colors.
   - Background validation: verifies background brightness/color matches prompt specification.
   - Multi-probe VQA decomposition based on Bhowmik et al. (2026).
2. Report actual computed metrics honestly (no fabricated scores).
3. Provide constructive corrective prompts based on detected discrepancies.

### Phase 6: End-to-End Real Testing
1. Execute the 6 required benchmark tests:
   - TEST 1: Red circle with small black dot at center on white background.
   - TEST 2: Blue square centered on plain white background.
   - TEST 3: Futuristic smartwatch with circular AMOLED display, brushed titanium frame, dark graphite strap.
   - TEST 4: Minimalist wooden lounge chair with curved ergonomic construction.
   - TEST 5: Realistic mountain landscape at sunset with lake in foreground.
   - TEST 6: Modern electric motorcycle with aerodynamic bodywork and realistic proportions.
2. Inspect and document actual generated images in `docs/TEST_RESULTS.md`.

### Phase 7: Polish UI, Startup Scripts & IEEE Preparation
1. Verify Create Studio, Explore, My Projects, Settings pages.
2. Verify debug panel display of original and optimized prompts.
3. Refine `start.bat`, `stop.bat`, `setup.bat` with proper port readiness polling.
4. Finalize `IEEE_PAPER_PREPARATION.md` with transparent distinction between implemented methods and future experimental benchmarks.
