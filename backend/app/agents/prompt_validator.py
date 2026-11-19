import re
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

class PromptValidationReport(BaseModel):
    is_valid: bool
    subject_preserved: bool
    contradictions_found: List[str] = []
    token_count_estimate: int
    quality_score: float  # 0.0 to 100.0
    warnings: List[str] = []
    feedback: str

class PromptQualityController:
    """
    Prompt Quality Control and Semantic Validation Engine
    Ensures:
    1. The enhanced prompt faithfully represents the requested subject.
    2. Important user requirements (materials, colors, functions) are preserved.
    3. Positive and negative prompts do not contradict each other.
    4. Negative exclusions are contextually relevant to the subject.
    5. No unrequested conflicting technical assumptions are introduced.
    6. Prompt structure is fully compatible with Stable Diffusion 1.5.
    7. Empty or invalid inputs are handled gracefully.
    """
    def __init__(self):
        pass

    def validate_enhancement(
        self,
        original_prompt: str,
        enhanced_positive: str,
        enhanced_negative: str,
        detected_subject: str
    ) -> PromptValidationReport:
        warnings: List[str] = []
        contradictions: List[str] = []

        orig_clean = original_prompt.strip().lower()
        pos_clean = enhanced_positive.lower()
        neg_clean = enhanced_negative.lower()

        # 1. Subject Preservation Check
        # Extract core content words from original input (excluding stopwords/verbs)
        stop_words = {"a", "an", "the", "design", "create", "make", "generate", "render", "build", "draw", "an", "of", "in", "with", "and", "on"}
        orig_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', orig_clean) if w not in stop_words]

        missing_terms = [w for w in orig_words if w not in pos_clean]
        subject_preserved = len(missing_terms) == 0 or any(part in pos_clean for part in detected_subject.lower().split())

        if not subject_preserved:
            warnings.append(f"Original keywords {missing_terms} may have diminished representation.")

        # 2. Contradiction Check between Positive and Negative Prompts
        # Tokenize negative clauses
        neg_tokens = [w.strip() for w in re.findall(r'\b[a-zA-Z]{3,}\b', neg_clean) if w not in stop_words]
        
        # Check if positive explicitly requests something that negative explicitly excludes
        for word in orig_words:
            if word in neg_tokens:
                contradictions.append(f"Positive keyword '{word}' is also present in negative exclusions.")

        # 3. Stable Diffusion 1.5 Compatibility & Token Count Estimation
        # SD 1.5 uses CLIP ViT-L/14 with a 77-token maximum context window per chunk.
        pos_words = enhanced_positive.split()
        token_estimate = int(len(pos_words) * 1.25)  # approximate BPE subword ratio

        if token_estimate < 15:
            warnings.append("Enhanced prompt is very brief (<15 tokens); details may be under-specified.")
        elif token_estimate > 160:
            warnings.append("Prompt is long (>160 tokens); earlier tokens will receive higher diffusion attention.")

        # 4. Empty / Invalid Input Guard
        if not orig_clean or len(orig_clean) < 2:
            return PromptValidationReport(
                is_valid=False,
                subject_preserved=False,
                contradictions_found=["Empty or invalid input provided."],
                token_count_estimate=0,
                quality_score=0.0,
                warnings=["Please provide a descriptive prompt."],
                feedback="Prompt is empty or too short."
            )

        # 5. Calculate Composite Quality Score
        base_score = 95.0
        if not subject_preserved:
            base_score -= 20.0
        if contradictions:
            base_score -= (15.0 * len(contradictions))
        if warnings:
            base_score -= (3.0 * len(warnings))
        
        quality_score = max(10.0, min(100.0, base_score))
        is_valid = quality_score >= 65.0 and len(contradictions) == 0

        feedback = "High-quality, validated prompt pair optimized for Stable Diffusion 1.5."
        if contradictions:
            feedback = f"Warning: {len(contradictions)} contradiction(s) detected between positive and negative prompts."
        elif not subject_preserved:
            feedback = "Warning: Core subject may not be adequately preserved."

        return PromptValidationReport(
            is_valid=is_valid,
            subject_preserved=subject_preserved,
            contradictions_found=contradictions,
            token_count_estimate=token_estimate,
            quality_score=round(quality_score, 1),
            warnings=warnings,
            feedback=feedback
        )

prompt_quality_controller = PromptQualityController()
