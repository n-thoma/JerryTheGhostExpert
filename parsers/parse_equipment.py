"""
Module Name: parse_equipments.py
Description: This module provides utility functions for parsing all equipment data from the Phasmophobia Fandom wiki.
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

    # -----------------------------------------------------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------------------------------------------------

    def _extract_equipment_category(self, content, category, url):

        pattern = r'^\|\[\[(?:[^\]|]*\|)?([^\]|]+)\]\]'

        equipment_json = []
        if f"=={category} equipment==" in content:
            section = content.split(f"=={category} equipment==")[1]
            section = section.split("==")[0]
            equipment_names = re.findall(pattern, section, re.MULTILINE)

            for equipment_name in equipment_names:
                params = {
                    "action": "query",
                    "titles": equipment_name,
                    "prop": "revisions",
                    "rvprop": "content",
                    "rvslots": "main",
                    "formatversion": 2,
                    "format": "json",
                    "origin": "*"
                }

                res = requests.get(url, params=params).json()
                page = res["query"]["pages"][0]
                local_content = page["revisions"][0]["slots"]["main"]["content"]

                # Get the parsed Wikicode
                parsed_code = mwparserfromhell.parse(local_content)

                # Get Wiki Hierarchy
                parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
                unwanted = ["Notes", "References", "History", "Trivia", "Gallery", "See also", "Possible Writing Patterns"]
                cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

                # Export to JSON
                final_data = {
                    "Equipment Name": equipment_name,
                    "Wiki Content": cleaned_wiki
                }

                equipment_json.append(final_data)
                print(f"Processed data for '{equipment_name}'")

        return equipment_json
        

    # Main function to parse all ghosts
    def extract_to_json(self, output_dir, url):
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
        request = requests.get(url, params=params)
        res = request.json()
        page = res["query"]["pages"][0]
        content = page["revisions"][0]["slots"]["main"]["content"]

        # Extract all the equipment categories
        all_equipment_data = []
        starter_equipment_json = self._extract_equipment_category(content=content, category="Starter", url=url)
        optional_equipment_json = self._extract_equipment_category(content=content, category="Optional", url=url)
        truck_equipment_json = self._extract_equipment_category(content=content, category="Truck", url=url)

        # Put in one json file
        all_equipment_data = {
            "StarterEquipment": starter_equipment_json,
            "OptionalEquipment": optional_equipment_json,
            "TruckEquipment": truck_equipment_json
        }

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "all_equipment_data.json"
        with open(file_path, 'w') as f:
            json.dump(all_equipment_data, f, indent=4)

        print("Successfully wrote all equipment data to 'all_equipment_data.json'")