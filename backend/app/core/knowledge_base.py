from typing import Dict, Any, List, Optional
import re

# Comprehensive Engineering & Design Knowledge Base
# Structured across 10 essential visual-engineering dimensions:
# 1. Subject identity
# 2. Mechanical structure & assemblies
# 3. Materials & surface treatments
# 4. Geometry, shape & proportions
# 5. Component positioning & arrangement
# 6. Lighting, highlights & shadows
# 7. Camera perspective & composition
# 8. Background & realistic environment
# 9. Visual style & rendering fidelity (tuned for SD 1.5)
# 10. Realistic engineering details & negative exclusions

DOMAIN_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "cnc_machine": {
        "domain": "industrial_machinery",
        "patterns": [r"\bcnc\b", r"\bcnc\s+machine\b", r"\bmilling\s+machine\b", r"\bmachining\s+center\b", r"\bmachining\s+centre\b", r"\bcnc\s+mill\b", r"\blathe\b", r"\b5-axis\b"],
        "display_name": "Industrial CNC Machining Center",
        "core_subject": "(industrial CNC vertical machining center:1.35), 5-axis CNC milling machine with front door open revealing brightly illuminated machining interior",
        "mechanical_structure": "(vertical cutting spindle head:1.25), spinning metal cutting end mill tool chucked in spindle, (slotted steel T-slot milling bed:1.25), heavy steel machine vise clamping metal workpiece block, rotary automatic tool changer carousel with tool holders, dual flexible segmented blue coolant nozzles",
        "materials": "heavy cast iron machine tool base, milled ground steel coordinate worktable, tempered safety glass sliding door frame, industrial blue and gray protective enclosure with open front access",
        "proportions_geometry": "three-dimensional industrial machine-tool geometry, heavy rigid footprint with integrated swarf and chips collection tray",
        "component_arrangement": "vertical spindle head positioned directly over the slotted T-slot worktable and machine vise, side-mounted swing-arm CNC digital control pendant with monitor and emergency stop button",
        "lighting": "bright 5500K internal LED chamber workspace illumination casting crisp reflections on spindle tool and steel worktable, soft ambient factory lighting",
        "camera": "eye-level front three-quarter hero perspective looking directly into the open machining chamber, centered framing, sharp focus on spindle and table",
        "environment": "clean industrial precision manufacturing workshop floor, polished concrete, high-tech machine shop setting",
        "visual_style": "professional industrial equipment photograph, 8k resolution, razor-sharp mechanical edges, authentic manufacturing finish",
        "engineering_details": "precision CNC axis markings, flexible black cable drag chains, braided hydraulic lubrication hoses, metal chips tray",
        "negative_exclusions": "(cupboard:1.4), (cabinet:1.4), (wardrobe:1.4), (locker:1.4), closet, refrigerator, kitchen counter, office furniture, server rack, filing cabinet, closed opaque metal doors, blank metal box, flat featureless wall, room partition, reception desk, desk, missing spindle, missing worktable, missing cutting tool, deformed mechanical parts, distorted geometry, blurry details, cartoon, low resolution"
    },
    "robotic_arm": {
        "domain": "robotics",
        "patterns": [r"\brobotic\s+arm\b", r"\bindustrial\s+robot\b", r"\brobot\s+arm\b", r"\bmanipulator\b", r"\barticulated\s+arm\b", r"\bcobot\b"],
        "display_name": "6-Axis Industrial Robotic Arm",
        "core_subject": "(industrial robotic arm:1.35), 6-axis heavy articulated industrial robot arm in dynamic reaching pose",
        "mechanical_structure": "(multi-jointed articulated arm with rotating joints and high-torque servo motors:1.25), (two-jaw mechanical parallel pneumatic gripper end-effector:1.25), counterbalanced rotating shoulder turret, articulated elbow linkage, multi-axis wrist module",
        "materials": "bright industrial safety yellow and orange cast aluminum arm segments, stainless steel joint pins, flexible black ribbed polyurethane energy chain cable conduit",
        "proportions_geometry": "slender high-reach articulated geometry, rigid circular steel mounting pedestal base firmly bolted to factory floor plate",
        "component_arrangement": "heavy round bolted base flange on floor, vertical rotating pedestal, articulated upper arm and forearm extending forward with gripper open",
        "lighting": "directional industrial lighting, edge rim reflections tracing joint contours, diffused fill light",
        "camera": "three-quarter perspective angle hero shot, dynamic work pose, eye-level framing, deep focus",
        "environment": "modern automated smart factory manufacturing cell, safety barrier marking on epoxy floor, clean production cell",
        "visual_style": "photorealistic industrial automation photography, 8k resolution, tack sharp detail, immaculate manufacturing finish",
        "engineering_details": "flexible black cable drag chain routed along elbow and shoulder, LED status indicator on wrist, laser etched joint axis angles",
        "negative_exclusions": "humanoid robot, android, human face, eyes, legs, toy, plastic toy, cartoon, 3d printer, cabinet, cupboard, desk, stationary pole, disconnected arm, floppy rubber limb, deformed joints, distorted geometry, low resolution, blurry"
    },
    "hydraulic_press": {
        "domain": "industrial_machinery",
        "patterns": [r"\bhydraulic\s+press\b", r"\bforging\s+press\b", r"\bstamping\s+press\b", r"\bforming\s+press\b", r"\bpress\b"],
        "display_name": "Heavy-Duty Industrial Hydraulic Press",
        "core_subject": "(heavy-duty industrial hydraulic press:1.35), 4-column vertical steel forging and stamping press",
        "mechanical_structure": "(massive central vertical hydraulic cylinder ram piston:1.3), polished hard chrome piston rod pressing downward, (heavy steel sliding ram bolster plate:1.25), thick slotted steel press bed table with precision lower forming die",
        "materials": "industrial teal and machine gray enamel finish, mirror-polished hard chrome cylinder rod, precision ground cast steel bolster plates, braided high-pressure steel hydraulic hoses",
        "proportions_geometry": "massive vertical rectangular footprint, 4 heavy cylindrical solid steel tie-rod columns, high mechanical rigidity and structural symmetry",
        "component_arrangement": "top-mounted hydraulic pump manifold reservoir on crown, vertical central piston ram pressing downward toward lower bolster bed, dual analog pressure gauge dials and dual palm cycle-start pushbuttons",
        "lighting": "dramatic industrial commercial lighting, metallic rim light along cylindrical chrome ram rod, soft floor shadows",
        "camera": "straight-on slightly low-angle perspective emphasizing structural power and scale, centered framing",
        "environment": "clean industrial metal stamping and forging facility, heavy reinforced industrial floor, manufacturing plant setting",
        "visual_style": "ultra-realistic industrial machinery photograph, 8k resolution, razor-sharp steel edges, authentic heavy engineering aesthetic",
        "engineering_details": "dual analog pressure dial gauges with PSI scale, heavy hex bolt connections, hydraulic manifold valve block, optical safety light curtain sensors",
        "negative_exclusions": "(cabinet:1.4), (cupboard:1.4), (wardrobe:1.4), (refrigerator:1.4), 3d printer, laser engraver, drill press, lathe, small desktop tool, office furniture, wooden frame, household appliance, flat closed box, blurry gauges, deformed piston, distorted columns, cartoon, low resolution"
    },
    "electric_motor": {
        "domain": "industrial_machinery",
        "patterns": [r"\belectric\s+motor\b", r"\binduction\s+motor\b", r"\bbrushless\s+motor\b", r"\bstepper\s+motor\b", r"\bmotor\b"],
        "display_name": "Industrial High-Efficiency Electric Motor",
        "core_subject": "(industrial electric motor:1.4), (heavy-duty three-phase AC induction electric motor:1.35), complete standalone industrial motor",
        "mechanical_structure": "horizontal cylindrical cast iron stator housing with deep longitudinal cooling heat sink fins, (turned cylindrical ground steel drive shaft with keyway slot:1.3) extending forward from front circular flange, stamped metal cooling fan shroud cover on rear non-drive end",
        "materials": "durable industrial blue enamel coating, precision turned stainless steel drive shaft, cast iron stator frame, brass grounding terminals",
        "proportions_geometry": "cylindrical radial body with prominent cooling fins, rigid cast iron mounting foot base with four bolt holes resting on floor",
        "component_arrangement": "horizontal shaft orientation, drive-end flange with bolt mounting holes, weatherproof electrical conduit connection terminal box mounted directly on top of stator",
        "lighting": "clean industrial studio product lighting with specular grazing highlights across cooling fins, sharp reflection along steel shaft",
        "camera": "side three-quarter hero angle product catalog photograph, shallow depth of field, sharp focus on front shaft and fin contours",
        "environment": "neutral studio cyclorama infinity background in warm gray, clean reflective ground plane",
        "visual_style": "precision commercial product photography, immaculate industrial engineering showcase, 8k resolution, razor-sharp mechanical edges",
        "engineering_details": "precision milled shaft keyway slot, rating plate with technical electrical specifications, ventilation fan shroud on non-drive end",
        "negative_exclusions": "animal, squirrel, rodent, pet, creature, fur, face, eyes, (cabinet:1.4), (cupboard:1.4), internal combustion engine, spark plugs, car engine, pistons, vehicle, pump, fan blade without motor, blurry fins, deformed shaft, distorted geometry, low resolution, cartoon"
    },
    "conveyor_system": {
        "domain": "industrial_machinery",
        "patterns": [r"\bconveyor\b", r"\bconveyor\s+system\b", r"\bbelt\s+conveyor\b", r"\broller\s+conveyor\b", r"\bassembly\s+line\b"],
        "display_name": "Modular Industrial Conveyor System",
        "core_subject": "automated modular industrial belt conveyor transport system",
        "mechanical_structure": "structural extruded anodized aluminum profile bed with T-slots, high-torque integrated gearmotor drive roller assembly, continuous heavy-duty vulcanized textured rubber belt, adjustable stainless steel side guide rails, welded tubular steel support stands with leveling feet",
        "materials": "matte natural anodized 6061-T6 aluminum extrusion, textured matte black synthetic rubber belt, stainless steel hardware, bright safety yellow drive chain guards",
        "proportions_geometry": "elongated linear profile, modular sectional construction, sturdy low-vibration tripod support legs",
        "component_arrangement": "head drive roller with electric motor gearbox, tensioning tail roller at far end, intermediate support legs spaced evenly, adjustable lateral guide brackets along bed edges",
        "lighting": "uniform diffused industrial facility lighting, subtle linear highlights along aluminum profile channels, crisp shadow underneath belt",
        "camera": "three-quarter perspective looking down the length of the conveyor line, wide focal length creating depth, clean horizon",
        "environment": "modern automated logistics fulfillment warehouse or clean electronics packaging facility, polished concrete floor, organized background",
        "visual_style": "sharp commercial industrial photography, high-clarity engineering render, 8k resolution, crisp structural lines",
        "engineering_details": "photoelectric optical presence sensors mounted on brackets, emergency pull-cord switch along side, digital speed controller module",
        "negative_exclusions": "twisted belt, broken rollers, sagging frame, disconnected legs, debris, spilled liquids, warped aluminum, blurry structure, outdoor elements, trees, messy room, low poly, watermark, text"
    },
    "smartwatch": {
        "domain": "consumer_electronics",
        "patterns": [r"\bsmartwatch\b", r"\bwatch\b", r"\bdigital\s+watch\b", r"\bwearable\b", r"\btimepiece\b"],
        "display_name": "Premium Futuristic Smartwatch",
        "core_subject": "premium futuristic standalone smartwatch with circular display",
        "mechanical_structure": "precision CNC-machined aerospace grade titanium unibody case, ultra-sharp circular high-contrast AMOLED display, tactile knurled digital crown wheel, physical haptic feedback button, ceramic backplate with multi-channel biosensor optical array",
        "materials": "micro-brushed grade 5 titanium bezel, anti-reflective sapphire crystal cover glass, dark graphite textured fluoroelastomer silicone strap, polished ceramic sensor lens",
        "proportions_geometry": "sleek circular watch case with chamfered lug transitions, balanced ergonomic curvature fitting human wrist anatomy",
        "component_arrangement": "centered circular watch face showing refined minimalist UI metrics, knurled crown dial at 3 o'clock position, seamless strap integration at top and bottom lugs",
        "lighting": "calibrated studio softbox illumination, dynamic edge rim lighting emphasizing brushed titanium curvature, subtle display screen luminescence",
        "camera": "centered macro hero product photograph, isometric angled perspective, crisp focal plane across dial face",
        "environment": "clean minimalist studio infinity backdrop in neutral dark slate gray, gentle contact shadow on non-reflective ground plane",
        "visual_style": "high-end industrial design product showcase, immaculate Apple/Bang&Olufsen aesthetic, 8k resolution, photorealistic commercial render",
        "engineering_details": "micro-machined knurling on button, precision sensor optical ring, crisp display micro-contrast, magnetic quick-release strap lugs",
        "negative_exclusions": "analog watch hands with gears, mechanical clockwork, wrist, hairy arm, human body, multiple watches, room clutter, lamps, blurry screen, scratches, deformed bezel, low resolution, watermark, text"
    },
    "electric_vehicle": {
        "domain": "vehicle",
        "patterns": [r"\belectric\s+vehicle\b", r"\belectric\s+car\b", r"\bev\b", r"\belectric\s+motorcycle\b", r"\bsuperbike\b", r"\bhypercar\b", r"\bcar\b", r"\bmotorcycle\b"],
        "display_name": "Modern Aerodynamic Electric Vehicle",
        "core_subject": "futuristic high-performance electric vehicle with aerodynamic bodywork",
        "mechanical_structure": "lightweight carbon composite monocoque chassis, aerodynamic wind-tunnel sculpted bodywork, flush aerodynamic door panels, integrated front LED continuous lightbar headlamp, active rear aerodynamic diffuser, aerodynamic lightweight alloy wheels",
        "materials": "multi-coat metallic pearl paint finish with deep clearcoat, exposed woven matte carbon fiber splitters and side skirts, dark tinted panoramic glass roof, forged magnesium alloy rims",
        "proportions_geometry": "low-slung aerodynamic silhouette, aggressive forward stance, wide athletic wheel track, fluid tear-drop roofline",
        "component_arrangement": "single standalone vehicle, centered three-quarter front hero angle, wheels turned slightly toward viewer showcasing rim geometry",
        "lighting": "commercial automotive studio key light, long continuous softbox reflections defining aerodynamic shoulder lines, subtle floor mirror reflection",
        "camera": "low-angle three-quarter front perspective, automotive commercial catalog framing, wide focal length",
        "environment": "dark minimalist automotive studio cyclorama, neutral charcoal gray infinity backdrop, polished dark floor with subtle reflection, zero other vehicles",
        "visual_style": "hyperrealistic automotive CGI commercial render, immaculate surface reflections, 8k resolution, tack sharp body lines",
        "engineering_details": "regenerative brake calipers visible behind aerodynamic wheel blades, flush ultrasonic sensor cutouts, illuminated brand emblem, high-downforce aero wing",
        "negative_exclusions": "exhaust pipes, muffler, gas cap, radiator grille, combustion engine, distorted wheels, oval tires, multiple cars, street traffic, pedestrians, license plate, blurry bodywork, dented panels, low poly, watermark, text"
    },
    "furniture": {
        "domain": "furniture",
        "patterns": [r"\bchair\b", r"\blounge\s+chair\b", r"\barmchair\b", r"\bsofa\b", r"\btable\b", r"\bdesk\b", r"\bfurniture\b"],
        "display_name": "Minimalist Ergonomic Furniture",
        "core_subject": "minimalist wooden lounge chair with curved ergonomic construction",
        "mechanical_structure": "continuous curved molded plywood ergonomic shell, contoured lumbar backrest and deep seat cradle, slender powder-coated tubular steel leg frame, concealed brass joining fasteners",
        "materials": "natural authentic Scandinavian white oak or walnut veneer with visible open-pore wood grain, smooth satin matte protective lacquer, matte charcoal powder-coated steel legs",
        "proportions_geometry": "sculptural organic curves, low-profile relaxed seating angle, balanced structural stability and visual lightness",
        "component_arrangement": "single standalone chair centered in frame, angled slightly toward camera, graceful sweep from seat to headrest",
        "lighting": "soft diffused 4500K natural studio illumination, gentle wrap-around light revealing wood curvature, soft natural floor contact shadow",
        "camera": "three-quarter eye-level studio perspective, centered composition, calm balanced negative space",
        "environment": "clean neutral architectural studio backdrop in warm off-white, concrete or light hardwood floor, zero distracting room clutter",
        "visual_style": "high-end Scandinavian furniture catalog photography, Architectural Digest aesthetic, 8k resolution, authentic material texture",
        "engineering_details": "visible layered ply edges along contour, precision brass mounting spacers, chamfered edge beveling, felt floor glides on legs",
        "negative_exclusions": "multiple chairs, dining table, room clutter, ceiling lamps, pillows, people, pets, crooked legs, cracked wood, rough splinters, distorted proportions, blurry textures, watermark, text"
    },
    "landscape_nature": {
        "domain": "landscape_nature",
        "patterns": [r"\blandscape\b", r"\bmountain\b", r"\bsunset\b", r"\blake\b", r"\bforest\b", r"\bocean\b", r"\briver\b", r"\bnature\b"],
        "display_name": "Realistic Natural Landscape",
        "core_subject": "realistic scenic mountain landscape at sunset with pristine alpine lake",
        "mechanical_structure": "rugged natural geological rock formations with snow-dusted peaks, serene mirror-smooth alpine lake in foreground, natural shoreline with scattered granite boulders and evergreen pine trees",
        "materials": "weathered natural granite rock, crystal clear mountain water with subtle surface ripples, deep green pine needles, atmospheric twilight sky",
        "proportions_geometry": "expansive wide panoramic composition, towering mountain range dominating the horizon, tranquil reflective water filling lower foreground",
        "component_arrangement": "foreground shoreline and reflective lake leading into majestic midground mountain ridges with sharp vertical peaks against sunset sky",
        "lighting": "golden hour sunset sunlight, warm amber and rose alpine glow kissing the jagged mountain peaks, soft twilight sky gradient, golden light reflections across water",
        "camera": "wide-angle panoramic landscape photography, eye-level vantage from shoreline, deep focus from foreground stones to distant peaks",
        "environment": "untouched pristine wilderness, clean crisp mountain air, atmospheric haze in valley canyons, serene natural silence",
        "visual_style": "fine-art landscape photography, National Geographic / Hasselblad clarity, 8k resolution, rich vibrant natural color palette",
        "engineering_details": "natural geological rock strata lines, individual tree needle clarity, water surface specular reflections of sunset colors",
        "negative_exclusions": "buildings, houses, cabins, vehicles, roads, power lines, fences, people, trash, urban elements, indoor furniture, oversaturated neon, blurry horizon, low resolution, digital noise, watermark, text"
    },
    "architecture": {
        "domain": "architecture",
        "patterns": [r"\bvilla\b", r"\bhouse\b", r"\bbuilding\b", r"\barchitecture\b", r"\bpavilion\b", r"\bfacade\b"],
        "display_name": "Modern Architectural Concept",
        "core_subject": "photorealistic modern minimalist architectural villa",
        "mechanical_structure": "cantilevered geometric concrete volumes, floor-to-ceiling structural glass curtain walls, integrated timber sun-shading louvers, floating entry steps over shallow reflecting pool",
        "materials": "smooth board-formed architectural concrete, rich warm natural teak timber slats, ultra-clear low-iron architectural glass, dark bronze anodized window mullions",
        "proportions_geometry": "balanced rectilinear volumes, strong horizontal roof planes, harmonious interplay of solid mass and transparent glass voids",
        "component_arrangement": "two-story luxury residence integrated into manicured landscape, interior living spaces visible through glass, cantilevered upper terrace",
        "lighting": "twilight blue hour ambient sky balanced with warm 3000K interior architectural LED strip lighting, linear facade grazing lights, water reflection highlights",
        "camera": "eye-level two-point architectural perspective, straight vertical lines, wide field of view capturing full building envelope and landscaping",
        "environment": "lush contemporary landscape garden, mature specimen trees, clean architectural paving, serene reflecting water feature",
        "visual_style": "architectural photography, ArchDaily / Architectural Digest quality, 8k resolution, razor-sharp geometric edges",
        "engineering_details": "recessed window frames, shadow gap reveals along ceilings, frameless glass balustrades, integrated exterior downlights",
        "negative_exclusions": "crooked walls, floating roofs, poor construction, debris, construction vehicles, distorted perspective, blurry textures, cartoon, chaotic crowds, watermark, text"
    }
}

