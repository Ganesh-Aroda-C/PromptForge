from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from backend.app.core.database import get_db
from backend.app.models.schemas import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    GeneratedImageItem
)
from backend.app.agents.image_generation import image_generation_agent
from backend.app.agents.visual_framework import visual_framework_agent

router = APIRouter(prefix="/generation", tags=["Image Generation"])

@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_images(request: ImageGenerationRequest):
    """
    Agent 5: Image Generation Agent
    Generates candidates and logs to database.
    """
    response = await image_generation_agent.generate(request)
    
    # Persist generations in database
    gen_coll = get_db("generations")
    for item in response.generations:
        await gen_coll.insert_one(item.model_dump())
        
    # If project_id is set, update project thumbnail if not set
    if request.project_id and response.generations:
        proj_coll = get_db("projects")
        await proj_coll.update_one(
            {"project_id": request.project_id, "thumbnail_url": None},
            {"$set": {"thumbnail_url": response.generations[0].thumbnail_url}}
        )
        
    return response

@router.post("/condition")
async def process_structural_conditioning(
    conditioning_type: str = Body(..., embed=True),
    image_data: str = Body(..., embed=True)
):
    """
    Agent 4: Visual Framework Agent
    Generates Canny edge, Scribble, or Depth map conditioning representations.
    """
    try:
        processed_data, metadata = visual_framework_agent.process_conditioning(conditioning_type, image_data)
        return {
            "success": True,
            "conditioning_type": conditioning_type,
            "processed_image": processed_data,
            "metadata": metadata
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process structural conditioning: {str(e)}")

@router.get("/history", response_model=List[GeneratedImageItem])
async def list_generation_history(project_id: Optional[str] = None, limit: int = 50):
    coll = get_db("generations")
    query = {"project_id": project_id} if project_id else {}
    results = await coll.find(query, sort=[("created_at", -1)], limit=limit)
    return results

@router.get("/{generation_id}", response_model=GeneratedImageItem)
async def get_generation_detail(generation_id: str):
    coll = get_db("generations")
    doc = await coll.find_one({"generation_id": generation_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Generation item not found")
    return doc
