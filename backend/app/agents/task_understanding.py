import re
from typing import Dict, List, Any, Optional
from backend.app.models.schemas import TaskUnderstandingRequest, TaskUnderstandingResponse, SpatialConstraint

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
    Agent 1: Task Understanding Agent
    Understands ANY creative concept (Simple Shapes, Graphics, Nature/Landscapes,
    Vehicles, Electronics, Furniture, Architecture, Characters, etc.)
    Strictly preserves user intent, count, shape, color, and background.
    Never forcefully converts arbitrary or simple prompts into industrial products.
    """
    def __init__(self):
        pass

    def _clean_action_prefix(self, prompt: str) -> str:
        """Strip user action imperatives like 'generate a', 'draw an', etc."""
        cleaned = re.sub(
            r'^(please\s+)?(generate|create|render|make|draw|paint|produce|give\s+me|an\s+image\s+of|a\s+picture\s+of|a\s+photo\s+of)\s+(a\s+|an\s+|the\s+)?',
            '',
            prompt.strip(),
            flags=re.IGNORECASE
        ).strip()
        # If string became empty, return original
        return cleaned if cleaned else prompt.strip()

    def analyze(self, request: TaskUnderstandingRequest) -> TaskUnderstandingResponse:
        raw_prompt = request.prompt.strip()
        cleaned_prompt = self._clean_action_prefix(raw_prompt)
        prompt_lower = raw_prompt.lower()
        cleaned_lower = cleaned_prompt.lower()

        # 1. Detect Explicit Shapes & Pure Geometric Requests
        geometric_tokens = ["circle", "square", "triangle", "rectangle", "polygon", "cube", "sphere", "cylinder", "cone", "oval", "hexagon", "octagon", "pentagon", "dot", "line"]
        has_geometric_token = any(re.search(r'\b' + re.escape(g) + r'\b', prompt_lower) for g in geometric_tokens)

        # Disambiguate if shape token is merely an adjective describing a product (e.g. "circular display", "square table")
        product_nouns = [
            "watch", "smartwatch", "table", "chair", "desk", "sofa", "lamp",
            "phone", "car", "motorcycle", "bike", "building", "villa", "room",
            "laptop", "headphone", "speaker", "camera"
        ]
        has_product_noun = any(re.search(r'\b' + re.escape(p) + r'\b', prompt_lower) for p in product_nouns)

        is_pure_geometric = has_geometric_token and not has_product_noun

        # 2. Extract Requested Colors
        color_library = [
            "red", "blue", "green", "yellow", "orange", "purple", "pink", "black",
            "white", "gray", "grey", "silver", "gold", "brown", "cyan", "magenta",
            "titanium", "cognac", "emerald", "navy", "crimson", "beige", "bronze"
        ]
        detected_colors = [c for c in color_library if re.search(r'\b' + re.escape(c) + r'\b', prompt_lower)]

        # 3. Extract Requested Background
        detected_background = None
        if "white background" in prompt_lower or "on white" in prompt_lower:
            detected_background = "plain solid white background"
        elif "black background" in prompt_lower or "on black" in prompt_lower:
            detected_background = "plain solid black background"
        elif "dark background" in prompt_lower:
            detected_background = "plain neutral dark background"
        elif "neutral background" in prompt_lower or "plain background" in prompt_lower:
            detected_background = "plain neutral background"
        elif "transparent background" in prompt_lower:
            detected_background = "plain isolated background"

        # 4. Domain & Intent Classification
        if is_pure_geometric:
            product_category = "geometric_shape"
            task_type = "geometric_graphic_design"
            matched_shape = next((g for g in geometric_tokens if re.search(r'\b' + re.escape(g) + r'\b', prompt_lower)), "shape")
            color_prefix = f"{detected_colors[0]} " if detected_colors else ""
            primary_subject = f"simple {color_prefix}{matched_shape}".strip()
            bg_desc = detected_background or "plain solid white background"
            composition = f"centered single {matched_shape}, flat 2D graphic, sharp clean silhouette, {bg_desc}, zero extra objects"
            lighting = "uniform flat lighting, zero shadows"
            detected_materials = ["solid flat color fill"]
            common_objects = [f"{color_prefix}{matched_shape}".strip()]

        elif any(k in prompt_lower for k in ["landscape", "mountain", "sunset", "sunrise", "forest", "ocean", "sea", "lake", "river", "beach", "desert", "waterfall", "sky", "valley"]) and not has_product_noun:
            product_category = "landscape_nature"
            task_type = "landscape_photography"
            primary_subject = cleaned_prompt
            composition = "wide scenic panorama, natural environmental landscape perspective"
            lighting = "atmospheric natural sunlight during sunset / golden hour" if "sunset" in prompt_lower else "natural ambient daylight"
            detected_materials = ["natural rock, earth, foliage, water"]
            common_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["chair", "table", "sofa", "desk", "armchair", "stool", "cabinet", "furniture", "couch", "bench"]):
            product_category = "furniture"
            task_type = "furniture_design"
            primary_subject = cleaned_prompt
            composition = "centered single hero furniture item, isolated studio framing, clean neutral backdrop, no surrounding clutter"
            lighting = "soft diffused studio lighting with subtle floor contact shadow"
            detected_materials = [m for m in ["walnut wood", "oak wood", "leather", "curved wood", "brushed aluminum", "fabric"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["fine natural wood", "soft upholstery"] if "wood" in prompt_lower else ["crafted furniture material"]
            common_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["smartwatch", "watch", "headphone", "earphone", "speaker", "phone", "laptop", "tablet", "camera", "display"]):
            product_category = "consumer_electronics"
            task_type = "electronics_design"
            primary_subject = cleaned_prompt
            composition = "centered hero macro product perspective, single device, clean minimal studio backdrop"
            lighting = "precise studio product rim lighting and display luminescence"
            detected_materials = [m for m in ["titanium", "aluminum", "glass", "sapphire crystal", "ceramic", "fluoroelastomer"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["grade 5 titanium", "sapphire glass"] if "titanium" in prompt_lower else ["precision matte casing"]
            common_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["motorcycle", "bike", "scooter", "superbike", "car", "vehicle", "automobile", "ev", "sedan", "suv", "hypercar", "truck"]):
            product_category = "vehicle"
            task_type = "automotive_design"
            primary_subject = cleaned_prompt
            composition = "three-quarter hero angle, single vehicle, clean automotive studio setting"
            lighting = "commercial automotive studio key light with clean surface reflection lines"
            detected_materials = [m for m in ["carbon fiber", "brushed aluminum", "matte black resin", "gloss paint"] if any(k in prompt_lower for k in m.split())]
            if not detected_materials:
                detected_materials = ["lightweight carbon composite", "aerodynamic bodywork"]
            common_objects = [cleaned_prompt]

        elif any(k in prompt_lower for k in ["villa", "house", "mansion", "facade", "pavilion", "building", "architecture", "residence"]):
            product_category = "architecture"
            task_type = "architectural_design"
            primary_subject = cleaned_prompt
            composition = "eye-level architectural perspective, wide framing, natural landscaping integration"
            lighting = "soft golden hour ambient sunlight, warm interior linear lighting"
            detected_materials = ["structural architectural glass", "natural timber", "smooth concrete"]
            common_objects = [cleaned_prompt]

        else:
            # Respect user category dropdown if explicit and prompt is generic
            req_cat = (request.category or "").lower()
            if "vehicle" in req_cat:
                product_category = "vehicle"
                task_type = "automotive_design"
            elif "electronic" in req_cat:
                product_category = "consumer_electronics"
                task_type = "electronics_design"
            elif "furniture" in req_cat:
                product_category = "furniture"
                task_type = "furniture_design"
            else:
                product_category = "general_concept"
                task_type = "creative_concept_design"

            primary_subject = cleaned_prompt
            composition = "centered subject, balanced clean framing, neutral background"
            lighting = "natural balanced illumination with soft shadows"
            detected_materials = ["authentic surface textures"]
            common_objects = [cleaned_prompt]

        # 5. Detect Lexical Ambiguity
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
            objects=common_objects,
            materials=detected_materials,
            colors=detected_colors or ["natural tones"],
            style="clean high-fidelity representation",
            lighting=lighting,
            composition=composition,
            spatial_constraints=[],
            ambiguous_terms=ambiguous_terms,
            missing_information=[]
        )

task_understanding_agent = TaskUnderstandingAgent()
