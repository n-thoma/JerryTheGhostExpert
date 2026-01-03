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
from openai import OpenAI

# ---------------------------------------------------------------------------------------------------------------------
# Initializes the parsing
# ---------------------------------------------------------------------------------------------------------------------

# Dynamically find all parsers given in config.json

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
        parsers.append({"class": parser_class(), "name": parser_module_name})
    except AttributeError:
        raise AttributeError(f"Class {class_name} has not been found in {parser_module_name}")

# Handling parsing argument

if len(sys.argv) > 1:
    arg = sys.argv[1]
else:
    arg = "parse_none"

if arg == "parse_all":
    for parser in parsers:
        parser["class"].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
elif arg == "parse_none":
    print("Running code without updating parsing")
elif len(sys.argv) > 1:
    found = False
    for parser in parsers:
        if arg == parser["name"]:
            found = True
            parser["class"].extract_to_json(data.get("OutputFolder"), data.get("WikiURL"))
    if not found:
        print(f"Invalid argument given: {arg}")

# ---------------------------------------------------------------------------------------------------------------------
# Initializes OpenAI
# ---------------------------------------------------------------------------------------------------------------------

client = OpenAI(api_key=str(data.get("APIKey")))
vector_store = client.vector_stores.create(name="Project Knowledge Base")

data_dir = Path(data.get("OutputFolder"))
file_ids = []

# For every file in the data directory, upload to OpenAI
for file_path in data_dir.glob("*"):
    if file_path.is_file():
            print(f"Uploading: {file_path.name}...")
            
            # Upload file to OpenAI and get file ID
            with open(file_path, "rb") as f:
                uploaded_file = client.files.create(
                    file=f,
                    purpose="assistants"
                )
                file_ids.append(uploaded_file.id)

# If we have files, create a batch to add them to the vector store
if file_ids:
    print(f"Adding {len(file_ids)} files to Vector Store...")
    
    file_batch = client.vector_stores.file_batches.create_and_poll(
      vector_store_id=vector_store.id,
      file_ids=file_ids
    )
    
    print(f"Batch Status: {file_batch.status}")
    print(f"Files successfully indexed: {file_batch.file_counts.completed}")
else:
    print("No files found in the data directory.")

# # List files in the vector store to confirm
# result = client.vector_stores.files.list(vector_store_id=vector_store.id)
# print(result)

# Intialize conversation with system prompt
system_prompt = {
    "role": "system",
    "content": str(data.get("AIPersonality"))
}

conversation = [system_prompt]


# Used to handle chat interactions
def chat(user_input: str):
    global conversation

    # Add user message
    conversation.append({
        "role": "user",
        "content": user_input
    })

    # Call Responses API
    response = client.responses.create(
        model=str(data.get("AIModel")),
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store.id]
        }],
        input=conversation
    )

    # Extract assistant text
    assistant_message = response.output_text

    # Add assistant message back to history
    conversation.append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


# Loop for user input
while True:
    user = input("You: ")
    if user.lower() in ("quit", "exit"):
        break

    reply = chat(user)
    print("Bot:", reply)

