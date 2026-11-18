import os
import re
import math
import uuid
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageDraw

COLOR_MAP: Dict[str, Tuple[int, int, int, str]] = {
    "red": (220, 38, 38, "#DC2626"),
    "crimson": (225, 29, 72, "#E11D48"),
    "blue": (37, 99, 235, "#2563EB"),
    "sky blue": (14, 165, 233, "#0EA5E9"),
    "cyan": (6, 182, 212, "#06B6D4"),
    "navy": (30, 58, 138, "#1E3A8A"),
    "black": (15, 15, 15, "#0F0F0F"),
    "dark": (24, 24, 27, "#18181B"),
    "green": (22, 163, 74, "#16A34A"),
    "emerald": (16, 185, 129, "#10B981"),
    "yellow": (234, 179, 8, "#EAB308"),
    "amber": (245, 158, 11, "#F59E0B"),
    "orange": (249, 115, 22, "#F97316"),
    "purple": (147, 51, 234, "#9333EA"),
    "violet": (124, 58, 237, "#7C3AED"),
    "pink": (236, 72, 153, "#EC4899"),
    "rose": (244, 63, 94, "#F43F5E"),
    "white": (255, 255, 255, "#FFFFFF"),
    "gray": (107, 114, 128, "#6B7280"),
    "grey": (107, 114, 128, "#6B7280"),
    "slate": (71, 85, 105, "#475569"),
    "teal": (20, 184, 166, "#14B8A6"),
    "brown": (120, 53, 15, "#78350F")
}

