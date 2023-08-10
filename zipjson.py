
import jsonlines

def extract_query(prompt):
    query_index = prompt.find("query:")
    if query_index != -1:
        return prompt[query_index + len("query:"):].strip()
    return None

# Reading complete.jsonl
with jsonlines.open('complete.jsonl') as reader:
    complete_data = list(reader)

# Reading indexed_inputs.jsonl
with jsonlines.open('indexed_inputs.jsonl') as reader:
    indexed_inputs_data = list(reader)

# Prompting for minimum number of completion tokens
min_completion_tokens = int(input("Enter the minimum number of completion tokens: "))

# Creating a dictionary to hold the indexed inputs by their index number
indexed_inputs_dict = {index: extract_query(content['prompt']) for index, content in indexed_inputs_data}

# Creating the final array by matching the index numbers
final_array = []

for complete_entry in complete_data:
    index, complete_content = complete_entry
    input_value = indexed_inputs_dict.get(index) # Getting the corresponding input by matching the index number
    
    # Handling cases where the "usage" key is not found
    usage_data = complete_content.get('usage')
    if not usage_data:
        continue

    completion_tokens = usage_data['completion_tokens'] # Getting the completion tokens count from 'usage'

    # Skip entries with completion tokens less than the specified minimum
    if int(completion_tokens) < min_completion_tokens:
        continue

    output_value = complete_content['choices'][0]['message']['content'] # Getting the content value for the 'output' key

    # Creating the entry and appending to the final array
    entry = {
        "index": index,
        "input": input_value,
        "output": output_value
    }
    final_array.append(entry)

# Writing the final array to a JSONL file
with jsonlines.open('final_output.jsonl', 'w') as writer:
    for item in final_array:
        writer.write(item)

print("Processing completed. The final output is saved in final_output.jsonl.")

