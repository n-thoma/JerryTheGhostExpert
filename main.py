"""
Module Name: main.py
Description: 
Author: Nathaniel Thoma
Date: 2025-12-19
"""

import parse_ghosts
import parse_ghost_general
import parse_equipment
import parse_equipment_general
import sys

extractors = [
    parse_ghosts.Extractor(),
    parse_ghost_general.Extractor(),
    parse_equipment.Extractor(),
    parse_equipment_general.Extractor()
]

if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = "all"

if arg == "all":
    for extractor in extractors:
        extractor.extract_to_json()
elif arg == "ghosts":
    extractors[0].extract_to_json()
elif arg == "ghost_general":
    extractors[1].extract_to_json()
elif arg == "equipment":
    extractors[2].extract_to_json()
elif arg == "equipment_general":
    extractors[3].extract_to_json()
else:
    print(f"Unknown argument: {arg}")