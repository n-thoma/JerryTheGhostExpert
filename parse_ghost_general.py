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

with open('config.json', 'r') as f:
    config = json.load(f)

URL = "https://phasmophobia.fandom.com/api.php"

class Parser():

    # -----------------------------------------------------------------------------------------------------------------
    # Private Methods
    # -----------------------------------------------------------------------------------------------------------------

    # Parse the wiki content into a hierarchical structure
    def _parse_wiki_hierarchy(self, raw_text):
        header_regex = r"^(={1,6})\s*(.*?)\s*\1\s*$"
        tokens = re.split(header_regex, raw_text, flags=re.MULTILINE)
        
        def clean_text(text):
            if not text:
                return ""

            parsed = mwparserfromhell.parse(text)
            return str(parsed.strip_code()).strip()

        # The first token is always the "root" content before any headers
        root = {
            "title": "Root",
            "level": 0,
            "content": "",
            "subsections": []
        }
        stack = [root]
        
        # Iterate through matches (each match is: level_markup, title, content)
        for i in range(1, len(tokens), 3):
            level = len(tokens[i])      # Count of '='
            title = clean_text(tokens[i+1])
            content = clean_text(tokens[i+2])
            
            new_section = {
                "title": title,
                "level": level,
                "content": content,
                "subsections": []
            }
            
            while stack and stack[-1]["level"] >= level:
                stack.pop()
            
            stack[-1]["subsections"].append(new_section)
            stack.append(new_section)

        return root

    # Filter out unwanted sections
    def _filter_sections(self, section, exclude_list):
        exclude_list = [item.lower() for item in exclude_list]
        
        # Filter the subsections first (bottom-up approach)
        section["subsections"] = [
            self._filter_sections(sub, exclude_list) 
            for sub in section["subsections"] 
            if sub["title"].lower() not in exclude_list
        ]
        
        # Remove None values (if any) and return the cleaned section
        section["subsections"] = [s for s in section["subsections"] if s is not None]
        
        return section

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

        # Get the parsed Wikicode
        parsed_code = mwparserfromhell.parse(content)

        # Get Wiki Hierarchy
        parsed_wiki = self._parse_wiki_hierarchy(str(parsed_code))
        unwanted = ["See also", "References", "Trivia", "Evidence"]
        cleaned_wiki = self._filter_sections(parsed_wiki, unwanted)

        # Export to JSON
        final_data = {
            "Wiki Content": cleaned_wiki
        }

        output_dir_name = config.get("OutputFolder", "data")
        output_path = Path(output_dir_name)
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path / "general_ghost_data.json"
        with open(file_path, 'w') as f:
            json.dump(final_data, f, indent=4)

        print("Successfully wrote general ghost data to 'general_ghost_data.json'")
