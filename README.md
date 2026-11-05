# Local AI Coding Agent in Python

A command-line AI agent built in Python that uses the Gemini API to answer prompts and interact with local project files through safe tool calls.

## Features
- Multi-turn conversation history
- Gemini API integration
- Function/tool calling
- Read file contents safely
- List files in a working directory
- Run Python files
- Write files
- Verbose mode for debugging

## Live Demo
`app.py` is a Streamlit page that replays real agent runs step by step (each tool call, its result, and the final answer), lets visitors try the working-directory safety guard live, and walks through the agent loop. It never calls Gemini and never writes or runs files, so it needs no API key.

- `record_runs.py` records the runs into `demo_runs.json`, working on a temporary copy of `calculator/` (needs `GEMINI_API_KEY` in `.env`).
- Run the demo locally: `uv run streamlit run app.py`
- Deploy on [Streamlit Community Cloud](https://share.streamlit.io): pick this repository and `app.py`. Dependencies come from `uv.lock`.

## Tech Stack
Python, Google Gemini API, argparse, dotenv, subprocess, unit testing

## What I Learned
- How AI agents use function calling
- How to pass tool results back to the model
- How to protect file access using working directory validation
- How to structure a command-line Python project