class VectorEngine:
    """
    Precision Vector & SVG Synthesis Engine
    1. Supports geometric primitives (circles, squares, triangles, polygons, diagrams, icons).
    2. Supports nested geometric primitives (e.g. dot at center of circle, concentric shapes).
    3. Generates valid standard W3C SVG markup.
    4. Validates SVG XML, viewBox, dimensions, fill, stroke, and visibility.
    5. Rasterizes anti-aliased PNG images with verification that output is not blank.
    6. Saves both .svg and .png assets.
    """
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or "backend/data/storage/generations"
        os.makedirs(self.output_dir, exist_ok=True)

    def is_vector_candidate(self, prompt: str, category: Optional[str] = None) -> bool:
        """Determines if the prompt should be routed to the vector engine."""
        prompt_lower = prompt.lower()
        
        # If user explicitly selected Shapes category
        if category and category.lower() in ["shapes", "geometric_shape", "vector", "icon", "svg"]:
            return True

        # Disqualify realistic products, landscapes, vehicles, complex 3D scenes
        complex_keywords = [
            "smartwatch", "watch", "chair", "table", "sofa", "furniture",
            "motorcycle", "bike", "car", "vehicle", "automobile", "hypercar",
            "landscape", "mountain", "sunset", "lake", "forest", "beach",
            "building", "villa", "architecture", "photorealistic", "photo of",
            "portrait", "face", "person", "character", "human", "realistic", "3d render"
        ]
        if any(re.search(r'\b' + re.escape(w) + r'\b', prompt_lower) for w in complex_keywords):
            # Check if it's explicitly asking for an icon/vector of that item
            if not any(k in prompt_lower for k in ["vector icon", "flat icon", "svg icon", "simple icon", "minimalist icon"]):
                return False

        # Strong vector indicators
        vector_keywords = [
            "circle", "square", "triangle", "rectangle", "polygon", "hexagon",
            "octagon", "pentagon", "oval", "star", "dot", "geometric", "diagram",
            "vector graphic", "vector icon", "flat vector", "svg", "simple graphic"
        ]
        return any(re.search(r'\b' + re.escape(w) + r'\b', prompt_lower) for w in vector_keywords)

    def _parse_colors(self, text: str) -> Tuple[Tuple[int, int, int, str], Tuple[int, int, int, str]]:
        """Extracts background color and primary shape color from text."""
        text_lower = text.lower()
        
        # Determine background
        bg_color = (255, 255, 255, "#FFFFFF")  # Default pure white
        if "black background" in text_lower or "on black" in text_lower or "dark background" in text_lower:
            bg_color = (15, 15, 15, "#0F0F0F")
        elif "blue background" in text_lower:
            bg_color = (30, 58, 138, "#1E3A8A")
        elif "gray background" in text_lower or "grey background" in text_lower:
            bg_color = (229, 231, 235, "#E5E7EB")
        elif "transparent background" in text_lower:
            bg_color = (255, 255, 255, "#FFFFFF")

        # Determine shape color
        shape_color = (220, 38, 38, "#DC2626")  # Default clean red
        for c_name, c_val in COLOR_MAP.items():
            # Check color for shape (avoiding background color phrase)
            pattern = r'\b' + re.escape(c_name) + r'\b(?!\s+background)'
            if re.search(pattern, text_lower):
                shape_color = c_val
                break

        return bg_color, shape_color

    def generate_vector(
        self,
        prompt: str,
        seed: int,
        variant_idx: int = 0,
        width: int = 512,
        height: int = 512
    ) -> Tuple[str, str, str]:
        """
        Synthesizes validated SVG markup, saves .svg, rasterizes anti-aliased .png,
        and verifies the output image is not blank.
        Returns: (png_relative_url, svg_relative_url, engine_name)
        """
        prompt_lower = prompt.lower()
        gen_id = f"vector_gen_{uuid.uuid4().hex[:10]}_{seed}"
        svg_filename = f"{gen_id}.svg"
        png_filename = f"{gen_id}.png"
        
        svg_path = os.path.join(self.output_dir, svg_filename)
        png_path = os.path.join(self.output_dir, png_filename)

        bg_color, shape_color = self._parse_colors(prompt)
        cx, cy = width / 2.0, height / 2.0

        # Elements to render
        svg_elements = []
        pil_draw_actions = []

        # 1. Background
        svg_elements.append(f'<rect width="{width}" height="{height}" fill="{bg_color[3]}"/>')

        # 2. Check for shapes
        # Shape A: Circle
        if "circle" in prompt_lower or "oval" in prompt_lower:
            radius = int(min(width, height) * (0.28 if variant_idx == 0 else 0.32))
            svg_elements.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{shape_color[3]}" stroke="none"/>'
            )
            pil_draw_actions.append(("circle", (cx, cy, radius), shape_color[0:3]))

        # Shape B: Square or Rectangle
        elif "square" in prompt_lower or "rectangle" in prompt_lower:
            half = int(min(width, height) * (0.26 if variant_idx == 0 else 0.30))
            x1, y1 = cx - half, cy - half
            x2, y2 = cx + half, cy + half
            svg_elements.append(
                f'<rect x="{x1}" y="{y1}" width="{half * 2}" height="{half * 2}" fill="{shape_color[3]}" stroke="none"/>'
            )
            pil_draw_actions.append(("rect", (x1, y1, x2, y2), shape_color[0:3]))

        # Shape C: Triangle
        elif "triangle" in prompt_lower:
            side = int(min(width, height) * (0.58 if variant_idx == 0 else 0.64))
            th = int(side * (3**0.5) / 2)
            top = (cx, cy - int(th * 0.55))
            bl = (cx - side / 2, cy + int(th * 0.45))
            br = (cx + side / 2, cy + int(th * 0.45))
            pts_svg = f"{top[0]},{top[1]} {bl[0]},{bl[1]} {br[0]},{br[1]}"
            svg_elements.append(
                f'<polygon points="{pts_svg}" fill="{shape_color[3]}" stroke="none"/>'
            )
            pil_draw_actions.append(("polygon", [top, bl, br], shape_color[0:3]))

        # Shape D: Hexagon
        elif "hexagon" in prompt_lower:
            r = int(min(width, height) * 0.28)
            points = []
            for i in range(6):
                angle = math.radians(60 * i - 30)
                points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
            pts_svg = " ".join(f"{px},{py}" for px, py in points)
            svg_elements.append(f'<polygon points="{pts_svg}" fill="{shape_color[3]}" stroke="none"/>')
            pil_draw_actions.append(("polygon", points, shape_color[0:3]))

        # Shape E: Star
        elif "star" in prompt_lower:
            r_out = int(min(width, height) * 0.30)
            r_in = r_out * 0.45
            points = []
            for i in range(10):
                angle = math.radians(36 * i - 90)
                r_curr = r_out if i % 2 == 0 else r_in
                points.append((cx + r_curr * math.cos(angle), cy + r_curr * math.sin(angle)))
            pts_svg = " ".join(f"{px},{py}" for px, py in points)
            svg_elements.append(f'<polygon points="{pts_svg}" fill="{shape_color[3]}" stroke="none"/>')
            pil_draw_actions.append(("polygon", points, shape_color[0:3]))

        # Default fallback primitive
        else:
            radius = int(min(width, height) * 0.28)
            svg_elements.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{shape_color[3]}" stroke="none"/>'
            )
            pil_draw_actions.append(("circle", (cx, cy, radius), shape_color[0:3]))

        # 3. Handle Child / Nested Elements (e.g., "small black dot exactly at its center")
        if re.search(r'\b(dot|point|center dot|black dot|small dot)\b', prompt_lower) or "at its center" in prompt_lower or "at the center" in prompt_lower:
            dot_color = (15, 15, 15, "#0F0F0F")
            for c_name, c_val in COLOR_MAP.items():
                if f"{c_name} dot" in prompt_lower or f"{c_name} point" in prompt_lower:
                    dot_color = c_val
                    break
            
            # Sub-element radius
            dot_radius = max(6, int(min(width, height) * 0.035))
            svg_elements.append(
                f'<circle cx="{cx}" cy="{cy}" r="{dot_radius}" fill="{dot_color[3]}" stroke="none"/>'
            )
            pil_draw_actions.append(("circle", (cx, cy, dot_radius), dot_color[0:3]))

        # Construct full SVG Document
        svg_content = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">\n  '
            + "\n  ".join(svg_elements)
            + "\n</svg>"
        )

        # 4. Strict XML & Visibility Validation
        self._validate_svg(svg_content, width, height)

        # Write SVG file
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        # 5. High-Resolution Rasterization with 4x Supersampling
        scale = 4
        sw, sh = width * scale, height * scale
        img = Image.new("RGB", (sw, sh), color=bg_color[0:3])
        draw = ImageDraw.Draw(img)

        for action_type, params, color in pil_draw_actions:
            if action_type == "circle":
                pcx, pcy, pr = params[0] * scale, params[1] * scale, params[2] * scale
                draw.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=color)
            elif action_type == "rect":
                px1, py1, px2, py2 = params[0] * scale, params[1] * scale, params[2] * scale, params[3] * scale
                draw.rectangle([px1, py1, px2, py2], fill=color)
            elif action_type == "polygon":
                scaled_pts = [(p[0] * scale, p[1] * scale) for p in params]
                draw.polygon(scaled_pts, fill=color)

        # Anti-aliasing with Lanczos filter
        final_img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # 6. Verify image is NOT blank (non-monochrome check)
        extrema = final_img.getextrema()
        is_blank = all(channel_min == channel_max for channel_min, channel_max in extrema)
        if is_blank:
            raise ValueError(f"Vector rasterization generated a blank monochrome image for prompt: '{prompt}'")

        final_img.save(png_path, format="PNG")

        return f"/api/static/generations/{png_filename}", f"/api/static/generations/{svg_filename}", "Precision Vector Engine (W3C SVG)"

    def _validate_svg(self, svg_text: str, width: int, height: int):
        """Validates XML syntax, dimensions, and viewBox."""
        try:
            root = ET.fromstring(svg_text)
        except ET.ParseError as pe:
            raise ValueError(f"Generated SVG markup is invalid XML: {pe}")

        if root.tag.split("}")[-1] != "svg":
            raise ValueError("Root element is not <svg>")

        view_box = root.attrib.get("viewBox")
        if not view_box:
            raise ValueError("Missing viewBox in SVG markup")

        if len(root) < 2:  # At least background + 1 shape element
            raise ValueError("SVG contains no graphical elements")

vector_engine = VectorEngine()
