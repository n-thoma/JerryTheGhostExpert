import mwparserfromhell
import re

class GeneralParser:

    def __init__(self):
        pass


    temp_pattern = re.compile(r"\{\{Temperature\|(\d+)(?:\|(\d+))?\}\}")
    def replace_temperature(match):

        def c_to_f(c):
            return c * 9 / 5 + 32

        t1 = int(match.group(1))
        t2 = match.group(2)

        if t2 is None:
            f1 = c_to_f(t1)
            return f"{t1}C ({f1:.0f}F)"
        else:
            t2 = int(t2)
            f1 = c_to_f(t1)
            f2 = c_to_f(t2)
            return f"{t1}-{t2}C ({f1:.1f}-{f2:.0f}F)"

    
    def parse_tables(text):
        """
        Parses Wikitext tables into a structured list of dictionaries.
        Each table includes its caption (if any) and a list of rows/cells.
        """
        parsed = mwparserfromhell.parse(text)
        tables_data = []

        # Find all table tags in the wikicode
        for table in parsed.filter_tags(matches=lambda node: node.tag == "table"):
            table_str = str(table.contents)

            # Extract the headers (sometimes people do it weird so i've set it up for 2 cases)
            titles = re.findall(r"!'''(.*?)'''", table_str)
            if (titles is None) or (len(titles) == 0):
                titles = re.findall(r"!(.*?)\n", table_str)

            # Clean titles (strip whitespace/new lines)
            titles = [t.strip() for t in titles]

            # Extract rows
            rows = table_str.split('|-')[1:]
            table_rows = []

            for row in rows:
                #Extract cells
                cells = re.findall(r"^\|([^-\n].*)$", row, re.MULTILINE)
                if not cells:
                    continue

                # Clean the cell data
                cleaned_cells = []
                for cell in cells:
                    c = re.sub(r"<br\s*/?>", ", ", cell)                # <br>, <br/>, or <br > -> comma
                    c = re.sub(r"\[\[[^|\]]*\|([^\]]+)\]\]", r"\1", c)  # [[Link|Display]] -> Display
                    c = re.sub(r"\[\[([^\]]+)\]\]", r"\1", c)           # [[Display]] -> Display
                    c = GeneralParser.temp_pattern.sub(GeneralParser.replace_temperature, c)
                    c = c.replace("≥", ">=").replace("≤", "<=")


                    cleaned_cells.append(c.strip())

                # Zip headers with cleaned cells into a dictionary
                if len(cleaned_cells) == len(titles):
                    row_dict = dict(zip(titles, cleaned_cells))
                    table_rows.append(row_dict)

            if table_rows:
                tables_data.append(table_rows)

        return tables_data
    

    # Parse the wiki content into a hierarchical structure
    def parse_wiki_hierarchy(raw_text):
        header_regex = r"^(={1,6})\s*(.*?)\s*\1\s*$"
        tokens = re.split(header_regex, raw_text, flags=re.MULTILINE)
        
        def clean_text(text):
            if not text:
                return {"text": "", "tables": []}
            
            # 1. Extract structured table data
            tables = GeneralParser.parse_tables(text)
            
            # 2. Get clean text (stripping tables and markup)
            parsed = mwparserfromhell.parse(text)
            for table in parsed.filter_tags(matches=lambda node: node.tag == "table"):
                try:
                    parsed.remove(table)
                except ValueError:
                    # This triggers if the table was already removed
                    pass
                
            if (tables is None) or (len(tables) == 0):
                return str(parsed.strip_code()).strip()
            else:
                return {
                    "text": str(parsed.strip_code()).strip(),
                    "tables": tables
                }

        # The first token is always the "root" content before any headers
        root = {
            "title": "Root",
            "level": 0,
            "content": clean_text(tokens[0]),
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
    def filter_sections(section, exclude_list):
        exclude_list = [item.lower() for item in exclude_list]
        
        # Filter the subsections first (bottom-up approach)
        section["subsections"] = [
            GeneralParser.filter_sections(sub, exclude_list) 
            for sub in section["subsections"] 
            if sub["title"].lower() not in exclude_list
        ]
        
        # Remove None values (if any) and return the cleaned section
        section["subsections"] = [s for s in section["subsections"] if s is not None]
        
        return section