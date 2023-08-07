
import os
import json
import asyncio
import aiohttp

BATCH_SIZE = 50
MAX_RETRIES = 5
RETRY_DELAY = 2

class OpenAI_API:
    def __init__(self):
        self.session = None

    async def send_prompt(self, prompt, index, results_queue, inputs_queue):
        base_url = os.environ['OPENAI_API_BASE']
        url = f"{base_url}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {os.environ['OPENAI_API_KEY']}"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt["prompt"]
                }
            ]
        }
        for retry in range(MAX_RETRIES):
            try:
                async with self.session.post(url, headers=headers, json=data) as response:
                    result = await response.json()
                    response_text = json.dumps(result)

                    if any(phrase in response_text for phrase in ["%assistant%", "%I'm sorry%", "% AI %", "%language model%", "%I cannot%", "%September 2021%"]):
                        print(f"Special response detected for prompt {index}")
                        await results_queue.put((index, result))
                        await inputs_queue.put((index, prompt))
                        return (index, result)

                    print(f'Model output for prompt {index}:', response_text)
                    await results_queue.put((index, result))
                    await inputs_queue.put((index, prompt))
                    return (index, result)
            except Exception as e:
                print(f'Error sending prompt {index} (retry {retry + 1}):', e)
                await asyncio.sleep(RETRY_DELAY ** (retry + 1))
        print(f'Failed to process prompt {index} after {MAX_RETRIES} retries.')
        return (index, None)

    async def process_prompts(self, prompt_generator):
        results_queue = asyncio.Queue()  # Queue to hold results
        inputs_queue = asyncio.Queue()  # Queue to hold indexed inputs

        # Start coroutines to write results and inputs to files
        asyncio.create_task(self.write_to_file(results_queue, 'complete.json'))
        asyncio.create_task(self.write_to_file(inputs_queue, 'indexed_inputs.json'))

        async with aiohttp.ClientSession() as self.session:
            batch = []
            for index, prompt in enumerate(prompt_generator):
                batch.append((index, prompt))
                if len(batch) >= BATCH_SIZE:
                    await self.process_batch(batch, results_queue, inputs_queue)
                    batch = []
            if batch:
                await self.process_batch(batch, results_queue, inputs_queue)

        # Signal the writers to stop
        await results_queue.put(None)
        await inputs_queue.put(None)

    async def write_to_file(self, queue, file_name, buffer_size=100):
        with open(file_name, 'w') as f:
            f.write("[\n")
            buffer = []
            while True:
                item = await queue.get()
                if item is None and buffer:
                    f.write(",\n".join(buffer))
                    break
                buffer.append(json.dumps(item))
                if len(buffer) >= buffer_size:
                    f.write(",\n".join(buffer))
                    buffer = []
            f.write("\n]\n")

    async def process_batch(self, batch, results_queue, inputs_queue):
        tasks = [self.send_prompt(prompt, index, results_queue, inputs_queue) for index, prompt in batch]
        return await asyncio.gather(*tasks)

def ask_for_generations():
    try:
        num_generations = int(input("Please enter the number of generations you want to perform: "))
        return num_generations
    except ValueError:
        print("Invalid input! Please enter an integer value.")
        return ask_for_generations()

def prompt_generator(num_generations):
    with open('prompts.json', 'r') as f:
        prompts = json.load(f)[:num_generations]
        for prompt in prompts:
            yield prompt

def main():
    api = OpenAI_API()
    num_generations = ask_for_generations()
    try:
        asyncio.run(api.process_prompts(prompt_generator(num_generations)))
    except Exception as e:
        print('An error occurred:', e)

if __name__ == "__main__":
    main()
