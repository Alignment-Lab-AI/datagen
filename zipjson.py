import json

def extract_query(prompt):
    query_index = prompt.find("query:")
    if query_index != -1:
        return prompt[query_index + len("query:"):].strip()
    return None

# Reading complete.json
with open('complete.json', 'r') as file:
    complete_data = json.load(file)

# Reading indexed_inputs.json
with open('indexed_inputs.json', 'r') as file:
    indexed_inputs_data = json.load(file)

# Creating a dictionary to hold the indexed inputs by their index number
indexed_inputs_dict = {index: extract_query(content['prompt']) for index, content in indexed_inputs_data}

# Creating the final array by matching the index numbers
final_array = []

for complete_entry in complete_data:
    index, complete_content = complete_entry
    input_value = indexed_inputs_dict.get(index) # Getting the corresponding input by matching the index number
    output_value = complete_content['choices'][0]['message']['content'] # Getting the content value for the 'output' key
    
    # Creating a dictionary with 'input' and 'output' keys
    combined_entry = {
        'input': input_value,
        'output': output_value
    }
    
    final_array.append(combined_entry)

# Saving the final array to a new JSON file
with open('combined_data.json', 'w') as file:
    json.dump(final_array, file, indent=4)

print("Data combined and saved to combined_data.json")

