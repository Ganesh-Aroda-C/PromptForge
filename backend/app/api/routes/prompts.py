import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.core.database import get_db
from backend.app.models.schemas import (
    TaskUnderstandingRequest,
    TaskUnderstandingResponse,
    PromptRefinementRequest,
    PromptRefinementResponse,
    EvolutionaryOptimizationRequest,
    EvolutionaryOptimizationResponse,
    PromptEnhancementRequest,
    PromptEnhancementResponse
)
from backend.app.agents.task_understanding import task_understanding_agent
from backend.app.agents.prompt_refinement import prompt_refinement_agent
from backend.app.agents.prompt_optimization import prompt_optimization_engine
from backend.app.agents.prompt_enhancer import prompt_enhancement_engine

router = APIRouter(prefix="/prompts", tags=["Prompts & AI Pipeline"])

@router.post("/enhance", response_model=PromptEnhancementResponse)
async def enhance_prompt(request: PromptEnhancementRequest):
    """
    Intelligent Prompt Enhancement Engine:
    Converts simple user descriptions into comprehensive, engineering-detailed
    positive prompts and tailored negative prompts for Stable Diffusion 1.5.
    """
    result = prompt_enhancement_engine.enhance(
        raw_prompt=request.prompt,
        style_preset_name=request.visual_style or "Photorealistic 3D",
        category_hint=request.category
    )
    return PromptEnhancementResponse(
        original_prompt=result.original_prompt,
        enhanced_positive_prompt=result.enhanced_positive_prompt,
        enhanced_negative_prompt=result.enhanced_negative_prompt,
        detected_subject=result.detected_subject,
        detected_domain=result.detected_domain,
        extracted_attributes=result.extracted_attributes,
        breakdown=result.breakdown,
        validation_report=result.validation_report.model_dump(),
        recommended_settings=result.recommended_settings
    )

@router.post("/understand", response_model=TaskUnderstandingResponse)
async def understand_task(request: TaskUnderstandingRequest):
    """
    Agent 1: Task Understanding Agent
    Extracts entities, detects lexical ambiguity, and outputs spatial constraints.
    """
    return task_understanding_agent.analyze(request)

@router.post("/refine", response_model=PromptRefinementResponse)
async def refine_prompt(request: PromptRefinementRequest):
    """
    Agent 2: Inspiration and Prompt Refinement Agent
    Generates high/low-level progressive prompts, negative prompts, and alternatives.
    """
    return prompt_refinement_agent.refine(request)

@router.post("/optimize", response_model=EvolutionaryOptimizationResponse)
async def optimize_prompt(request: EvolutionaryOptimizationRequest):
    """
    Agent 3: Evolutionary Prompt Optimization Engine
    Executes true population genetic search with selection, crossover, and mutation.
    """
    return prompt_optimization_engine.optimize(request)

@router.post("/save")
async def save_prompt(
    project_id: str,
    original_prompt: str,
    optimized_prompt: str,
    negative_prompt: Optional[str] = "",
    optimization_history: Optional[List] = None
):
    coll = get_db("prompts")
    prompt_id = f"prm-{uuid.uuid4().hex[:8]}"
    doc = {
        "prompt_id": prompt_id,
        "project_id": project_id,
        "original_prompt": original_prompt,
        "optimized_prompt": optimized_prompt,
        "negative_prompt": negative_prompt,
        "optimization_history": optimization_history or [],
        "created_at": datetime.utcnow().isoformat()
    }
    await coll.insert_one(doc)
    return {"success": True, "prompt_id": prompt_id, "message": "Prompt saved successfully"}

@router.get("")
async def list_prompts(project_id: Optional[str] = None):
    coll = get_db("prompts")
    query = {"project_id": project_id} if project_id else {}
    results = await coll.find(query, sort=[("created_at", -1)])
    return results
