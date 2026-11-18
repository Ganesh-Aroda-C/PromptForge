import uuid
import json
import csv
import io
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Response
from backend.app.core.database import get_db
from backend.app.models.schemas import (
    DatasetRecord,
    DatasetCreate,
    DatasetResponse
)

router = APIRouter(prefix="/datasets", tags=["Dataset Studio"])

# Research Benchmark Samples Pre-Loaded for Academic Exploration
BENCHMARK_DATASETS = [
    {
        "dataset_id": "ds-vlab-disambiguation",
        "name": "V-LAB Disambiguation Benchmark (Sample)",
        "description": "Lexically ambiguous prompts evaluating Word Sense Disambiguation and negative sense suppression in industrial T2I.",
        "source": "Ajou University (Na et al., 2024)",
        "task_category": "lexical_disambiguation",
        "records": [
            {
                "record_id": "VLAB-001",
                "task_type": "industrial_product_design",
                "product_category": "automotive",
                "input_prompt": "electric car with aggressive aerodynamic front grille",
                "optimized_prompt": "aerodynamic electric vehicle concept with active cooling front ventilation lattice fascia, stealth matte titanium finish, negative front splitter, studio lighting",
                "negative_prompt": "barbecue grill, cooking stove, charcoal, meat, food, low quality, warped mesh",
                "objects": ["electric car", "front ventilation lattice", "splitter"],
                "attributes": {"color": "stealth titanium", "finish": "matte"},
                "style": "photorealistic automotive render",
                "image_reference": "https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=800&q=80",
                "expected_constraints": ["no cooking barbecue elements", "clean automotive lattice"],
                "evaluation_metadata": {"wsd_accuracy": 1.0, "clip_score": 0.89}
            },
            {
                "record_id": "VLAB-002",
                "task_type": "industrial_product_design",
                "product_category": "consumer_electronics",
                "input_prompt": "ergonomic optical mouse with carbon fiber palm rest",
                "optimized_prompt": "precision gaming computer peripheral mouse, contoured carbon fiber palm grip, Omron micro-switches, illuminated RGB DPI indicator, 85mm macro studio capture",
                "negative_prompt": "rodent, animal, fur, tail, whiskers, organic mammal, deformed buttons",
                "objects": ["computer mouse", "carbon fiber palm rest", "scroll wheel"],
                "attributes": {"color": "matte black", "material": "carbon fiber"},
                "style": "clean product photography",
                "image_reference": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=800&q=80",
                "expected_constraints": ["strictly electronic device", "no biological rodent"],
                "evaluation_metadata": {"wsd_accuracy": 1.0, "clip_score": 0.92}
            }
        ]
    },
    {
        "dataset_id": "ds-idd-industrial-sketch",
        "name": "IDD Industrial Sketch-to-Design Benchmark",
        "description": "Pairs of structural hand-drawn sketches and photorealistic industrial product concepts (Yang et al. & Eswarawaka et al.).",
        "source": "Anhui Jianzhu Univ / RNSIT (2024)",
        "task_category": "sketch_to_image",
        "records": [
            {
                "record_id": "IDD-001",
                "task_type": "industrial_product_design",
                "product_category": "electric_mobility",
                "input_prompt": "electric cafe racer urban motorcycle with exposed battery pack",
                "optimized_prompt": "custom electric cafe racer motorcycle, trellis frame holding finned modular battery pack, round LED projector headlamp, inverted front forks, clip-on handlebars, studio cyclorama",
                "negative_prompt": "exhaust pipe, fuel tank, spark plugs, chains, messy wires, cartoon",
                "objects": ["motorcycle", "trellis frame", "finned battery", "projector headlamp"],
                "attributes": {"color": "gunmetal gray", "material": "anodized aluminum"},
                "style": "industrial prototype render",
                "image_reference": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&w=800&q=80",
                "expected_constraints": ["adherence to hand sketch lines", "no combustion motor"],
                "evaluation_metadata": {"structural_ssim": 0.88, "clip_score": 0.91}
            }
        ]
    },
    {
        "dataset_id": "ds-drawbench-hard-surface",
        "name": "DrawBench Hard-Surface & Product Subset",
        "description": "Complex compositional and multi-attribute prompts for industrial product evaluation.",
        "source": "Google Research / DrawBench Benchmark",
        "task_category": "compositional_evaluation",
        "records": [
            {
                "record_id": "DB-001",
                "task_type": "industrial_product_design",
                "product_category": "furniture",
                "input_prompt": "a minimalist lounge chair made of bent walnut plywood and cognac leather on a concrete floor",
                "optimized_prompt": "architectural lounge chair with steam-bent American walnut plywood structure, hand-stitched cognac leather cushions, matte black powder-coated swivel base, concrete loft interior",
                "negative_prompt": "plastic, cheap wood, oversaturated colors, crooked seams, cluttered room",
                "objects": ["lounge chair", "walnut shell", "leather cushions", "swivel base"],
                "attributes": {"wood": "walnut", "leather": "cognac", "base": "black metal"},
                "style": "high-end architectural catalog photography",
                "image_reference": "https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?auto=format&fit=crop&w=800&q=80",
                "expected_constraints": ["correct material binding: walnut structure + cognac leather"],
                "evaluation_metadata": {"attribute_binding_accuracy": 0.96, "clip_score": 0.93}
            }
        ]
    }
]

