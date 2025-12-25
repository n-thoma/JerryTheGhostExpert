"""
Module Name: parse_ghost_general.py
Description: This module provides utility functions for parsing the ghost general data from the Phasmophobia Fandom wiki.
Author: Nathaniel Thoma
Date: 2025-12-19
"""

from pathlib import Path
import requests
import mwparserfromhell
import json
import re
from general_parser import GeneralParser

class Extractor():

    def __init__(self):
        pass

    # Main function to parse all ghosts
    def extract_to_json(self, output_dir, url):
        params = {
            "action": "query",
            "titles": "Ghost",
            "prop": "revisions",
            "rvprop": "content",
            "rvslots": "main",
            "formatversion": 2,
            "format": "json",
            "origin": "*"
        }

        # Fetch the page content
        request = requests.get(url, params=params)
        res = request.json()
        page = res["query"]["pages"][0]
        content = page["revisions"][0]["slots"]["main"]["content"]

        # Get the parsed Wikicode
        parsed_code = mwparserfromhell.parse(content)

        # Get Wiki Hierarchy
        parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
        unwanted = ["See also", "References", "Trivia", "Evidence"]
        cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

        # Export to JSON
        final_data = {
            "Wiki Content": cleaned_wiki
        }

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "general_ghost_data.json"
        with open(file_path, 'w') as f:
            json.dump(final_data, f, indent=4)

        print("Successfully wrote general ghost data to 'general_ghost_data.json'")