# Style Presets for Stable Diffusion 1.5
STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "Photorealistic 3D": {
        "positive": "photorealistic 3D render, 8k resolution, octane render, unreal engine 5 render, raytraced ambient occlusion, subsurface scattering, crisp focal clarity",
        "negative": "cartoon, illustration, 2d drawing, painting, sketch, low poly, flat render"
    },
    "Industrial Design Studio": {
        "positive": "professional industrial design studio photograph, commercial product catalog lighting, clean neutral cyclorama infinity backdrop, tack sharp detail, immaculate prototype finish",
        "negative": "domestic clutter, home environment, messy room, amateur lighting, harsh shadows"
    },
    "Technical Engineering": {
        "positive": "precision technical engineering documentation photograph, isometric exploded view aesthetics, micro-machined tolerances, clean industrial illumination, razor-sharp mechanical edges",
        "negative": "artistic blur, bokeh, dreamlike, fantasy, warped geometry, misaligned parts"
    },
    "Minimalist & Clean": {
        "positive": "minimalist aesthetic, Dieter Rams design philosophy, honest materials, clean negative space, balanced composition, soft diffused lighting",
        "negative": "excessive ornamentation, chaotic clutter, over-complicated elements, busy background"
    },
    "Futuristic Concept": {
        "positive": "futuristic industrial concept prototype, cutting-edge high-tech styling, integrated LED accents, aerodynamic fluid surfacing, premium space-age materials",
        "negative": "retro, vintage, antique, steampunk, worn-out, rusted, outdated technology"
    }
}
