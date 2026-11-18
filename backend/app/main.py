import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.core.config import settings
from backend.app.core.database import db_manager, get_db
from backend.app.api.routes import (
    projects,
    prompts,
    generation,
    evaluation,
    datasets,
    settings as settings_routes
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connection
    await db_manager.connect()
    
    # Pre-seed sample project & generations if empty
    proj_coll = get_db("projects")
    count = await proj_coll.count_documents({})
    if count == 0:
        sample_proj = {
            "project_id": "proj-default-01",
            "user_id": "default_user",
            "title": "AeroStrata Apex 1 - Electric Superbike",
            "description": "High-performance urban electric motorcycle visual prototyping using ControlNet structural conditioning and progressive prompt staging.",
            "category": "electric_motorcycle",
            "tags": ["electric", "motorcycle", "aerodynamics", "carbon_fiber"],
            "thumbnail_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=80",
            "created_at": "2026-11-17T09:00:00Z",
            "updated_at": "2026-11-17T09:00:00Z"
        }
        await proj_coll.insert_one(sample_proj)
        
        gen_coll = get_db("generations")
        sample_gen = {
            "generation_id": "gen-seed-01",
            "project_id": "proj-default-01",
            "image_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=80",
            "thumbnail_url": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=1200&q=80",
            "prompt": "high-end minimalist electric urban motorcycle, lightweight matte carbon fiber monocoque frame, hub-mounted brushless motor, integrated LED strip headlamp, premium Brembo hydraulic disc brakes, sleek aerodynamic stance, clean studio lighting on neutral gray backdrop, 8k resolution photorealistic 3D render",
            "negative_prompt": "exhaust pipe, fuel tank, combustion engine, chains, wires hanging, chrome scratches, blurry, distorted geometry, low poly, noisy background",
            "seed": 459102,
            "width": 768,
            "height": 768,
            "model_name": "Stable Diffusion XL + ControlNet",
            "provider": "demo",
            "clip_score": 0.884,
            "rank": 1,
            "created_at": "2026-11-17T09:05:00Z"
        }
        await gen_coll.insert_one(sample_gen)

    yield
    # Shutdown logic if any

app = FastAPI(
    title="PromptForge AI",
    description="Intelligent AI-powered design generation and prompt optimization platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads and generated local assets
generations_dir = os.path.join(settings.STORAGE_DIR, "generations")
os.makedirs(generations_dir, exist_ok=True)
app.mount("/api/static/generations", StaticFiles(directory=generations_dir), name="generations")

# Register API Routers
app.include_router(projects.router, prefix="/api")
app.include_router(prompts.router, prefix="/api")
app.include_router(generation.router, prefix="/api")
app.include_router(evaluation.router, prefix="/api")
app.include_router(datasets.router, prefix="/api")
app.include_router(settings_routes.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "database": "connected" if db_manager.is_mongodb_connected else "local_persistent_json",
        "mode": "live" if bool(settings.OPENAI_API_KEY or settings.GEMINI_API_KEY) else "demo"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
