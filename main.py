"""
Module Name: main.py
Description: 
Author: Nathaniel Thoma
Date: 2025-12-19
"""

import json
import sys
import importlib.util
from pathlib import Path

# ---------------------------------------------------------------------------------------------------------------------
# Initializes the parsing
# ---------------------------------------------------------------------------------------------------------------------

parsers = []

with open('config.json', 'r') as f:
    data = json.load(f)

file_paths = data.get("ParserModules")
class_name = data.get("ParserClassName")

if not file_paths or not class_name:
    raise ValueError("config.json is missing ParserModules[] or ParserClass Name")

for file_path in file_paths:
    parser_path = Path(file_path).resolve()

    if not parser_path:
        raise FileNotFoundError(f"The file {file_path} does not exist")
    print(f"Found file {file_path}")

    parser_module_name = parser_path.stem

    parser_spec = importlib.util.spec_from_file_location(parser_module_name, file_path)
    if not parser_spec:
        raise ImportError(f"Could not import module specification for {file_path}")
    
    parser_module = importlib.util.module_from_spec(parser_spec)
    sys.modules[parser_module_name] = parser_module
    parser_spec.loader.exec_module(parser_module)

    try:
        parser_class = getattr(parser_module, class_name)
        parsers.append(parser_class())
    except AttributeError:
        raise AttributeError(f"Class {class_name} has not been found in {parser_module_name}")


if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = "none"

if arg == "parse_all":
    for parser in parsers:
        parser.extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
elif arg == "parse_none":
    print("Running code without updating parsing")
elif arg == "parse_ghosts":
    parsers[0].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
elif arg == "parse_ghost_general":
    parsers[1].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
elif arg == "parse_equipment":
    parsers[2].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
elif arg == "parse_equipment_general":
    parsers[3].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
else:
    print(f"Unknown argument: {arg}")

# ---------------------------------------------------------------------------------------------------------------------
# Initializes OpenAI
# ---------------------------------------------------------------------------------------------------------------------
