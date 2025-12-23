"""
Module Name: parse_equipment_general.py
Description: This module provides utility functions for parsing the equipment general data from the Phasmophobia Fandom wiki.
Author: Nathaniel Thoma
Date: 2025-12-19
"""

from pathlib import Path
import requests
import mwparserfromhell
import json
import re
from general_parser import GeneralParser

with open('config.json', 'r') as f:
    config = json.load(f)

URL = "https://phasmophobia.fandom.com/api.php"

class Extractor():

    # Main function to parse all ghosts
    def extract_to_json(self):
        params = {
            "action": "query",
            "titles": "Equipment",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "formatversion": 2,
            "format": "json",
            "origin": "*"
        }

        # Fetch the page content
        request = requests.get(URL, params=params)
        res = request.json()
        page = res["query"]["pages"][0]
        content = page["revisions"][0]["slots"]["main"]["content"]

        # Get the parsed Wikicode
        parsed_code = mwparserfromhell.parse(content)

        # Get Wiki Hierarchy
        parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))

        # Export to JSON
        final_data = {
            "Wiki Content": parsed_wiki
        }

        output_dir_name = config.get("OutputFolder", "data")
        output_path = Path(output_dir_name)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "general_equipment_data.json"
        with open(file_path, 'w') as f:
            json.dump(final_data, f, indent=4)

        print("Successfully wrote general equipment data to 'general_equipment_data.json'")
