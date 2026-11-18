import pytest
from backend.app.agents.task_understanding import task_understanding_agent, TaskUnderstandingRequest
from backend.app.agents.prompt_refinement import prompt_refinement_agent, PromptRefinementRequest
from backend.app.agents.prompt_optimization import prompt_optimization_engine, EvolutionaryOptimizationRequest
from backend.app.agents.visual_framework import visual_framework_agent
from backend.app.agents.image_evaluation import visual_evaluation_agent, ImageEvaluationRequest

def test_task_understanding_agent():
    req = TaskUnderstandingRequest(prompt="high-end electric urban motorcycle with carbon fiber frame and aerodynamic front grille")
    res = task_understanding_agent.analyze(req)
    assert res.task_type == "industrial_product_design"
    assert res.product_category == "electric_motorcycle"
    assert "carbon" in " ".join(res.materials).lower()
    # Check ambiguity detection for 'grille'
    terms = [item["term"] for item in res.ambiguous_terms]
    assert "grille" in terms

def test_prompt_refinement_agent():
    req = PromptRefinementRequest(original_prompt="minimalist electric motorcycle in matte black")
    res = prompt_refinement_agent.refine(req)
    assert len(res.high_level_prompt) > 20
    assert len(res.low_level_prompt) > 20
    assert "matte" in res.full_positive_prompt.lower()
    assert len(res.negative_prompt) > 20
    assert len(res.alternatives) == 3

def test_evolutionary_optimization_engine():
    req = EvolutionaryOptimizationRequest(
        initial_prompt="electric motorcycle concept",
        task_type="industrial_design",
        population_size=4,
        num_generations=2,
        mutation_rate=0.5,
        seed=100
    )
    res = prompt_optimization_engine.optimize(req)
    assert res.total_generations == 2
    assert len(res.generation_history) == 3  # Gen 0, Gen 1, Gen 2
    assert res.best_fitness >= res.initial_fitness
    assert len(res.best_prompt) > len(req.initial_prompt)

def test_visual_evaluation_agent():
    req = ImageEvaluationRequest(
        generation_id="gen-test-01",
        image_url="https://images.unsplash.com/photo-1558981403-c5f9899a28bc",
        prompt="matte black electric motorcycle in studio with carbon frame",
        expected_objects=["motorcycle", "carbon frame"]
    )
    res = visual_evaluation_agent.evaluate(req)
    assert res.clip_similarity > 0.8
    assert res.prompt_adherence_score > 70.0
    assert len(res.vqa_probes) >= 4
    assert res.suggested_corrective_prompt is not None
