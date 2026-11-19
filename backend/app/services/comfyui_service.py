import json
import os
import time
import uuid
import requests
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("promptforge.comfyui")

class ComfyUIService:
    """
    ComfyUI Integration Service
    Connects to the local ComfyUI server via its REST API (http://127.0.0.1:8188).
    Handles prompt submission, execution polling, and image retrieval.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = 8188):
        self.base_url = f"http://{host}:{port}"
        self.client_id = str(uuid.uuid4())

    def is_server_running(self) -> bool:
        """Check if local ComfyUI server is accessible."""
        try:
            res = requests.get(f"{self.base_url}/system_stats", timeout=1.5)
            return res.status_code == 200
        except Exception:
            return False

    def get_available_checkpoints(self) -> list:
        """Fetch list of installed models from ComfyUI object info."""
        try:
            res = requests.get(f"{self.base_url}/object_info/CheckpointLoaderSimple", timeout=2.0)
            if res.status_code == 200:
                data = res.json()
                return data.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [[]])[0]
        except Exception as e:
            logger.warning(f"Could not query ComfyUI checkpoints: {e}")
        return []

    def build_sd15_workflow(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 42,
        width: int = 512,
        height: int = 512,
        steps: int = 28,
        cfg: float = 7.5,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Constructs standard Stable Diffusion 1.5 execution graph for ComfyUI.
        Optimized for 4GB VRAM (NVIDIA RTX 2050) using 512x512 resolution, DPMPP_2M Karras, and FP16.
        """
        available = self.get_available_checkpoints()
        ckpt = model_name if (model_name and model_name in available) else (available[0] if available else "v1-5-pruned-emaonly.safetensors")

        return {
            "3": {
                "inputs": {
                    "seed": seed,
                    "steps": steps,
                    "cfg": cfg,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": ckpt
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": width,
                    "height": height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": prompt,
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": negative_prompt or "blurry, low quality, distorted, deformed, watermark",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "PromptForge",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: int = 42,
        width: int = 512,
        height: int = 512,
        steps: int = 25,
        model_name: Optional[str] = None,
        timeout: int = 90
    ) -> Optional[Tuple[bytes, str]]:
        """
        Queues workflow, waits for execution completion, and returns raw image bytes and filename.
        """
        workflow = self.build_sd15_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            width=width,
            height=height,
            steps=steps,
            model_name=model_name
        )

        payload = {
            "prompt": workflow,
            "client_id": self.client_id
        }

        try:
            res = requests.post(f"{self.base_url}/prompt", json=payload, timeout=5)
            if res.status_code != 200:
                logger.error(f"ComfyUI prompt submission failed: {res.text}")
                return None
            data = res.json()
            prompt_id = data.get("prompt_id")
            if not prompt_id:
                return None

            # Poll for completion
            start_time = time.time()
            while time.time() - start_time < timeout:
                time.sleep(1.0)
                h_res = requests.get(f"{self.base_url}/history/{prompt_id}", timeout=5)
                if h_res.status_code == 200:
                    history = h_res.json()
                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        # Node 9 is SaveImage
                        for node_id, node_out in outputs.items():
                            images = node_out.get("images", [])
                            if images:
                                img_info = images[0]
                                filename = img_info["filename"]
                                subfolder = img_info.get("subfolder", "")
                                img_type = img_info.get("type", "output")

                                view_url = f"{self.base_url}/view?filename={filename}&subfolder={subfolder}&type={img_type}"
                                img_res = requests.get(view_url, timeout=10)
                                if img_res.status_code == 200:
                                    return img_res.content, filename
        except Exception as e:
            logger.error(f"ComfyUI generation error: {e}")

        return None

comfyui_service = ComfyUIService()
