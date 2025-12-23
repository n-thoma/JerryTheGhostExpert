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

with open('config.json', 'r') as f:
    config = json.load(f)

URL = "https://phasmophobia.fandom.com/api.php"

class Extractor():

    # -----------------------------------------------------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------------------------------------------------

    def __init__(self):
        pass

    # -----------------------------------------------------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------------------------------------------------

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

        pattern = r'^\|\[\[(?:[^\]|]*\|)?([^\]|]+)\]\]'
        all_equipment_data = []

        # -------------------------------------------------------------------------------------------------------------
        # Starter Equipment
        # -------------------------------------------------------------------------------------------------------------

        starter_equipment_json = []
        if f"==Starter equipment==" in content:
            section = content.split(f"==Starter equipment==")[1]
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

                res = requests.get(URL, params=params).json()
                page = res["query"]["pages"][0]
                local_content = page["revisions"][0]["slots"]["main"]["content"]

                # Get the parsed Wikicode
                parsed_code = mwparserfromhell.parse(local_content)

                # Get Wiki Hierarchy
                parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
                unwanted = ["Notes", "References", "History", "Trivia", "Gallery", "See also"]
                cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

                # Export to JSON
                final_data = {
                    "Equipment Name": equipment_name,
                    "Wiki Content": cleaned_wiki
                }

                starter_equipment_json.append(final_data)
                print(f"Processed data for '{equipment_name}'")

        # -------------------------------------------------------------------------------------------------------------
        # Optional Equipment
        # -------------------------------------------------------------------------------------------------------------

        optional_equipment_json = []
        if f"==Optional equipment==" in content:
            section = content.split(f"==Optional equipment==")[1]
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

                res = requests.get(URL, params=params).json()
                page = res["query"]["pages"][0]
                local_content = page["revisions"][0]["slots"]["main"]["content"]

                # Get the parsed Wikicode
                parsed_code = mwparserfromhell.parse(local_content)

                # Get Wiki Hierarchy
                parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
                unwanted = ["Notes", "References", "History", "Trivia", "Gallery", "See also"]
                cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

                # Export to JSON
                final_data = {
                    "Equipment Name": equipment_name,
                    "Wiki Content": cleaned_wiki
                }

                optional_equipment_json.append(final_data)
                print(f"Processed data for '{equipment_name}'")

        # -------------------------------------------------------------------------------------------------------------
        # Truck Equipment
        # -------------------------------------------------------------------------------------------------------------

        truck_equipment_json = []
        if f"==Truck equipment==" in content:
            section = content.split(f"==Truck equipment==")[1]
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

                res = requests.get(URL, params=params).json()
                page = res["query"]["pages"][0]
                local_content = page["revisions"][0]["slots"]["main"]["content"]

                # Get the parsed Wikicode
                parsed_code = mwparserfromhell.parse(local_content)

                # Get Wiki Hierarchy
                parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
                unwanted = ["Notes", "References", "History", "Trivia", "Gallery", "See also"]
                cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

                # Export to JSON
                final_data = {
                    "Equipment Name": equipment_name,
                    "Wiki Content": cleaned_wiki
                }

                truck_equipment_json.append(final_data)
                print(f"Processed data for '{equipment_name}'")

        # -------------------------------------------------------------------------------------------------------------

        all_equipment_data = {
            "StarterEquipment": starter_equipment_json,
            "OptionalEquipment": optional_equipment_json,
            "TruckEquipment": truck_equipment_json
        }








        output_dir_name = config.get("OutputFolder", "data")
        output_path = Path(output_dir_name)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "all_equipment_data.json"
        with open(file_path, 'w') as f:
            json.dump(all_equipment_data, f, indent=4)

        print("Successfully wrote all equipment data to 'all_equipment_data.json'")