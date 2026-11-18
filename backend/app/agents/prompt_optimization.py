import random
import re
from typing import List, Dict, Any, Tuple
from backend.app.models.schemas import (
    EvolutionaryOptimizationRequest,
    EvolutionaryOptimizationResponse,
    CandidatePrompt,
    GenerationLog,
    OptimizationWeights
)

DOMAIN_MODIFIERS: Dict[str, List[str]] = {
    "geometric_shape": [
        "razor-sharp geometric boundaries",
        "flat 2D vector graphic design",
        "pure solid color fill",
        "isolated single centered primitive",
        "zero shadows and zero gradients",
        "clean mathematical precision"
    ],
    "consumer_electronics": [
        "precision brushed titanium frame",
        "anti-reflective high-resolution AMOLED display",
        "calibrated studio rim lighting",
        "clean minimal tactile buttons",
        "diffused studio softbox illumination",
        "clean neutral cyclorama background"
    ],
    "furniture": [
        "sculpted curved hardwood construction",
        "authentic tactile wood grain finish",
        "soft ground contact shadow",
        "diffused studio key light",
        "minimal Scandinavian ergonomic proportions",
        "clean neutral studio backdrop"
    ],
    "vehicle": [
        "aerodynamic wind-tunnel sculpted bodywork",
        "commercial automotive studio key light",
        "clean surface reflection horizon lines",
        "lightweight performance chassis proportions",
        "crisp three-quarter studio stance",
        "neutral automotive cyclorama background"
    ],
    "landscape_nature": [
        "atmospheric golden hour sunlight",
        "wide-angle panoramic depth",
        "natural foreground and mountain horizon",
        "serene environmental water reflections",
        "Hasselblad medium format clarity",
        "rich vibrant natural color palette"
    ],
    "architecture": [
        "clean structural glass and timber elements",
        "warm interior linear illumination",
        "natural integrated landscaping",
        "balanced eye-level architectural perspective",
        "crisp geometric proportions"
    ],
    "general": [
        "calibrated studio softbox lighting",
        "clean neutral background",
        "sharp focal plane with immaculate finish",
        "balanced centered composition",
        "high texture fidelity and crisp contrast"
    ]
}

