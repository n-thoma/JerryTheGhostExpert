"""
Module Name: parse_ghosts.py
Description: This module provides utility functions for parsing all ghost data from the Phasmophobia Fandom wiki.
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

    # Parse the first bit of the ghost summary
    def _parse_ghost_summary(self, raw_text):
        data = {}
        
        # 1. Improved regex to capture the full value even if it contains internal pipes
        # It only stops if it sees a pipe followed by a key name and an equals sign
        pattern = r"\|\s*([\w\(\)]+)\s*=\s*(.*?)(?=\s*\|(?:\s*[\w\(\)]+\s*=)|\s*\}\})"
        pairs = re.findall(pattern, raw_text, re.DOTALL)
        
        # Mapping for Phasmophobia Evidence Icons to actual names
        evidence_map = {
            "EMFReader_Render": "EMF Level 5",
            "Fingerprints_3": "Ultraviolet",
            "ClosedBook_Render": "Ghost Writing",
            "SpiritBox_Render": "Spirit Box",
            "DOTTSRender": "D.O.T.S Projector",
            "GhostOrb_Render": "Ghost Orbs",
            "Thermometer_Render": "Freezing Temperatures"
        }

        for key, value in pairs:
            clean_val = value.strip()

            # A. Handle File tags: Extract alt text OR the filename slug
            if "[[File:" in clean_val:
                # First, try to get 'alt' or 'link' text if it exists
                alt_match = re.search(r"(?:alt|link)=([^|\]]+)", clean_val)
                if alt_match:
                    clean_val = alt_match.group(1)
                else:
                    # If no alt text, extract the filename (e.g., EMFReader_Render)
                    file_name_match = re.search(r"File:([^.|\]]+)", clean_val)
                    if file_name_match:
                        slug = file_name_match.group(1)
                        # Use mapping or the slug itself if not in map
                        clean_val = evidence_map.get(slug, slug.replace("_", " "))

            # B. General Cleanup (Remove remaining brackets, bolding, bullet points)
            clean_val = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", clean_val)
            clean_val = clean_val.replace("'''", "").replace("*", "").strip()
            
            # C. Remove leftover partial tags like "24x24px"
            clean_val = re.sub(r"\d+x\d+px", "", clean_val).strip()
            
            data[key] = clean_val

        # Construct the final Ghost Summary object
        evidence_list = [v for k, v in data.items() if k.startswith("Evidence") and v]
        
        result = {
            "Description": data.get("quote", ""),
            "Abilities": data.get("abiliti(es)", ""),
            "Strengths": data.get("strength", ""),
            "Weaknesses": data.get("weakness(es)", ""),
            "Evidence": evidence_list
        }

        return result

    # -----------------------------------------------------------------------------------------------------------------
    # Public Methods
    # -----------------------------------------------------------------------------------------------------------------

    # Main function to parse all ghosts
    def extract_to_json(self):
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
        request = requests.get(URL, params=params)
        res = request.json()
        page = res["query"]["pages"][0]
        content = page["revisions"][0]["slots"]["main"]["content"]

        # Extract ghost names from table
        section_match = re.search(r"==Types of ghosts.*?\{\|(.*?)\|\}", content, re.DOTALL)
        if section_match:
            table_content = section_match.group(1)
            ghost_names = re.findall(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", table_content)
        else:
            print("Could not find the 'Types of ghosts' section in ", request.url)

        # Process each ghost
        all_ghosts_data = []
        for ghost_name in ghost_names:

            params = {
                "action": "query",
                "titles": ghost_name,
                "prop": "revisions",
                "rvprop": "content",
                "rvslots": "main",
                "formatversion": 2,
                "format": "json",
                "origin": "*"
            }

            res = requests.get(URL, params=params).json()
            page = res["query"]["pages"][0]
            content = page["revisions"][0]["slots"]["main"]["content"]

            # Get the parsed Wikicode
            parsed_code = mwparserfromhell.parse(content)

            # Get Ghost Summary
            ghost_summary = self._parse_ghost_summary(str(parsed_code))

            # Get Wiki Hierarchy
            parsed_wiki = GeneralParser.parse_wiki_hierarchy(str(parsed_code))
            unwanted = ["Notes", "References", "History", "Trivia", "Evidence"]
            cleaned_wiki = GeneralParser.filter_sections(parsed_wiki, unwanted)

            # Export to JSON
            final_data = {
                "Ghost Name": ghost_name,
                "Ghost Summary": ghost_summary,
                "Wiki Content": cleaned_wiki
            }

            all_ghosts_data.append(final_data)
            print(f"Processed data for '{ghost_name}'")

        output_dir_name = config.get("OutputFolder", "data")
        output_path = Path(output_dir_name)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "all_ghosts_data.json"
        with open(file_path, 'w') as f:
            json.dump(all_ghosts_data, f, indent=4)

        print("Successfully wrote all ghost data to 'all_ghosts_data.json'")
