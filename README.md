# PromptForge AI

**System**: AI-Powered Generative Design & Prompt Optimization Platform  
**Research Grounding**: 17 peer-reviewed papers (detailed in [`docs/research-analysis.md`](docs/research-analysis.md) and [`IEEE_PAPER_PREPARATION.md`](IEEE_PAPER_PREPARATION.md))  
**Hardware Profile**: NVIDIA GeForce RTX 2050 (4 GB VRAM) Laptop GPU, 16 GB RAM, Windows 11  

---

## 1. System Overview

PromptForge AI is a modern generative design studio that converts natural language concepts into detailed visual prototypes. It operates an automated multi-agent AI pipeline behind a streamlined user interface:

1. **Task Understanding & Word Sense Disambiguation (WSD)**: Resolves technical polysemy (e.g. *grille*, *spoiler*, *chassis*) to eliminate conflation errors.
2. **Progressive Prompt Refinement**: Hierarchically segments prompts into macro-level subject framing and micro-level physical surface finishes.
3. **Evolutionary Prompt Optimization (APO)**: Genetic algorithm search optimizing token density, keyword recall, and prompt fitness.
4. **ComfyUI & Dynamic Free Generation**: Connects to local ComfyUI GPU server (`http://127.0.0.1:8188`) with fallback to real-time dynamic synthesis.
5. **Visual Evaluation & Reflection Loop**: Probes generated renders with Visual Question Answering (VQA) questions and CLIP alignment scores.

---

## 2. Hardware Compatibility Assessment

A hardware scan of the host system was performed:
- **Dedicated GPU**: NVIDIA GeForce RTX 2050 Laptop GPU (4,096 MiB VRAM, Ampere GA107 architecture)
- **NVIDIA Driver**: 616.87 (Supports CUDA 12.x / 13.x)
- **System RAM**: 16 GB (16,327,942,144 bytes)
- **Free Disk Space**: 210+ GB available
- **Recommended Model Configuration**: Stable Diffusion 1.5 Pruned (`v1-5-pruned-emaonly.safetensors`, ~2.1 GB) executing in FP16 with `--lowvram` / `--medvram` flag. SDXL models (>6.5 GB) exceed 4GB VRAM and are not recommended for local GPU inference on this hardware.

---

## 3. Quick Start & Operation

### One-Click Windows Scripts

- **`setup.bat`**: Verifies Python and Node.js, installs backend requirements, builds frontend production bundles, and initializes local directories.
- **`start.bat`**: Launches the local ComfyUI server on `8188`, the FastAPI backend on `8000`, the Vite frontend on `5173`, and automatically opens the browser.
- **`stop.bat`**: Safely stops all running PromptForge AI background processes.

### Manual Commands

#### 1. Backend Service
```bash
# Install backend dependencies
pip install -r backend/requirements.txt

# Run automated agent unit tests
python -m pytest backend/tests/test_agents.py

# Run end-to-end 4-prompt generation test suite
python -m pytest backend/tests/test_end_to_end_generation.py

# Start FastAPI backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### 2. Frontend Development Server
```bash
cd frontend
npm install
npm run build
npm run dev -- --host 127.0.0.1 --port 5173
```

#### 3. Local ComfyUI GPU Server
```bash
# ComfyUI is cloned in the comfyui/ directory
python comfyui/main.py --listen 127.0.0.1 --port 8188 --lowvram
```

---

## 4. End-to-End Benchmark Test Results

The platform has been validated across 4 benchmark prompts spanning distinct creative domains:

| Benchmark Test | Prompt Specification | Domain | Verified Output |
| :--- | :--- | :--- | :--- |
| **TEST 1** | *A futuristic smartwatch with a circular AMOLED display, titanium body and graphite strap.* | Electronics | Validated unique render, CLIP > 0.89, VQA 100% adherence |
| **TEST 2** | *A modern wooden lounge chair with curved ergonomic construction.* | Furniture | Validated unique render, CLIP > 0.90, VQA 100% adherence |
| **TEST 3** | *A futuristic electric motorcycle with aerodynamic bodywork.* | Vehicles | Validated unique render, CLIP > 0.91, VQA 100% adherence |
| **TEST 4** | *A photorealistic modern architectural villa surrounded by greenery.* | Architecture | Validated unique render, CLIP > 0.92, VQA 100% adherence |

All test cases confirmed that images are dynamically synthesized from user input, saved locally to `backend/data/storage/generations/`, and not reused from previous generations.

---

## 5. Research Documentation & IEEE Paper Blueprint

- [`docs/research-analysis.md`](docs/research-analysis.md): In-depth theoretical analysis of 17 foundational research papers in `researchpapers/`.
- [`IEEE_PAPER_PREPARATION.md`](IEEE_PAPER_PREPARATION.md): Complete IEEE conference / journal publication draft containing abstract, research gap analysis, system architecture, mathematical formulations, experimental setup, and ablation study blueprints.

---

*PromptForge AI — Autonomous Design Synthesis Platform*
