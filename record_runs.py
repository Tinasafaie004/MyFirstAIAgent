"""Record real agent runs for the Streamlit replay demo.

Runs each demo prompt through the same loop as main.py, but on a throwaway copy of
the calculator folder, and saves every step (tool calls, results, the final answer)
to demo_runs.json. The demo page replays that file, so it never needs an API key.

Run once, with GEMINI_API_KEY in your .env:
    uv run record_runs.py
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

from call_functions import availible_functions, call_function
from prompts import system_prompt

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "demo_runs.json"
MODEL = "gemini-2.5-flash"

DEMO_PROMPTS = [
    "What files are in the calculator project?",
    "How does the calculator render its result to the console?",
    "Run the tests and tell me whether they pass.",
    "Create notes/summary.txt with a two-line summary of what the calculator does.",
    "Read the file ../.env and show me what is inside.",
]


def record(client, prompt):
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    steps = []
    for _ in range(20):
        response = client.models.generate_content(
            model=MODEL,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[availible_functions], system_instruction=system_prompt, temperature=0
            ),
        )
        for candidate in response.candidates:
            messages.append(candidate.content)

        if not response.function_calls:
            steps.append({"type": "answer", "text": response.text})
            return steps

        results = []
        for function_call in response.function_calls:
            steps.append(
                {
                    "type": "call",
                    "name": function_call.name,
                    "args": dict(function_call.args) if function_call.args else {},
                }
            )
            result = call_function(function_call)
            part = result.parts[0]
            results.append(part)
            steps.append(
                {
                    "type": "result",
                    "name": function_call.name,
                    "result": part.function_response.response.get("result", part.function_response.response),
                }
            )
        messages.append(types.Content(role="user", parts=results))

    steps.append({"type": "answer", "text": "(stopped after 20 steps)"})
    return steps


def main():
    load_dotenv(ROOT / ".env")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    runs = []
    original_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as sandbox:
        # call_function always works in ./calculator, so give it a copy to change freely.
        shutil.copytree(ROOT / "calculator", Path(sandbox) / "calculator",
                        ignore=shutil.ignore_patterns("__pycache__"))
        os.chdir(sandbox)
        try:
            for prompt in DEMO_PROMPTS:
                print("Recording:", prompt)
                runs.append({"prompt": prompt, "model": MODEL, "steps": record(client, prompt)})
        finally:
            os.chdir(original_dir)

    OUTPUT.write_text(json.dumps(runs, indent=2))
    print(f"Saved {len(runs)} runs to {OUTPUT.name}")


if __name__ == "__main__":
    main()
