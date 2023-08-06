
# Prompt Generator Guide

## Introduction

The Prompt Generator crafts customized prompts by merging predefined templates with structured data. The provided example illustrates the complexity and adaptability of the templates, allowing the creation of unique and dynamic prompts.

## Templates

Templates are stored in the `templates` folder and define the blueprint for generating prompts. Placeholders in the templates are replaced with corresponding values from the data files.

### Example Template

Here's an example of a prompt template:

\`\`\`plaintext
ONLY reply as the pythonicpros' or the summarizer from the following prompt.
    EXPLAINPROMPT?orCLARIFY?  NO!
            Procedure:
    ONLY IN-CHARACTER RESPONSES.
Pythonicpro=2 (  ALPHA, BETA )

  Reasoning task: "{instruction} to achieve the output {output}"
    Reasoning type: "{reasoning}"

    Rules:
    ALPHA, BETA = EXPERTS= SCIENTIFIC METHOD=ARTICULATE.
    DISSECT, EXAMPLES over (min.2) ROUNDS until CONCLUSION=DRAWN.
    If FLAWS detected, RECTIFY else, ACKNOWLEDGE, ADJUST. CODESNIPPETS?=True
FORMAT:
Alpha:""

Beta:""

Omega:""
etc
AT END RETURN
final dialogue from

   summarizer:
\`\`\`

This template demonstrates the flexibility of the Prompt Generator, allowing complex structures and multiple sections to be defined. Placeholders such as `{instruction}`, `{output}`, and `{reasoning}` will be replaced with values from the main and supporting data files.

## Data Handling

### Main Data File (`data.json` or `data.jsonl`)

- **Location**: `data` folder.
- **Structure**: Contains key-value pairs.
- **Iteration**: The script processes this file once.

### Supporting Data Files

- **Location**: Additional JSON files in the `data` folder.
- **Cycling**: Accessed cyclically, allowing repeated use.

## Generating Prompts

### Step 1: Define Templates

Create or modify text files in the `templates` folder, using placeholders that correspond to keys in the data files.

### Step 2: Organize Data

Ensure that the main data file and supporting data files contain keys that align with placeholders in the templates.

### Step 3: Execute the Script

Run the script to combine the data and templates into complete prompts:

\`\`\`bash
python generate.py
\`\`\`

## Conclusion

The Prompt Generator is a powerful tool that enables the creation of diverse and tailored prompts. By understanding the intricate templates, data handling, and prompt generation process, users can craft prompts that meet specific requirements and complexities.
