import json
from pathlib import Path
from itertools import cycle

def load_templates(folder="templates"):
    templates = []
    template_folder = Path(folder)
    for file_path in template_folder.glob("*.txt"):
        with open(file_path, 'r') as file:
            templates.append(file.read().strip())
    return templates

def load_main_data(file_name="data/data.json"):
    with open(file_name, 'r') as file:
        if file_name.endswith('.json'):
            return json.load(file)
        else:
            return [json.loads(line) for line in file]

def load_supporting_data(folder="data"):
    supporting_data = {}
    data_folder = Path(folder)
    for file_path in data_folder.glob("*"):
        if file_path.name not in ["data.json", "data.jsonl"]:
            key_name = file_path.stem
            with open(file_path, 'r') as file:
                if file_path.suffix == '.json':
                    supporting_data[key_name] = cycle(json.load(file))
                else:
                    supporting_data[key_name] = cycle([json.loads(line) for line in file])
    return supporting_data

def generate_prompts_with_supporting_data(output_file_name="prompts.json"):
    main_data = load_main_data()
    supporting_data = load_supporting_data()
    templates = cycle(load_templates()) # Using cycle to iterate through templates
    
    all_prompts = []
    for item in main_data:
        template = next(templates) # Getting the next template in the cycle
        prompt = template
        main_data_unwrapped = {k: str(v) for k, v in item.items()} # Converting all values to strings
        combined_data = {**main_data_unwrapped, **{k: str(next(v)[k]) for k, v in supporting_data.items()}}
        for key, value in combined_data.items():
            prompt = prompt.replace(f'{{{key}}}', value)
        all_prompts.append({"prompt": prompt})

    # Writing the prompts to an indented JSON array
    with open(output_file_name, 'w') as file:
        json.dump(all_prompts, file, indent=4)

if __name__ == "__main__":
    generate_prompts_with_supporting_data()

