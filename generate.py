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

def generate_prompts_with_supporting_data():
    main_data = load_main_data()
    supporting_data = load_supporting_data()
    templates = load_templates()
    
    all_prompts = []
    for item in main_data:
        for template in templates:
            prompt = template
            main_data_unwrapped = {k: v if isinstance(v, str) else str(v[k]) for k, v in item.items()}
            combined_data = {**main_data_unwrapped, **{k: str(next(v)[k]) for k, v in supporting_data.items()}}
            for key, value in combined_data.items():
                prompt = prompt.replace(f'{{{key}}}', value)
            all_prompts.append({"prompt": prompt})
            
    return all_prompts

# Example code to generate prompts and save to a file
final_prompts = generate_prompts_with_supporting_data()
output_file_path = 'prompts.jsonl'
with open(output_file_path, 'w') as file:
    for prompt_obj in final_prompts:
        file.write(json.dumps(prompt_obj, indent=4) + '\n')


if __name__ == "__main__":
    generate_prompts_with_supporting_data()


