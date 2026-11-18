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

class PromptOptimizationEngine:
    """
    Agent 3: Evolutionary Prompt Optimization Engine
    Inspired by:
    - TAPO (Luo et al., 2024): Task-Referenced Adaptation for Prompt Optimization
    - CoolPrompt (Kulin et al., 2024): ReflectivePrompt, DistillPrompt, HyPE
    - Evolutionary Prompt Optimization (Vishwanth et al., 2024): Genetic Search
    - Comparisons of EC Algorithms (2024): Elitism, Truncation, Population Dynamics
    """
    def __init__(self):
        # Lexical engineering modifier dictionary
        self.engineering_modifiers = [
            "anodized 6061 aluminum alloy finish",
            "aerodynamic NACA duct profiling",
            "exposed carbon fiber monocoque weave",
            "micro-textured silicone tactile interfaces",
            "recessed stainless steel hex fasteners",
            "precision CNC chamfered edges with 0.5mm radius",
            "diffused 4500K studio key light and high-contrast rim lighting",
            "neutral gray gradient cyclorama infinity studio backdrop",
            "subtle contact shadows on non-reflective ground plane",
            "Hasselblad H6D-100c medium format camera clarity",
            "uncompromising industrial design geometric tolerances"
        ]

    def _select_task_metrics(self, task_type: str, custom_weights: OptimizationWeights) -> Tuple[List[str], Dict[str, float]]:
        """Task-Aware Metric Selection (TAPO - Luo et al., 2024)"""
        if "industrial" in task_type or "product" in task_type or "automotive" in task_type:
            metrics = ["semantic_accuracy", "component_completeness", "clarity_and_fidelity", "structural_adherence"]
            weights = {
                "semantic_accuracy": custom_weights.semantic_accuracy,
                "component_completeness": custom_weights.component_completeness,
                "clarity_and_fidelity": custom_weights.clarity_and_fidelity,
                "structural_adherence": custom_weights.structural_adherence
            }
        else:
            metrics = ["semantic_relevance", "aesthetic_diversity", "style_consistency", "prompt_conciseness"]
            weights = {
                "semantic_relevance": 0.40,
                "aesthetic_diversity": 0.25,
                "style_consistency": 0.20,
                "prompt_conciseness": 0.15
            }
        # Normalize weights to sum to 1.0
        total_weight = sum(weights.values())
        normalized_weights = {k: v / total_weight for k, v in weights.items()}
        return metrics, normalized_weights

    def _evaluate_candidate(self, prompt: str, initial_prompt: str, weights: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Genuine objective multi-metric scoring function.
        Evaluates semantic alignment, token signal-to-noise, domain keyword density, and structural clarity.
        """
        words_initial = set(re.findall(r'\b[a-zA-Z]{3,}\b', initial_prompt.lower()))
        words_candidate = set(re.findall(r'\b[a-zA-Z]{3,}\b', prompt.lower()))
        tokens_count = len(prompt.split())

        # Metric 1: Semantic Accuracy (Preservation of initial core keywords)
        preserved = len(words_initial.intersection(words_candidate))
        semantic_acc = min(1.0, (preserved / max(1, len(words_initial))) * 0.7 + 0.3)

        # Metric 2: Component Completeness (Density of technical engineering terms)
        tech_terms = ["chassis", "carbon", "aluminum", "alloy", "frame", "motor", "lighting", "lens", "studio", "texture", "finish", "precision", "aerodynamic", "ergonomic", "display"]
        tech_count = sum(1 for term in tech_terms if term in prompt.lower())
        completeness = min(1.0, 0.4 + (tech_count / 8.0) * 0.6)

        # Metric 3: Clarity and Fidelity (Optimal length: 30-70 words, avoids redundancy)
        if 25 <= tokens_count <= 85:
            clarity = 0.92
        elif tokens_count < 25:
            clarity = 0.60 + (tokens_count / 25.0) * 0.3
        else:
            clarity = max(0.5, 0.92 - ((tokens_count - 85) / 100.0) * 0.4)

        # Metric 4: Structural Adherence (Presence of lighting, camera, material, and composition cues)
        has_lighting = any(k in prompt.lower() for k in ["lighting", "light", "studio", "rim", "softbox"])
        has_camera = any(k in prompt.lower() for k in ["lens", "angle", "view", "camera", "format", "perspective"])
        has_materials = any(k in prompt.lower() for k in ["carbon", "aluminum", "finish", "matte", "glass", "titanium", "leather"])
        has_backdrop = any(k in prompt.lower() for k in ["backdrop", "studio", "background", "ground", "neutral"])
        structural = (float(has_lighting) + float(has_camera) + float(has_materials) + float(has_backdrop)) / 4.0

        metrics = {
            "semantic_accuracy": round(semantic_acc, 3),
            "component_completeness": round(completeness, 3),
            "clarity_and_fidelity": round(clarity, 3),
            "structural_adherence": round(structural, 3)
        }

        # Weighted composite fitness
        fitness = sum(metrics[m] * weights.get(m, 0.25) for m in metrics)
        return round(fitness, 4), metrics

    def _crossover(self, parent_a: str, parent_b: str, rng: random.Random) -> str:
        """Semantic Crossover (Vishwanth et al., 2024): Recombining prompt sub-clauses"""
        clauses_a = [c.strip() for c in re.split(r'[,.]', parent_a) if c.strip()]
        clauses_b = [c.strip() for c in re.split(r'[,.]', parent_b) if c.strip()]

        if not clauses_a or not clauses_b:
            return parent_a

        split_a = len(clauses_a) // 2
        split_b = len(clauses_b) // 2

        child_clauses = clauses_a[:split_a] + clauses_b[split_b:]
        # Remove duplicate clauses
        unique_clauses = []
        for c in child_clauses:
            if c not in unique_clauses:
                unique_clauses.append(c)
        return ", ".join(unique_clauses)

    def _mutate(self, prompt: str, mutation_type: str, rng: random.Random) -> str:
        """
        Mutation Operators inspired by CoolPrompt (Kulin et al., 2024):
        - Reflective: Injects missing engineering specifications
        - Distill: Prunes redundant tokens
        - Lexical: Upgrades modifiers to precise terminology
        """
        if mutation_type == "reflective":
            # Add a high-impact modifier not already in prompt
            available = [m for m in self.engineering_modifiers if m.split()[0] not in prompt.lower()]
            if available:
                added = rng.choice(available)
                return f"{prompt.rstrip('.')}, {added}"
            return prompt

        elif mutation_type == "distill":
            # Compress redundant tokens
            replacements = {
                "in a very high resolution": "8k resolution",
                "made of metal": "machined aerospace-grade aluminum",
                "very beautiful": "sculptural",
                "nice lighting": "calibrated 4500K studio softbox illumination",
                "in a room": "neutral studio environment",
                "with a lot of detail": "intricate mechanical assemblies"
            }
            res = prompt
            for old, new in replacements.items():
                res = res.replace(old, new)
            return res

        elif mutation_type == "lexical":
            # Lexical synonym replacement
            synonyms = {
                "black": "matte stealth black",
                "clean": "pristine minimalist",
                "light": "diffuse rim lighting",
                "car": "electric hyper-tourer vehicle",
                "bike": "high-performance electric cafe racer",
                "screen": "flush OLED capacitive display bezel",
                "wheel": "CNC machined lightweight alloy wheel"
            }
            words = prompt.split()
            new_words = []
            for w in words:
                cleaned = w.strip(".,;:").lower()
                if cleaned in synonyms and rng.random() < 0.35:
                    new_words.append(synonyms[cleaned])
                else:
                    new_words.append(w)
            return " ".join(new_words)

        return prompt

    def optimize(self, request: EvolutionaryOptimizationRequest) -> EvolutionaryOptimizationResponse:
        rng = random.Random(request.seed if request.seed is not None else 42)
        metric_names, weights = self._select_task_metrics(request.task_type, request.weights)

        # Baseline Manual Prompt Evaluation
        initial_fitness, initial_metrics = self._evaluate_candidate(request.initial_prompt, request.initial_prompt, weights)

        # 1. Initialize Generation 0 Population
        population: List[CandidatePrompt] = []
        
        # Candidate 0 is the baseline
        population.append(CandidatePrompt(
            candidate_id="G0-C0",
            prompt=request.initial_prompt,
            fitness_score=initial_fitness,
            metrics=initial_metrics,
            generation=0,
            parent_ids=["baseline"],
            mutation_type="baseline"
        ))

        # Generate initial variations
        for i in range(1, request.population_size):
            mutated = self._mutate(request.initial_prompt, rng.choice(["reflective", "lexical"]), rng)
            fitness, metrics = self._evaluate_candidate(mutated, request.initial_prompt, weights)
            population.append(CandidatePrompt(
                candidate_id=f"G0-C{i}",
                prompt=mutated,
                fitness_score=fitness,
                metrics=metrics,
                generation=0,
                parent_ids=["baseline"],
                mutation_type="initial_variation"
            ))

        # Sort by fitness descending
        population.sort(key=lambda c: c.fitness_score, reverse=True)

        generation_history: List[GenerationLog] = []
        gen0_avg = sum(c.fitness_score for c in population) / len(population)
        generation_history.append(GenerationLog(
            generation_index=0,
            best_fitness=population[0].fitness_score,
            average_fitness=round(gen0_avg, 4),
            best_prompt=population[0].prompt,
            candidates=list(population)
        ))

        # 2. Evolutionary Loop across Generations (Selection -> Crossover -> Mutation -> Evaluation)
        current_pop = list(population)

        for gen in range(1, request.num_generations + 1):
            next_pop: List[CandidatePrompt] = []

            # Elitism: retain top 2 unchanged
            next_pop.append(current_pop[0])
            next_pop.append(current_pop[1])

            # Generate rest of population through Tournament Selection, Crossover & Mutation
            while len(next_pop) < request.population_size:
                # Tournament Selection (k=2)
                t1 = rng.sample(current_pop, 2)
                parent1 = max(t1, key=lambda c: c.fitness_score)
                t2 = rng.sample(current_pop, 2)
                parent2 = max(t2, key=lambda c: c.fitness_score)

                # Crossover
                child_prompt = self._crossover(parent1.prompt, parent2.prompt, rng)

                # Mutation
                mut_type = None
                if rng.random() < request.mutation_rate:
                    mut_type = rng.choice(["reflective", "distill", "lexical"])
                    child_prompt = self._mutate(child_prompt, mut_type, rng)

                fitness, metrics = self._evaluate_candidate(child_prompt, request.initial_prompt, weights)
                cand_id = f"G{gen}-C{len(next_pop)}"
                next_pop.append(CandidatePrompt(
                    candidate_id=cand_id,
                    prompt=child_prompt,
                    fitness_score=fitness,
                    metrics=metrics,
                    generation=gen,
                    parent_ids=[parent1.candidate_id, parent2.candidate_id],
                    mutation_type=mut_type
                ))

            # Sort next generation by fitness
            next_pop.sort(key=lambda c: c.fitness_score, reverse=True)
            current_pop = next_pop

            avg_fit = sum(c.fitness_score for c in current_pop) / len(current_pop)
            generation_history.append(GenerationLog(
                generation_index=gen,
                best_fitness=current_pop[0].fitness_score,
                average_fitness=round(avg_fit, 4),
                best_prompt=current_pop[0].prompt,
                candidates=list(current_pop)
            ))

        best_candidate = current_pop[0]
        improvement = ((best_candidate.fitness_score - initial_fitness) / max(0.01, initial_fitness)) * 100.0

        return EvolutionaryOptimizationResponse(
            initial_prompt=request.initial_prompt,
            best_prompt=best_candidate.prompt,
            initial_fitness=initial_fitness,
            best_fitness=best_candidate.fitness_score,
            improvement_percentage=round(improvement, 2),
            total_generations=request.num_generations,
            selected_metrics=metric_names,
            generation_history=generation_history
        )

prompt_optimization_engine = PromptOptimizationEngine()
