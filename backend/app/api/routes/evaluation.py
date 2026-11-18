from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.core.database import get_db
from backend.app.models.schemas import (
    ImageEvaluationRequest,
    ImageEvaluationResponse,
    ClosedLoopRefinementRequest,
    ClosedLoopRefinementResponse
)
from backend.app.agents.image_evaluation import visual_evaluation_agent

router = APIRouter(prefix="/evaluation", tags=["Evaluation & Reflection"])

@router.post("/evaluate", response_model=ImageEvaluationResponse)
async def evaluate_image(request: ImageEvaluationRequest):
    """
    Agent 6: Visual Evaluation and Reflection Agent
    Computes CLIP score, VQA probe question verification, and corrective recommendations.
    """
    response = visual_evaluation_agent.evaluate(request)
    
    # Store evaluation record
    eval_coll = get_db("evaluations")
    await eval_coll.insert_one(response.model_dump())
    
    return response

@router.post("/refine-loop", response_model=ClosedLoopRefinementResponse)
async def refine_closed_loop(request: ClosedLoopRefinementRequest):
    """
    Closed-loop iterative self-correction step (VQA-Guided Diffusion).
    Generate -> Evaluate -> Identify Errors -> Refine Prompt -> Regenerate -> Compare.
    """
    return visual_evaluation_agent.refine_closed_loop(request)

@router.get("/history", response_model=List[ImageEvaluationResponse])
async def list_evaluation_history(generation_id: Optional[str] = None, limit: int = 50):
    coll = get_db("evaluations")
    query = {"generation_id": generation_id} if generation_id else {}
    results = await coll.find(query, sort=[("created_at", -1)], limit=limit)
    return results
