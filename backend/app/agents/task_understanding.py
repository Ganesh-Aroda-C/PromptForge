import re
from typing import Dict, List, Any, Optional
from backend.app.models.schemas import (
    TaskUnderstandingRequest,
    TaskUnderstandingResponse,
    SpatialConstraint
)

# Technical disambiguation dictionary inspired by WordNet and Prompt Disambiguation (Na et al., 2024)
TECHNICAL_GLOSSARY: Dict[str, Dict[str, str]] = {
    "grille": {
        "intended": "automotive front ventilation lattice / radiator fascia",
        "confused_with": "barbecue grill / kitchen cooking grate"
    },
    "spoiler": {
        "intended": "aerodynamic vehicle rear wing for downforce",
        "confused_with": "narrative plot leak / text spoiler"
    },
    "chassis": {
        "intended": "structural load-bearing internal frame",
        "confused_with": "empty packaging or general shell"
    },
    "bat": {
        "intended": "ergonomic sports equipment / structural profile",
        "confused_with": "nocturnal winged mammal"
    },
    "mouse": {
        "intended": "ergonomic optical computer input peripheral",
        "confused_with": "small biological rodent"
    },
    "crane": {
        "intended": "heavy industrial hydraulic lifting machinery",
        "confused_with": "long-legged wading bird"
    },
    "bezel": {
        "intended": "slender perimeter rim holding a display or glass face",
        "confused_with": "slanted gemstone cut"
    },
    "hub": {
        "intended": "central axle rotor assembly in wheel or brushless motor",
        "confused_with": "airline network airport or social meeting center"
    },
    "canopy": {
        "intended": "aerodynamic glass cockpit or architectural transparent overhang",
        "confused_with": "fabric camping tent overhang"
    }
}

