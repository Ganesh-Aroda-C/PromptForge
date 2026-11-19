import re
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel, Field

from backend.app.core.knowledge_base import DOMAIN_KNOWLEDGE, STYLE_PRESETS
from backend.app.agents.prompt_validator import prompt_quality_controller, PromptValidationReport

class EnhancedPromptOutput(BaseModel):
    original_prompt: str
    enhanced_positive_prompt: str
    enhanced_negative_prompt: str
    detected_subject: str
    detected_domain: str
    extracted_attributes: Dict[str, Any]
    breakdown: Dict[str, str]
    validation_report: PromptValidationReport
    recommended_settings: Dict[str, Any] = Field(default_factory=lambda: {
        "steps": 25,
        "cfg_scale": 7.5,
        "sampler_name": "euler_ancestral",
        "scheduler": "karras",
        "width": 512,
        "height": 512
    })

class PromptEnhancementEngine:
    """
    Intelligent Prompt Enhancement Engine for PromptForge AI
    Converts short, simple natural language descriptions into professional,
    highly detailed, engineering-accurate positive and negative prompts
    custom-tailored for Stable Diffusion 1.5.
    """
    def __init__(self):
        pass

    def _clean_action_prefix(self, prompt: str) -> str:
        """Strip user action imperatives like 'design a', 'create an', 'render', etc."""
        cleaned = re.sub(
            r'^(please\s+)?(generate|create|render|make|draw|paint|produce|give\s+me|design|an\s+image\s+of|a\s+picture\s+of|a\s+photo\s+of)\s+(a\s+|an\s+|the\s+)?',
            '',
            prompt.strip(),
            flags=re.IGNORECASE
        ).strip()
        return cleaned if cleaned else prompt.strip()

    def _extract_attributes(self, prompt: str) -> Dict[str, Any]:
        """Extract user-specified materials, colors, components, and modifiers."""
        p_lower = prompt.lower()

        # 1. Colors
        color_list = [
            "titanium", "graphite", "slate", "matte black", "black", "white", "silver",
            "gold", "bronze", "brass", "copper", "red", "blue", "navy", "green",
            "yellow", "orange", "amber", "teal", "gray", "grey"
        ]
        detected_colors = [c for c in color_list if re.search(r'\b' + re.escape(c) + r'\b', p_lower)]

        # 2. Materials
        material_list = [
            "titanium", "brushed aluminum", "aluminum", "carbon fiber", "cast iron",
            "stainless steel", "hardened steel", "chrome", "brass", "bronze",
            "wood", "walnut", "oak", "plywood", "glass", "polycarbonate",
            "silicone", "ceramic", "leather", "rubber", "enamel"
        ]
        detected_materials = [m for m in material_list if re.search(r'\b' + re.escape(m) + r'\b', p_lower)]

        # 3. Environment / Background cues
        bg = None
        if "white background" in p_lower or "on white" in p_lower:
            bg = "pure white background"
        elif "black background" in p_lower or "on black" in p_lower:
            bg = "pure black background"
        elif "workshop" in p_lower or "factory" in p_lower or "shop" in p_lower:
            bg = "clean industrial factory workshop floor"
        elif "studio" in p_lower:
            bg = "clean neutral cyclorama studio backdrop"

        # 4. Geometry cues
        geom = None
        for g in ["circular", "square", "curved", "cylindrical", "rectangular", "hexagonal", "aerodynamic"]:
            if g in p_lower:
                geom = g
                break

        return {
            "colors": detected_colors,
            "materials": detected_materials,
            "background": bg,
            "geometry": geom
        }

    def _match_domain_knowledge(self, prompt: str, category_hint: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """Matches prompt against rich engineering knowledge base."""
        p_lower = prompt.lower()

        # Direct pattern match
        for key, data in DOMAIN_KNOWLEDGE.items():
            for pattern in data["patterns"]:
                if re.search(pattern, p_lower):
                    return key, data

        # Check category hint if provided
        if category_hint:
            cat_lower = category_hint.lower()
            if "cnc" in cat_lower or "machin" in cat_lower:
                return "cnc_machine", DOMAIN_KNOWLEDGE["cnc_machine"]
            if "robot" in cat_lower:
                return "robotic_arm", DOMAIN_KNOWLEDGE["robotic_arm"]
            if "press" in cat_lower:
                return "hydraulic_press", DOMAIN_KNOWLEDGE["hydraulic_press"]
            if "motor" in cat_lower:
                return "electric_motor", DOMAIN_KNOWLEDGE["electric_motor"]
            if "conveyor" in cat_lower:
                return "conveyor_system", DOMAIN_KNOWLEDGE["conveyor_system"]
            if "watch" in cat_lower or "electronic" in cat_lower:
                return "smartwatch", DOMAIN_KNOWLEDGE["smartwatch"]
            if "vehicle" in cat_lower or "car" in cat_lower or "motorcycle" in cat_lower:
                return "electric_vehicle", DOMAIN_KNOWLEDGE["electric_vehicle"]
            if "furniture" in cat_lower or "chair" in cat_lower:
                return "furniture", DOMAIN_KNOWLEDGE["furniture"]
            if "landscape" in cat_lower:
                return "landscape_nature", DOMAIN_KNOWLEDGE["landscape_nature"]
            if "arch" in cat_lower:
                return "architecture", DOMAIN_KNOWLEDGE["architecture"]

        # Dynamic Generic Industrial / Product Fallback Builder
        cleaned = self._clean_action_prefix(prompt)
        fallback_data = {
            "domain": "industrial_product",
            "display_name": cleaned.title(),
            "core_subject": f"high-precision industrial prototype of {cleaned}",
            "mechanical_structure": f"robust mechanical assembly of {cleaned}, precision-engineered structural housing, industrial fasteners, calibrated functional components",
            "materials": "machined anodized aluminum, powder-coated industrial steel casing, satin metallic finish",
            "proportions_geometry": "ergonomic functional geometry, clean mechanical proportions, solid stationary footing",
            "component_arrangement": f"centered hero orientation of {cleaned}, balanced layout showcasing key engineering features",
            "lighting": "calibrated 5500K commercial studio lighting, soft diffused key light with crisp edge rim reflections",
            "camera": "eye-level three-quarter perspective hero shot, centered framing, crisp focal depth",
            "environment": "clean neutral cyclorama infinity backdrop in warm slate gray, soft contact ground shadow",
            "visual_style": "hyperrealistic industrial engineering photography, 8k resolution, immaculate CAD prototype finish",
            "engineering_details": "precision tolerance markings, clean chamfered edges, recessed hex fasteners, high micro-contrast",
            "negative_exclusions": "distorted geometry, broken components, floating parts, disconnected wires, unrealistic textures, blurry details, low resolution, messy room clutter, people, hands, cartoon, 3d render artifacts, watermark, text"
        }
        return "custom_product", fallback_data

    def enhance(
        self,
        raw_prompt: str,
        style_preset_name: Optional[str] = "Photorealistic 3D",
        category_hint: Optional[str] = None
    ) -> EnhancedPromptOutput:
        orig = raw_prompt.strip()
        cleaned_subject = self._clean_action_prefix(orig)

        # 1. Extract User-Specified Attributes
        attrs = self._extract_attributes(orig)

        # 2. Retrieve Domain Knowledge
        key, data = self._match_domain_knowledge(orig, category_hint)
        domain_name = data.get("domain", "general")
        detected_subject = data.get("display_name", cleaned_subject.title())

        # 3. Integrate User Specifications with Domain Knowledge
        # If user explicitly requested custom materials/colors/background, prioritize them
        mat_text = data["materials"]
        if attrs["materials"]:
            custom_mats = ", ".join(attrs["materials"])
            mat_text = f"crafted with {custom_mats}, {mat_text}"

        bg_text = attrs["background"] if attrs["background"] else data["environment"]
        geom_text = data["proportions_geometry"]
        if attrs["geometry"]:
            geom_text = f"{attrs['geometry']} geometry, {geom_text}"

        # 4. Integrate Style Preset
        style_info = STYLE_PRESETS.get(style_preset_name or "Photorealistic 3D", STYLE_PRESETS["Photorealistic 3D"])
        style_pos = style_info["positive"]
        style_neg = style_info["negative"]

        # 5. Build Positive Prompt Components
        breakdown = {
            "subject": f"A standalone, high-precision {data['core_subject']}",
            "mechanical_structure": data["mechanical_structure"],
            "materials": mat_text,
            "geometry_proportions": geom_text,
            "arrangement": data["component_arrangement"],
            "lighting": data["lighting"],
            "camera": data["camera"],
            "environment": bg_text,
            "style_quality": f"{data['visual_style']}, {style_pos}",
            "engineering_details": data["engineering_details"]
        }

        # Synthesize Full Positive Prompt for Stable Diffusion 1.5
        # Structure: Subject -> Structure & Components -> Materials -> Arrangement & Camera -> Lighting & Environment -> Quality & Style
        positive_prompt_clauses = [
            breakdown["subject"],
            breakdown["mechanical_structure"],
            breakdown["materials"],
            breakdown["geometry_proportions"],
            breakdown["arrangement"],
            breakdown["camera"],
            breakdown["lighting"],
            breakdown["environment"],
            breakdown["engineering_details"],
            breakdown["style_quality"]
        ]
        enhanced_positive = ", ".join(c.strip().rstrip('.') for c in positive_prompt_clauses if c.strip()) + "."

        # 6. Build Tailored Negative Prompt
        # Combines domain-specific structural defects + generative flaws + style negative
        general_defects = (
            "deformed mechanical components, distorted geometry, incorrect proportions, "
            "floating components, disconnected parts, misaligned axes, unrealistic materials, "
            "blurry details, low resolution, noisy, pixelated, amateur lighting, harsh shadows, "
            "double image, duplicate objects, cut off, cropped, text artifacts, watermark, signature, logo"
        )
        domain_exclusions = data.get("negative_exclusions", "")
        negative_prompt_clauses = [
            general_defects,
            domain_exclusions,
            style_neg
        ]

        # Deduplicate negative tokens
        seen_clauses = set()
        clean_neg_parts = []
        for clause in ", ".join(negative_prompt_clauses).split(","):
            token = clause.strip().lower()
            if token and token not in seen_clauses:
                seen_clauses.add(token)
                clean_neg_parts.append(clause.strip())

        enhanced_negative = ", ".join(clean_neg_parts)

        # 7. Quality Control & Validation
        val_report = prompt_quality_controller.validate_enhancement(
            original_prompt=orig,
            enhanced_positive=enhanced_positive,
            enhanced_negative=enhanced_negative,
            detected_subject=detected_subject
        )

        # 8. Dynamic Recommended Settings tailored for Stable Diffusion 1.5
        recommended_settings = {
            "steps": 25,
            "cfg_scale": 7.5,
            "sampler_name": "euler_ancestral",
            "scheduler": "karras",
            "width": 512,
            "height": 512,
            "seed": -1
        }

        return EnhancedPromptOutput(
            original_prompt=orig,
            enhanced_positive_prompt=enhanced_positive,
            enhanced_negative_prompt=enhanced_negative,
            detected_subject=detected_subject,
            detected_domain=domain_name,
            extracted_attributes=attrs,
            breakdown=breakdown,
            validation_report=val_report,
            recommended_settings=recommended_settings
        )

prompt_enhancement_engine = PromptEnhancementEngine()