@router.get("", response_model=List[DatasetResponse])
async def list_datasets():
    coll = get_db("datasets")
    docs = await coll.find({}, sort=[("created_at", -1)])
    
    # Auto-seed benchmark datasets if empty
    if not docs:
        for b_data in BENCHMARK_DATASETS:
            b_copy = dict(b_data)
            b_copy["created_at"] = datetime.utcnow().isoformat()
            await coll.insert_one(b_copy)
        docs = await coll.find({}, sort=[("created_at", -1)])

    response = []
    for d in docs:
        response.append(DatasetResponse(
            dataset_id=d.get("dataset_id"),
            name=d.get("name", "Untitled Dataset"),
            description=d.get("description", ""),
            source=d.get("source", "custom"),
            task_category=d.get("task_category", "industrial_design"),
            record_count=len(d.get("records", [])),
            created_at=d.get("created_at", datetime.utcnow().isoformat()),
            updated_at=d.get("updated_at")
        ))
    return response

@router.get("/{dataset_id}")
async def get_dataset(dataset_id: str):
    coll = get_db("datasets")
    doc = await coll.find_one({"dataset_id": dataset_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return doc

@router.post("/create", response_model=DatasetResponse)
async def create_dataset(data: DatasetCreate):
    coll = get_db("datasets")
    d_id = f"ds-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()
    
    doc = {
        "dataset_id": d_id,
        "name": data.name,
        "description": data.description,
        "source": data.source,
        "task_category": data.task_category,
        "records": [r.model_dump() for r in data.records],
        "created_at": now,
        "updated_at": now
    }
    await coll.insert_one(doc)
    return DatasetResponse(
        dataset_id=d_id,
        name=data.name,
        description=data.description,
        source=data.source,
        task_category=data.task_category,
        record_count=len(data.records),
        created_at=now,
        updated_at=now
    )

@router.post("/{dataset_id}/records")
async def add_dataset_record(dataset_id: str, record: DatasetRecord):
    coll = get_db("datasets")
    doc = await coll.find_one({"dataset_id": dataset_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    records = doc.get("records", [])
    records.append(record.model_dump())
    await coll.update_one(
        {"dataset_id": dataset_id},
        {"$set": {"records": records, "updated_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "record_count": len(records), "message": "Record added"}

@router.delete("/{dataset_id}/records/{record_id}")
async def delete_dataset_record(dataset_id: str, record_id: str):
    coll = get_db("datasets")
    doc = await coll.find_one({"dataset_id": dataset_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    records = [r for r in doc.get("records", []) if r.get("record_id") != record_id]
    await coll.update_one(
        {"dataset_id": dataset_id},
        {"$set": {"records": records, "updated_at": datetime.utcnow().isoformat()}}
    )
    return {"success": True, "record_count": len(records), "message": "Record deleted"}

@router.delete("/{dataset_id}")
async def delete_dataset(dataset_id: str):
    coll = get_db("datasets")
    res = await coll.delete_one({"dataset_id": dataset_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"success": True, "message": f"Dataset {dataset_id} deleted"}

@router.get("/{dataset_id}/export")
async def export_dataset(dataset_id: str, format: str = "json"):
    coll = get_db("datasets")
    doc = await coll.find_one({"dataset_id": dataset_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Dataset not found")
        
    records = doc.get("records", [])
    
    if format == "csv":
        output = io.StringIO()
        fieldnames = ["record_id", "task_type", "product_category", "input_prompt", "optimized_prompt", "negative_prompt", "style"]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={dataset_id}.csv"}
        )
    else:
        return Response(
            content=json.dumps(records, indent=2),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={dataset_id}.json"}
        )
