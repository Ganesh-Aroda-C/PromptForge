import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.app.core.database import get_db
from backend.app.models.schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def list_projects(category: Optional[str] = None):
    coll = get_db("projects")
    query = {"category": category} if category else {}
    results = await coll.find(query, sort=[("created_at", -1)])
    
    # Calculate counts dynamically
    gen_coll = get_db("generations")
    prompt_coll = get_db("prompts")
    
    response = []
    for doc in results:
        p_id = doc.get("project_id")
        gen_count = await gen_coll.count_documents({"project_id": p_id})
        pr_count = await prompt_coll.count_documents({"project_id": p_id})
        
        response.append(ProjectResponse(
            project_id=p_id,
            user_id=doc.get("user_id", "default_user"),
            title=doc.get("title", "Untitled Project"),
            description=doc.get("description", ""),
            category=doc.get("category", "industrial_design"),
            tags=doc.get("tags", []),
            generations_count=gen_count,
            prompts_count=pr_count,
            thumbnail_url=doc.get("thumbnail_url"),
            created_at=doc.get("created_at", datetime.utcnow().isoformat()),
            updated_at=doc.get("updated_at")
        ))
    return response

@router.post("", response_model=ProjectResponse)
async def create_project(data: ProjectCreate):
    coll = get_db("projects")
    p_id = f"proj-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()
    
    doc = {
        "project_id": p_id,
        "user_id": "default_user",
        "title": data.title,
        "description": data.description or "",
        "category": data.category,
        "tags": data.tags,
        "thumbnail_url": None,
        "created_at": now,
        "updated_at": now
    }
    await coll.insert_one(doc)
    return ProjectResponse(
        project_id=p_id,
        user_id="default_user",
        title=data.title,
        description=data.description or "",
        category=data.category,
        tags=data.tags,
        generations_count=0,
        prompts_count=0,
        thumbnail_url=None,
        created_at=now,
        updated_at=now
    )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str):
    coll = get_db("projects")
    doc = await coll.find_one({"project_id": project_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
        
    gen_coll = get_db("generations")
    prompt_coll = get_db("prompts")
    gen_count = await gen_coll.count_documents({"project_id": project_id})
    pr_count = await prompt_coll.count_documents({"project_id": project_id})
    
    return ProjectResponse(
        project_id=project_id,
        user_id=doc.get("user_id", "default_user"),
        title=doc.get("title", ""),
        description=doc.get("description", ""),
        category=doc.get("category", "industrial_design"),
        tags=doc.get("tags", []),
        generations_count=gen_count,
        prompts_count=pr_count,
        thumbnail_url=doc.get("thumbnail_url"),
        created_at=doc.get("created_at", ""),
        updated_at=doc.get("updated_at")
    )

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectUpdate):
    coll = get_db("projects")
    doc = await coll.find_one({"project_id": project_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Project not found")
        
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow().isoformat()
    await coll.update_one({"project_id": project_id}, {"$set": update_data})
    
    updated_doc = await coll.find_one({"project_id": project_id})
    gen_coll = get_db("generations")
    prompt_coll = get_db("prompts")
    gen_count = await gen_coll.count_documents({"project_id": project_id})
    pr_count = await prompt_coll.count_documents({"project_id": project_id})
    
    return ProjectResponse(
        project_id=project_id,
        user_id=updated_doc.get("user_id", "default_user"),
        title=updated_doc.get("title", ""),
        description=updated_doc.get("description", ""),
        category=updated_doc.get("category", "industrial_design"),
        tags=updated_doc.get("tags", []),
        generations_count=gen_count,
        prompts_count=pr_count,
        thumbnail_url=updated_doc.get("thumbnail_url"),
        created_at=updated_doc.get("created_at", ""),
        updated_at=updated_doc.get("updated_at")
    )

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    coll = get_db("projects")
    res = await coll.delete_one({"project_id": project_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"success": True, "message": f"Project {project_id} deleted successfully"}
