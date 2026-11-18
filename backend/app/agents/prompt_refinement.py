import re
from typing import List, Dict, Any, Optional
from backend.app.models.schemas import (
    PromptRefinementRequest,
    PromptRefinementResponse,
    PromptAlternative,
    TaskUnderstandingResponse
)
from backend.app.agents.task_understanding import task_understanding_agent, TaskUnderstandingRequest

class PromptRefinementAgent:
    """
    Agent 2: Inspiration and Prompt Refinement Agent
    Hierarchically organizes Macro (subject/form/environment) and Micro (materials/textures/lighting).
    Strictly preserves the user's requested subject, shape, color, background, and object count.
    Never injects automotive, interior, or industrial boilerplate into unrelated concepts.
    """
    def __init__(self):
        pass

    def refine(self, request: PromptRefinementRequest) -> PromptRefinementResponse:
        tu = request.task_understanding
        if not tu:
            tu = task_understanding_agent.analyze(
                TaskUnderstandingRequest(prompt=request.original_prompt, category=request.category)
            )

        orig = request.original_prompt.strip()
        orig_lower = orig.lower()
        cat = tu.product_category
        subject = tu.primary_subject

        # Determine colors and background cues
        color_str = ", ".join(tu.colors) if tu.colors and tu.colors != ["natural tones"] else ""
        bg_cue = "plain solid white background"
        if "black background" in orig_lower:
            bg_cue = "plain solid black background"
        elif "white background" in orig_lower:
            bg_cue = "plain solid white background"
        elif "neutral background" in orig_lower:
            bg_cue = "clean neutral background"

        # 1. Geometric & Simple Shape Refinement
        if cat == "geometric_shape":
            high_level = f"A simple flat {subject}, centered in frame, {bg_cue}"
            low_level = "solid color fill, razor sharp edges, 2D graphic design, minimal vector icon style, high clarity"
            full_positive = f"A simple flat {subject}, solid color fill, centered in frame, sharp geometric edges, {bg_cue}, 2d flat graphic, minimal vector aesthetic, high clarity, clean composition, isolated single shape, no other objects"
            negative_prompt = "furniture, lamps, ceiling lights, room, interior, desk, table, people, 3d render, sphere, ball, orb, cylinder, box, shadows, gradients, textures, multiple objects, clutter, complex background, text, watermark, blurry"

            alternatives = [
                PromptAlternative(
                    title="Minimal 2D Graphic",
                    positive_prompt=full_positive,
                    description="Clean 2D vector flat representation with razor sharp edges on plain background."
                ),
                PromptAlternative(
                    title="Pure Geometric Silhouette",
                    positive_prompt=f"Centered single {subject}, pure solid color, crisp edges, {bg_cue}, graphic icon style, high contrast, zero shadows, no other objects",
                    description="High-contrast isolated geometric silhouette."
                )
            ]

        # 2. Nature & Landscape Refinement
        elif cat == "landscape_nature":
            high_level = f"A scenic landscape photograph of {subject}"
            low_level = f"{tu.lighting}, natural environmental details, atmospheric depth, rich vibrant natural tones, 8k resolution, crisp focus"
            full_positive = f"A breathtaking scenic landscape photograph of {subject}, {tu.lighting}, natural landscape elements, atmospheric depth, rich natural colors, wide angle panoramic shot, 8k resolution, highly detailed"
            negative_prompt = "furniture, lamps, interior, room, cars, vehicles, people, buildings, indoor, clutter, distorted, blurry, low quality, watermark, text"

            alternatives = [
                PromptAlternative(
                    title="High-Resolution Landscape",
                    positive_prompt=full_positive,
                    description="Vibrant panoramic natural landscape with atmospheric sunlight."
                ),
                PromptAlternative(
                    title="Cinematic Golden Hour",
                    positive_prompt=f"Cinematic wide-angle nature photography of {subject}, dramatic atmospheric lighting, natural horizon, Hasselblad clarity, 8k resolution",
                    description="Atmospheric cinematic treatment emphasizing natural environmental light."
                )
            ]

        # 3. Furniture Refinement
        elif cat == "furniture":
            high_level = f"A single standalone {subject}, centered in frame"
            materials_str = ", ".join(tu.materials)
            low_level = f"crafted {materials_str}, clean neutral studio background, soft floor contact shadow, professional furniture product photography, 8k resolution"
            full_positive = f"A standalone single {subject}, centered in frame, clean neutral studio background, soft ground contact shadow, crafted {materials_str}, high resolution studio photograph, detailed craftsmanship, no surrounding clutter"
            negative_prompt = "multiple chairs, multiple furniture pieces, table, lamps, ceiling lights, room clutter, people, distorted legs, crooked seams, blurry, low resolution, watermark, text"

            alternatives = [
                PromptAlternative(
                    title="Studio Hero Shot",
                    positive_prompt=full_positive,
                    description="Clean standalone furniture piece against neutral studio background."
                ),
                PromptAlternative(
                    title="Architectural Minimalist",
                    positive_prompt=f"Architectural minimalist studio concept of single {subject}, neutral cyclorama background, soft overcast diffused light, immaculate finish",
                    description="Clean, stripped-down visual focus with honest materials."
                )
            ]

        # 4. Consumer Electronics Refinement
        elif cat == "consumer_electronics":
            high_level = f"A modern standalone {subject}, centered hero macro shot"
            materials_str = ", ".join(tu.materials)
            low_level = f"precision {materials_str}, calibrated studio product lighting, clean minimal background, crisp details, 8k resolution"
            full_positive = f"A modern standalone {subject}, centered hero macro product photography, clean minimal studio backdrop, calibrated rim lighting, {materials_str}, high resolution, crisp industrial design details, zero clutter"
            negative_prompt = "hands, person, room clutter, lamps, furniture, multiple devices, blurry, low resolution, distorted, watermark, text"

            alternatives = [
                PromptAlternative(
                    title="Macro Product Hero",
                    positive_prompt=full_positive,
                    description="Precision macro product view highlighting materials and display clarity."
                ),
                PromptAlternative(
                    title="Clean Minimalist Studio",
                    positive_prompt=f"Ultra-clean minimalist studio photograph of {subject}, soft diffused light, neutral infinity background, impeccable finish",
                    description="Neutral studio focus emphasizing industrial design form."
                )
            ]

        # 5. Vehicle Refinement
        elif cat == "vehicle":
            high_level = f"A high-performance standalone {subject}, three-quarter angle hero view"
            materials_str = ", ".join(tu.materials)
            low_level = f"aerodynamic bodywork, {materials_str}, commercial automotive studio lighting, neutral background, 8k render"
            full_positive = f"A single standalone {subject}, three-quarter angle hero view, clean neutral automotive studio background, commercial automotive studio lighting, aerodynamic stance, crisp focus, 8k render, zero other vehicles"
            negative_prompt = "multiple vehicles, interior room, furniture, lamps, room clutter, distorted wheels, blurry, watermark, text"

            alternatives = [
                PromptAlternative(
                    title="Automotive Studio Hero",
                    positive_prompt=full_positive,
                    description="Automotive studio lighting with aerodynamic surface reflections."
                ),
                PromptAlternative(
                    title="Cinematic Track Stance",
                    positive_prompt=f"Cinematic automotive capture of single {subject}, clean asphalt surface, dramatic rim light, 8k resolution, crisp focus",
                    description="Dramatic commercial capture with crisp body lines."
                )
            ]

        # 6. Architecture & General Concept Refinement
        elif cat == "architecture":
            high_level = f"An architectural perspective of {subject}"
            low_level = f"{tu.lighting}, {', '.join(tu.materials)}, natural landscaping integration, 8k architectural render"
            full_positive = f"An architectural perspective of {subject}, {tu.lighting}, natural landscaping integration, structural glass and clean lines, high resolution photorealistic architectural render"
            negative_prompt = "crooked walls, floating roofs, poor construction, trash, blurry, low quality, watermark, text"

            alternatives = [
                PromptAlternative(
                    title="Architectural Perspective",
                    positive_prompt=full_positive,
                    description="Balanced architectural framing with natural landscaping."
                )
            ]

        else:
            high_level = f"A clean high-fidelity depiction of {subject}"
            low_level = f"centered composition, {tu.lighting}, sharp focus, neutral background, 8k resolution"
            full_positive = f"A clean high-fidelity depiction of {subject}, centered composition, natural balanced lighting, sharp focus, clean background, high resolution, no extra unwanted objects"
            negative_prompt = "blurry, distorted, low quality, artifacts, watermark, text, extra unwanted objects, clutter"

            alternatives = [
                PromptAlternative(
                    title="Clean Representation",
                    positive_prompt=full_positive,
                    description="Faithful centered representation preserving all prompt details."
                )
            ]

        return PromptRefinementResponse(
            original_prompt=request.original_prompt,
            high_level_prompt=high_level,
            low_level_prompt=low_level,
            full_positive_prompt=full_positive,
            negative_prompt=negative_prompt,
            detected_objects=tu.objects,
            materials=tu.materials,
            style_preset=request.style_preference or "photorealistic",
            alternatives=alternatives,
            disambiguations=tu.ambiguous_terms
        )

prompt_refinement_agent = PromptRefinementAgent()
