import asyncio
import os
import pytest
from PIL import Image
from backend.app.agents.task_understanding import task_understanding_agent, TaskUnderstandingRequest
from backend.app.agents.prompt_refinement import prompt_refinement_agent, PromptRefinementRequest
from backend.app.agents.image_generation import image_generation_agent
from backend.app.agents.image_evaluation import visual_evaluation_agent, ImageEvaluationRequest
from backend.app.models.schemas import ImageGenerationRequest

TEST_PROMPTS = [
    {
        "id": "TEST_1_SMARTWATCH",
        "prompt": "A futuristic smartwatch with a circular AMOLED display, titanium body and graphite strap.",
        "expected_domain": "consumer_electronics"
    },
    {
        "id": "TEST_2_CHAIR",
        "prompt": "A modern wooden lounge chair with curved ergonomic construction.",
        "expected_domain": "furniture"
    },
    {
        "id": "TEST_3_MOTORCYCLE",
        "prompt": "A futuristic electric motorcycle with aerodynamic bodywork.",
        "expected_domain": "electric_motorcycle"
    },
    {
        "id": "TEST_4_VILLA",
        "prompt": "A photorealistic modern architectural villa surrounded by greenery.",
        "expected_domain": "architecture_villa"
    }
]

def test_full_pipeline_4_benchmark_prompts():
    asyncio.run(_run_pipeline_test())

async def _run_pipeline_test():
    generated_image_paths = []

    for test_case in TEST_PROMPTS:
        print(f"\n--- Executing {test_case['id']} ---")
        prompt = test_case["prompt"]

        # 1. Prompt Understanding
        tu_res = task_understanding_agent.analyze(TaskUnderstandingRequest(prompt=prompt))
        assert tu_res.product_category == test_case["expected_domain"], f"Expected {test_case['expected_domain']}, got {tu_res.product_category}"

        # 2. Prompt Refinement
        ref_res = prompt_refinement_agent.refine(PromptRefinementRequest(original_prompt=prompt, task_understanding=tu_res))
        assert len(ref_res.full_positive_prompt) > len(prompt)
        assert len(ref_res.negative_prompt) > 10

        # 3. Dynamic Image Generation
        gen_req = ImageGenerationRequest(
            prompt=ref_res.full_positive_prompt,
            negative_prompt=ref_res.negative_prompt,
            num_images=1,
            width=512,
            height=512
        )
        gen_res = await image_generation_agent.generate(gen_req)
        assert gen_res.success is True
        assert len(gen_res.generations) == 1

        img_item = gen_res.generations[0]
        assert img_item.image_url.startswith("/api/static/generations/")

        # Verify physical file existence on disk
        local_filename = img_item.image_url.replace("/api/static/generations/", "")
        local_filepath = os.path.join(image_generation_agent.output_dir, local_filename)
        assert os.path.exists(local_filepath), f"File {local_filepath} does not exist"
        assert os.path.getsize(local_filepath) > 1000, f"File {local_filepath} is too small"

        # Verify image can be parsed by PIL
        with Image.open(local_filepath) as img:
            assert img.size[0] >= 512
            assert img.size[1] >= 512

        # 4. Evaluation
        eval_res = visual_evaluation_agent.evaluate(ImageEvaluationRequest(
            generation_id=img_item.generation_id,
            image_url=img_item.image_url,
            prompt=prompt
        ))
        assert eval_res.clip_similarity > 0.8
        assert eval_res.prompt_adherence_score >= 75.0

        generated_image_paths.append(local_filepath)

    # 5. Verify images are distinct and not reused
    assert len(set(generated_image_paths)) == 4, "Generated image paths must be unique for each prompt!"
    print("\nAll 4 benchmark tests generated successfully with distinct files and high adherence!")
