import os
import json
import asyncio
import aiohttp
import time
import numpy as np

class OpenAI_API:
    MAX_RETRIES = 5
    RETRY_DELAY = 2
    THROUGHPUT_SAMPLES = 10

    def __init__(self):
        self.session = None
        self.throughput = np.zeros(self.THROUGHPUT_SAMPLES)
        self.throughput_index = 0

    async def send_prompt(self, prompt, index, results_queue, inputs_queue):
        base_url = os.getenv('OPENAI_API_BASE')
        url = f"{base_url}/chat/completions"
        headers = self.get_headers()
        data = self.get_data(prompt)
        for retry in range(self.MAX_RETRIES):
            try:
                start_time = time.time()
                result, response_text = await self.post_request(url, headers, data)
                end_time = time.time()
                self.update_throughput(end_time - start_time)
                if self.is_special_response(response_text):
                    continue
                else:
                    await self.handle_normal_response(index, result, prompt, results_queue, inputs_queue)
                break
            except Exception as e:
                print(f'Error sending prompt {index} (retry {retry + 1}):', e)
                if retry == self.MAX_RETRIES - 1:
                    print(f'Failed to process prompt {index} after {self.MAX_RETRIES} retries.')
                    return (index, None)
                await asyncio.sleep(self.RETRY_DELAY ** (retry + 1))

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {os.getenv('OPENAI_API_KEY')}"
        }

    def get_data(self, prompt):
        return {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": prompt["prompt"]
                }
            ]
        }

    async def post_request(self, url, headers, data):
        async with self.session.post(url, headers=headers, json=data) as response:
            result = await response.json()
            return result, json.dumps(result)

    def is_special_response(self, response_text):
        return any(phrase in response_text for phrase in ["%assistant%", "%I'm sorry%", "% AI %", "%language model%", "%I cannot%", "%September 2021%"])

    async def handle_normal_response(self, index, result, prompt, results_queue, inputs_queue):
        print(f'Model output for prompt {index}:', json.dumps(result))
        await results_queue.put((index, result))
        await inputs_queue.put((index, prompt))
        return (index, result)

    def update_throughput(self, elapsed_time):
        self.throughput[self.throughput_index] = 1 / elapsed_time
        self.throughput_index = (self.throughput_index + 1) % self.THROUGHPUT_SAMPLES

    async def process_prompts(self, prompt_generator):
        results_queue = asyncio.Queue()  # Queue to hold results
        inputs_queue = asyncio.Queue()  # Queue to hold indexed inputs

        # Start coroutines to write results and inputs to files
        asyncio.create_task(self.write_to_file(results_queue, 'postapi/complete.jsonl'))
        asyncio.create_task(self.write_to_file(inputs_queue, 'postapi/indexed_inputs.jsonl'))

        async with aiohttp.ClientSession() as self.session:
            batch = []
            for index, prompt in enumerate(prompt_generator):
                batch.append((index, prompt))
                if len(batch) >= self.THROUGHPUT_SAMPLES:
                    await self.process_batch(batch, results_queue, inputs_queue)
                    batch = []
            if batch:
                await self.process_batch(batch, results_queue, inputs_queue)

        # Signal the writers to stop
        await results_queue.put(None)
        await inputs_queue.put(None)

    async def write_to_file(self, queue, file_name):
        with open(file_name, 'w') as f:
            while True:
                item = await queue.get()
                if item is None:
                    break
                f.write(json.dumps(item) + "\n")  # Add newline for valid jsonl formatting

    async def process_batch(self, batch, results_queue, inputs_queue):
        tasks = [self.send_prompt(prompt, index, results_queue, inputs_queue) for index, prompt in batch]
        return await asyncio.gather(*tasks)

def ask_for_generations():
    while True:
        try:
            num_generations = int(input("Please enter the number of generations you want to perform: "))
            return num_generations
        except ValueError:
            print("Invalid input! Please enter an integer value.")

def prompt_generator(num_generations):
    with open('preapi/preapi.jsonl', 'r') as f:
        prompts = [json.loads(line) for line in f][:num_generations]
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



