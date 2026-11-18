import asyncio
import os
import pytest
from PIL import Image
from backend.app.agents.task_understanding import task_understanding_agent, TaskUnderstandingRequest
from backend.app.agents.prompt_refinement import prompt_refinement_agent, PromptRefinementRequest
from backend.app.agents.image_generation import image_generation_agent
from backend.app.agents.image_evaluation import visual_evaluation_agent, ImageEvaluationRequest
from backend.app.models.schemas import ImageGenerationRequest

BENCHMARK_PROMPTS = [
    {
        "id": "TEST_1_RED_CIRCLE_DOT",
        "prompt": "A solid red circle with a small black dot exactly at its center on a pure white background.",
        "expected_domain": "geometric_shape",
        "is_vector": True
    },
    {
        "id": "TEST_2_BLUE_SQUARE",
        "prompt": "A blue square centered on a plain white background.",
        "expected_domain": "geometric_shape",
        "is_vector": True
    },
    {
        "id": "TEST_3_SMARTWATCH",
        "prompt": "A premium futuristic smartwatch with a circular AMOLED display, brushed titanium frame and dark graphite silicone strap.",
        "expected_domain": "consumer_electronics",
        "is_vector": False
    },
    {
        "id": "TEST_4_LOUNGE_CHAIR",
        "prompt": "A minimalist wooden lounge chair with curved ergonomic construction.",
        "expected_domain": "furniture",
        "is_vector": False
    },
    {
        "id": "TEST_5_MOUNTAIN_SUNSET",
        "prompt": "A realistic mountain landscape at sunset with a lake in the foreground.",
        "expected_domain": "landscape_nature",
        "is_vector": False
    },
    {
        "id": "TEST_6_ELECTRIC_MOTORCYCLE",
        "prompt": "A modern electric motorcycle with aerodynamic bodywork and realistic proportions.",
        "expected_domain": "vehicle",
        "is_vector": False
    }
]

def test_full_pipeline_benchmark_suite():
    asyncio.run(_run_benchmark_suite())

async def _run_benchmark_suite():
    generated_image_paths = []

    for test_case in BENCHMARK_PROMPTS:
        print(f"\n--- Executing {test_case['id']} ---")
        prompt = test_case["prompt"]

        # 1. Prompt Understanding
        tu_res = task_understanding_agent.analyze(TaskUnderstandingRequest(prompt=prompt))
        assert tu_res.product_category == test_case["expected_domain"], (
            f"Expected {test_case['expected_domain']}, got {tu_res.product_category}"
        )

        # 2. Prompt Refinement
        ref_res = prompt_refinement_agent.refine(PromptRefinementRequest(
            original_prompt=prompt,
            task_understanding=tu_res
        ))
        assert len(ref_res.full_positive_prompt) >= len(prompt)
        assert len(ref_res.negative_prompt) > 10
        assert len(ref_res.alternatives) == 3

        # 3. Dynamic Image Generation
        gen_req = ImageGenerationRequest(
            prompt=ref_res.full_positive_prompt,
            negative_prompt=ref_res.negative_prompt,
            num_images=1,
            width=512,
            height=512,
            seed=42
        )
        gen_res = await image_generation_agent.generate(gen_req)
        assert gen_res.success is True
        assert len(gen_res.generations) == 1

        img_item = gen_res.generations[0]
        assert img_item.image_url.startswith("/api/static/generations/")

        # Verify physical file on disk
        local_filename = img_item.image_url.replace("/api/static/generations/", "")
        local_filepath = os.path.join(image_generation_agent.output_dir, local_filename)
        assert os.path.exists(local_filepath), f"File {local_filepath} does not exist"
        assert os.path.getsize(local_filepath) > 500, f"File {local_filepath} is too small"

        # Verify image can be parsed by PIL and is not blank
        with Image.open(local_filepath) as img:
            assert img.size[0] >= 512
            assert img.size[1] >= 512
            extrema = img.getextrema()
            is_blank = all(c_min == c_max for c_min, c_max in extrema)
            assert not is_blank, f"Image {local_filepath} is a blank canvas!"

        # 4. Evaluation
        eval_res = visual_evaluation_agent.evaluate(ImageEvaluationRequest(
            generation_id=img_item.generation_id,
            image_url=img_item.image_url,
            prompt=prompt
        ))
        assert eval_res.clip_similarity >= 0.80
        assert eval_res.prompt_adherence_score >= 70.0

        generated_image_paths.append(local_filepath)

    # 5. Verify distinct images generated
    assert len(set(generated_image_paths)) == len(BENCHMARK_PROMPTS), (
        "Generated image paths must be unique for each benchmark test!"
    )
    print(f"\nAll {len(BENCHMARK_PROMPTS)} benchmark tests completed successfully with distinct non-blank images!")