class PromptOptimizationEngine:
    """
    Agent 3: Evolutionary Prompt Optimization Engine
    Inspired by:
    - TAPO (Luo et al., 2024): Task-Referenced Adaptation for Prompt Optimization
    - CoolPrompt (Kulin et al., 2024): ReflectivePrompt, DistillPrompt, HyPE
    - Evolutionary Prompt Optimization (Vishwanth et al., 2024): Multi-Task Genetic Search
    Executes domain-aware genetic prompt search preserving user intent without inserting irrelevant objects.
    """
    def __init__(self):
        pass

    def _detect_domain(self, prompt: str, task_type: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["circle", "square", "triangle", "rectangle", "hexagon", "vector", "icon", "svg", "dot"]):
            if not any(w in p for w in ["watch", "chair", "car", "bike"]):
                return "geometric_shape"
        if any(w in p for w in ["smartwatch", "watch", "phone", "laptop", "display", "headphone"]):
            return "consumer_electronics"
        if any(w in p for w in ["chair", "table", "furniture", "sofa", "desk"]):
            return "furniture"
        if any(w in p for w in ["motorcycle", "bike", "car", "vehicle", "automobile", "hypercar"]):
            return "vehicle"
        if any(w in p for w in ["landscape", "mountain", "sunset", "lake", "ocean", "forest"]):
            return "landscape_nature"
        if any(w in p for w in ["villa", "house", "building", "architecture"]):
            return "architecture"
        return "general"

    def _select_task_metrics(self, domain: str, custom_weights: OptimizationWeights) -> Tuple[List[str], Dict[str, float]]:
        """Task-Aware Metric Selection (TAPO - Luo et al., 2024)"""
        metrics = ["semantic_accuracy", "component_completeness", "clarity_and_fidelity", "structural_adherence"]
        weights = {
            "semantic_accuracy": custom_weights.semantic_accuracy,
            "component_completeness": custom_weights.component_completeness,
            "clarity_and_fidelity": custom_weights.clarity_and_fidelity,
            "structural_adherence": custom_weights.structural_adherence
        }
        total = sum(weights.values())
        normalized = {k: v / total for k, v in weights.items()}
        return metrics, normalized

    def _evaluate_candidate(self, prompt: str, initial_prompt: str, domain: str, weights: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Genuine multi-metric scoring function evaluating:
        1. Semantic accuracy (preserves words from initial prompt)
        2. Component completeness (appropriate domain modifiers present)
        3. Clarity and fidelity (optimal token length without word salad)
        4. Structural adherence (composition, lighting, and background cues)
        """
        words_initial = set(re.findall(r'\b[a-zA-Z]{3,}\b', initial_prompt.lower()))
        words_candidate = set(re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower()))
        tokens_count = len(prompt.split())

        # Metric 1: Semantic Accuracy (Preservation of user's core concepts)
        preserved = len(words_initial.intersection(words_candidate))
        semantic_acc = min(1.0, (preserved / max(1, len(words_initial))) * 0.75 + 0.25)

        # Metric 2: Component Completeness (Domain-specific quality terms)
        domain_terms = {
            "geometric_shape": ["vector", "flat", "geometric", "clean", "sharp", "solid", "fill"],
            "consumer_electronics": ["titanium", "display", "studio", "lighting", "finish", "clean", "amoled"],
            "furniture": ["wood", "ergonomic", "studio", "craftsmanship", "shadow", "neutral", "curve"],
            "vehicle": ["aerodynamic", "studio", "lighting", "bodywork", "chassis", "stance"],
            "landscape_nature": ["landscape", "sunlight", "depth", "natural", "horizon", "clarity", "sunset"],
            "architecture": ["architectural", "glass", "lines", "lighting", "render", "proportions"],
            "general": ["lighting", "studio", "background", "sharp", "clean", "composition"]
        }
        target_words = domain_terms.get(domain, domain_terms["general"])
        present_count = sum(1 for term in target_words if term in prompt.lower())
        completeness = min(1.0, 0.4 + (present_count / max(1, len(target_words))) * 0.6)

        # Metric 3: Clarity and Fidelity (Optimal length: 20-65 tokens)
        if 20 <= tokens_count <= 65:
            clarity = 0.94
        elif tokens_count < 20:
            clarity = 0.65 + (tokens_count / 20.0) * 0.25
        else:
            clarity = max(0.5, 0.94 - ((tokens_count - 65) / 80.0) * 0.4)

        # Metric 4: Structural Adherence
        has_lighting = any(k in prompt.lower() for k in ["lighting", "light", "sunlight", "illumination", "softbox", "flat"])
        has_camera = any(k in prompt.lower() for k in ["angle", "view", "perspective", "macro", "panoramic", "centered", "hero"])
        has_backdrop = any(k in prompt.lower() for k in ["background", "backdrop", "cyclorama", "environment", "white", "black"])
        has_style = any(k in prompt.lower() for k in ["vector", "render", "photograph", "design", "graphic", "finish"])
        structural = (float(has_lighting) + float(has_camera) + float(has_backdrop) + float(has_style)) / 4.0

        metrics = {
            "semantic_accuracy": round(semantic_acc, 3),
            "component_completeness": round(completeness, 3),
            "clarity_and_fidelity": round(clarity, 3),
            "structural_adherence": round(structural, 3)
        }

        fitness = sum(metrics[m] * weights.get(m, 0.25) for m in metrics)
        return round(fitness, 4), metrics

    def _crossover(self, parent_a: str, parent_b: str, rng: random.Random) -> str:
        """Semantic Crossover (Vishwanth et al., 2024): Recombining prompt sub-clauses"""
        clauses_a = [c.strip() for c in re.split(r'[,.]', parent_a) if c.strip()]
        clauses_b = [c.strip() for c in re.split(r'[,.]', parent_b) if c.strip()]

        if not clauses_a:
            return parent_b
        if not clauses_b:
            return parent_a

        split_a = max(1, len(clauses_a) // 2)
        split_b = max(1, len(clauses_b) // 2)

        child_clauses = clauses_a[:split_a] + clauses_b[split_b:]
        unique_clauses = []
        for c in child_clauses:
            if c not in unique_clauses:
                unique_clauses.append(c)
        return ", ".join(unique_clauses)

    def _mutate(self, prompt: str, domain: str, mutation_type: str, rng: random.Random) -> str:
        """
        Domain-Specific Mutation Operators (CoolPrompt - Kulin et al., 2024):
        - Reflective: Injects domain-appropriate quality cues
        - Distill: Prunes redundant boilerplate
        """
        available = DOMAIN_MODIFIERS.get(domain, DOMAIN_MODIFIERS["general"])

        if mutation_type == "reflective":
            unused = [m for m in available if m.split()[0] not in prompt.lower()]
            if unused:
                added = rng.choice(unused)
                return f"{prompt.rstrip('.')}, {added}"
            return prompt

        elif mutation_type == "distill":
            replacements = {
                "in a very high resolution": "8k resolution",
                "very high quality": "crisp studio clarity",
                "nice lighting": "calibrated studio illumination",
                "on a background": "clean neutral backdrop",
                "in a room": "studio setting"
            }
            res = prompt
            for old, new in replacements.items():
                res = res.replace(old, new)
            return res

        else:
            # Lexical upgrade
            if available:
                added = rng.choice(available)
                return f"{prompt.rstrip('.')}, {added}"
            return prompt

    def optimize(self, request: EvolutionaryOptimizationRequest) -> EvolutionaryOptimizationResponse:
        rng = random.Random(request.seed or 42)
        initial_prompt = request.initial_prompt.strip()
        domain = self._detect_domain(initial_prompt, request.task_type)
        metrics_list, weights = self._select_task_metrics(domain, request.weights)

        # Baseline evaluation
        init_fitness, init_metrics = self._evaluate_candidate(initial_prompt, initial_prompt, domain, weights)

        # Initialize Population (Seed + domain variations)
        population: List[CandidatePrompt] = []
        population.append(CandidatePrompt(
            candidate_id="p-0-0",
            prompt=initial_prompt,
            fitness_score=init_fitness,
            metrics=init_metrics,
            generation=0,
            mutation_type="seed"
        ))

        available_modifiers = DOMAIN_MODIFIERS.get(domain, DOMAIN_MODIFIERS["general"])
        for i in range(1, request.population_size):
            mod = available_modifiers[i % len(available_modifiers)]
            candidate_text = f"{initial_prompt.rstrip('.')}, {mod}"
            fit, met = self._evaluate_candidate(candidate_text, initial_prompt, domain, weights)
            population.append(CandidatePrompt(
                candidate_id=f"p-0-{i}",
                prompt=candidate_text,
                fitness_score=fit,
                metrics=met,
                generation=0,
                mutation_type="domain_seed"
            ))

        generation_history: List[GenerationLog] = []

        # Record Gen 0
        population.sort(key=lambda x: x.fitness_score, reverse=True)
        generation_history.append(GenerationLog(
            generation_index=0,
            best_fitness=population[0].fitness_score,
            average_fitness=round(sum(c.fitness_score for c in population) / len(population), 4),
            best_prompt=population[0].prompt,
            candidates=list(population)
        ))

        # Evolutionary Loop
        for gen in range(1, request.num_generations + 1):
            next_generation: List[CandidatePrompt] = []

            # 1. Elitism: Retain top candidates
            elite_count = max(1, request.population_size // 3)
            for e_idx in range(elite_count):
                elite = population[e_idx]
                next_generation.append(CandidatePrompt(
                    candidate_id=f"p-{gen}-e{e_idx}",
                    prompt=elite.prompt,
                    fitness_score=elite.fitness_score,
                    metrics=elite.metrics,
                    generation=gen,
                    parent_ids=[elite.candidate_id],
                    mutation_type="elite_retention"
                ))

            # 2. Tournament Selection, Crossover & Mutation
            while len(next_generation) < request.population_size:
                p1, p2 = rng.sample(population[:max(2, elite_count + 2)], 2)
                child_text = self._crossover(p1.prompt, p2.prompt, rng)

                # Mutate
                mut_type = "none"
                if rng.random() < request.mutation_rate:
                    mut_type = rng.choice(["reflective", "distill", "lexical"])
                    child_text = self._mutate(child_text, domain, mut_type, rng)

                fit, met = self._evaluate_candidate(child_text, initial_prompt, domain, weights)
                next_generation.append(CandidatePrompt(
                    candidate_id=f"p-{gen}-{len(next_generation)}",
                    prompt=child_text,
                    fitness_score=fit,
                    metrics=met,
                    generation=gen,
                    parent_ids=[p1.candidate_id, p2.candidate_id],
                    mutation_type=mut_type
                ))

            population = sorted(next_generation, key=lambda x: x.fitness_score, reverse=True)
            generation_history.append(GenerationLog(
                generation_index=gen,
                best_fitness=population[0].fitness_score,
                average_fitness=round(sum(c.fitness_score for c in population) / len(population), 4),
                best_prompt=population[0].prompt,
                candidates=list(population)
            ))

        best = population[0]
        improvement = round(((best.fitness_score - init_fitness) / max(0.01, init_fitness)) * 100.0, 1)

        return EvolutionaryOptimizationResponse(
            initial_prompt=initial_prompt,
            best_prompt=best.prompt,
            initial_fitness=init_fitness,
            best_fitness=best.fitness_score,
            improvement_percentage=max(0.0, improvement),
            total_generations=request.num_generations,
            selected_metrics=metrics_list,
            generation_history=generation_history
        )

prompt_optimization_engine = PromptOptimizationEngine()