class TaskUnderstandingAgent:
    """
    Agent 1: Task Understanding & Semantic Disambiguation Agent
    Extracts core subject, primary and child objects, counts, colors, materials,
    background specifications, and spatial relationships.
    Strictly preserves the user's intended subject without forcefully converting
    non-industrial concepts into industrial machines.
    """
    def __init__(self):
        pass

    def _clean_action_prefix(self, prompt: str) -> str:
        """Strip imperative prefixes like 'generate a', 'draw an', etc."""
        cleaned = re.sub(
            r'^(please\s+)?(generate|create|render|make|draw|paint|produce|give\s+me|an\s+image\s+of|a\s+picture\s+of|a\s+photo\s+of)\s+(a\s+|an\s+|the\s+)?',
            '',
            prompt.strip(),
            flags=re.IGNORECASE
        ).strip()
        return cleaned if cleaned else prompt.strip()

    def analyze(self, request: TaskUnderstandingRequest) -> TaskUnderstandingResponse:
        raw_prompt = request.prompt.strip()
        cleaned_prompt = self._clean_action_prefix(raw_prompt)
        prompt_lower = raw_prompt.lower()

        # 1. Detect Shapes & Pure Geometric Requests
        geometric_tokens = [
            "circle", "square", "triangle", "rectangle", "polygon", "cube",
            "sphere", "cylinder", "cone", "oval", "hexagon", "octagon", "pentagon",
            "star", "dot", "line", "diagram"
        ]
        has_geometric_token = any(re.search(r'\b' + re.escape(g) + r'\b', prompt_lower) for g in geometric_tokens)

        # Product nouns that might have geometric adjectives (e.g., "circular display")
        product_nouns = [
            "watch", "smartwatch", "table", "chair", "desk", "sofa", "lamp",
            "phone", "car", "motorcycle", "bike", "building", "villa", "room",
            "laptop", "headphone", "speaker", "camera"
        ]
        has_product_noun = any(re.search(r'\b' + re.escape(p) + r'\b', prompt_lower) for p in product_nouns)

        is_pure_geometric = (has_geometric_token and not has_product_noun) or (
            request.category and request.category.lower() in ["shapes", "geometric_shape", "vector"]
        )

        # 2. Extract Colors
        color_library = [
            "red", "blue", "green", "yellow", "orange", "purple", "pink", "black",
            "white", "gray", "grey", "silver", "gold", "brown", "cyan", "magenta",
            "titanium", "graphite", "emerald", "navy", "crimson", "amber", "bronze"
        ]
        detected_colors = [c for c in color_library if re.search(r'\b' + re.escape(c) + r'\b', prompt_lower)]

        # 3. Extract Background
        detected_background = "plain neutral background"
        if "white background" in prompt_lower or "on white" in prompt_lower:
            detected_background = "pure white background"
        elif "black background" in prompt_lower or "on black" in prompt_lower:
            detected_background = "pure black background"
        elif "dark background" in prompt_lower:
            detected_background = "neutral dark background"
        elif "neutral background" in prompt_lower or "plain background" in prompt_lower:
            detected_background = "neutral clean background"

        # 4. Domain & Intent Classification
        spatial_constraints: List[SpatialConstraint] = []
        detected_materials: List[str] = []
        detected_objects: List[str] = []

        if is_pure_geometric:
            product_category = "geometric_shape"
            task_type = "geometric_graphic_design"
            matched_shape = next((g for g in geometric_tokens if re.search(r'\b' + re.escape(g) + r'\b', prompt_lower)), "shape")
            color_prefix = f"{detected_colors[0]} " if detected_colors else ""
            
            # Preserve full subject description including nested sub-elements
            # Strip background phrase from cleaned prompt to get clean complete subject
            cleaned_subject = re.sub(r'\s+(on|with)\s+(a\s+)?(pure\s+|plain\s+|solid\s+)?(white|black|dark|neutral)\s+background.*$', '', cleaned_prompt, flags=re.IGNORECASE).strip()
            primary_subject = cleaned_subject if cleaned_subject else f"{color_prefix}{matched_shape}".strip()
            
            detected_objects.append(f"{color_prefix}{matched_shape}".strip())
            # Check for nested sub-objects (e.g., dot at center)
            if re.search(r'\b(dot|point)\b', prompt_lower) or "center" in prompt_lower:
                sub_color = "black" if "black" in prompt_lower else "center"
                detected_objects.append(f"{sub_color} dot at center")
                spatial_constraints.append(SpatialConstraint(
                    object_name="dot",
                    position="center",
                    bbox=[0.47, 0.47, 0.53, 0.53]
                ))

            composition = f"centered single {primary_subject}, flat 2D graphic, sharp clean silhouette, {detected_background}, zero extra objects"
            lighting = "uniform flat lighting, zero shadows"
            detected_materials = ["solid flat color fill"]

        elif any(k in prompt_lower for k in ["smartwatch", "watch", "headphone", "earphone", "speaker", "phone", "laptop", "tablet", "camera", "display"]):
            product_category = "consumer_electronics"
            task_type = "electronics_design"
            primary_subject = cleaned_prompt
            composition = "centered hero macro product perspective, single standalone device, clean minimal studio backdrop"
            lighting = "precise studio product rim lighting and display luminescence"
            detected_materials = [m for m in ["brushed titanium", "titanium", "graphite silicone", "silicone", "sapphire crystal", "aluminum", "glass", "ceramic"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["precision metallic frame", "AMOLED display"]
            detected_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["chair", "table", "sofa", "desk", "armchair", "stool", "cabinet", "furniture", "couch", "bench"]):
            product_category = "furniture"
            task_type = "furniture_design"
            primary_subject = cleaned_prompt
            composition = "centered single hero furniture piece, isolated studio framing, clean neutral backdrop, no surrounding clutter"
            lighting = "soft diffused studio lighting with subtle floor contact shadow"
            detected_materials = [m for m in ["curved wood", "natural wood", "walnut wood", "oak wood", "leather", "brushed aluminum", "fabric"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["ergonomic curved wood", "smooth timber finish"]
            detected_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["motorcycle", "bike", "superbike", "car", "vehicle", "automobile", "ev", "sedan", "suv", "hypercar", "truck"]):
            # Normalize category: vehicle
            product_category = "vehicle"
            task_type = "automotive_design"
            primary_subject = cleaned_prompt
            composition = "three-quarter hero angle, single standalone vehicle, clean automotive studio setting"
            lighting = "commercial automotive studio key light with clean surface reflection lines"
            detected_materials = [m for m in ["aerodynamic carbon fiber", "carbon fiber", "brushed aluminum", "matte black resin", "gloss paint"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["aerodynamic bodywork", "lightweight alloy"]
            detected_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["landscape", "mountain", "sunset", "sunrise", "forest", "ocean", "sea", "lake", "river", "beach", "desert", "waterfall", "sky", "valley"]):
            product_category = "landscape_nature"
            task_type = "landscape_photography"
            primary_subject = cleaned_prompt
            composition = "wide scenic panorama, natural environmental perspective"
            lighting = "atmospheric natural sunlight during sunset / golden hour" if "sunset" in prompt_lower else "natural ambient daylight"
            detected_materials = ["natural rock, earth, foliage, water reflections"]
            detected_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["villa", "house", "mansion", "facade", "pavilion", "building", "architecture", "residence"]):
            product_category = "architecture"
            task_type = "architectural_design"
            primary_subject = cleaned_prompt
            composition = "eye-level architectural perspective, wide framing, natural landscaping integration"
            lighting = "soft golden hour ambient sunlight, warm interior linear lighting"
            detected_materials = ["structural architectural glass", "natural timber", "smooth concrete"]
            detected_objects = [cleaned_prompt]

        else:
            req_cat = (request.category or "").lower()
            if "vehicle" in req_cat or "motorcycle" in req_cat:
                product_category = "vehicle"
                task_type = "automotive_design"
            elif "electronic" in req_cat:
                product_category = "consumer_electronics"
                task_type = "electronics_design"
            elif "furniture" in req_cat:
                product_category = "furniture"
                task_type = "furniture_design"
            elif "landscape" in req_cat:
                product_category = "landscape_nature"
                task_type = "landscape_photography"
            elif "architecture" in req_cat:
                product_category = "architecture"
                task_type = "architectural_design"
            else:
                product_category = "general_concept"
                task_type = "creative_concept_design"

            primary_subject = cleaned_prompt
            composition = "centered subject, balanced clean framing, neutral background"
            lighting = "natural balanced illumination with soft shadows"
            detected_materials = ["authentic surface textures"]
            detected_objects = [cleaned_prompt]

        # 5. Detect Lexical Ambiguity (Na et al., 2024)
        ambiguous_terms = []
        for term, gloss_data in TECHNICAL_GLOSSARY.items():
            if re.search(r'\b' + re.escape(term) + r'\b', prompt_lower):
                ambiguous_terms.append({
                    "term": term,
                    "intended_gloss": gloss_data["intended"],
                    "disambiguation_note": f"Ensure '{term}' represents {gloss_data['intended']}, not {gloss_data['confused_with']}."
                })

        return TaskUnderstandingResponse(
            task_type=task_type,
            product_category=product_category,
            primary_subject=primary_subject,
            objects=detected_objects,
            materials=detected_materials,
            colors=detected_colors or ["natural tones"],
            style="clean high-fidelity representation",
            lighting=lighting,
            composition=composition,
            spatial_constraints=spatial_constraints,
            ambiguous_terms=ambiguous_terms,
            missing_information=[]
        )

task_understanding_agent = TaskUnderstandingAgent()
