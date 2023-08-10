import json
from pathlib import Path
from itertools import cycle
import os

TEMPLATES_FOLDER = "templates"

def load_supporting_data_fixed(input_file_name):
    supporting_data = {}
    with open(input_file_name, 'r') as file:
        for line in file:
            item = json.loads(line)
            for key, value in item.items():
                if key not in supporting_data:
                    supporting_data[key] = [value]
                else:
                    supporting_data[key].append(value)
    for key, values in supporting_data.items():
        supporting_data[key] = cycle(values)
    return supporting_data

def load_templates_debug(folder=TEMPLATES_FOLDER):
    templates = []
    template_folder = Path(folder)
    for file_path in template_folder.glob("*.txt"):
        with open(file_path, 'r') as file:
            templates.append(file.read().strip())
    return templates

def generate_prompts_with_supporting_data_final(input_file_name, supporting_data_file, output_file_name="prompts.jsonl"):
    supporting_data = load_supporting_data_fixed(supporting_data_file)
    templates = cycle(load_templates_debug()) 
    with open(input_file_name, 'r') as input_file, open(output_file_name, 'w') as output_file:
        for line in input_file:
            item = json.loads(line)
            template = next(templates)
            prompt = template
            if not isinstance(item, dict):
                print(f"Unexpected item: {item}")
            else:
                main_data_unwrapped = {k: str(v) for k, v in item.items()}
                combined_data = {**main_data_unwrapped, **{k: str(next(v)) for k, v in supporting_data.items()}}
                for key, value in combined_data.items():
                    prompt = prompt.replace(f'{{{key}}}', value)
                prompt_object = {"prompt": prompt}
                output_file.write(json.dumps(prompt_object) + '\n')

def main():
    # Creating or using the 'data' folder
    data_folder_path = "data"
    os.makedirs(data_folder_path, exist_ok=True)
    
    # Creating or using the 'preapi' folder
    preapi_folder_path = "preapi"
    os.makedirs(preapi_folder_path, exist_ok=True)
    
    # Path to the main input file
    input_jsonl_path = os.path.join(data_folder_path, "data.jsonl")

    # Finding the first .jsonl file (other than the main data file) in the 'data' folder for supporting data
    supporting_data_jsonl_path = None
    for file_name in os.listdir(data_folder_path):
        if file_name.endswith(".jsonl") and file_name != "data.jsonl":
            supporting_data_jsonl_path = os.path.join(data_folder_path, file_name)
            break

    if supporting_data_jsonl_path is None:
        print("No supporting data file found in the 'data' folder.")
        return

    # Output file will be created in the 'preapi' folder
    output_jsonl_path = os.path.join(preapi_folder_path, "preapi.jsonl")

    generate_prompts_with_supporting_data_final(input_jsonl_path, supporting_data_jsonl_path, output_jsonl_path)

if __name__ == "__main__":
    main()
