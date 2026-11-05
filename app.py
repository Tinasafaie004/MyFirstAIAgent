"""Live demo of the Local AI Coding Agent.

Replays real recorded runs (demo_runs.json, made by record_runs.py) step by step, and lets
visitors try the path-safety guard live. It never calls Gemini and never writes or runs files,
so the server needs no API key.

Run locally with:  uv run streamlit run app.py
"""

import json
from pathlib import Path

import streamlit as st

from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info

ROOT = Path(__file__).resolve().parent
WORKING_DIR = ROOT / "calculator"
RUNS = json.loads((ROOT / "demo_runs.json").read_text())

TOOL_INFO = {
    "get_files_info": ("List files", "functions/get_files_info.py"),
    "get_file_content": ("Read a file", "functions/get_file_content.py"),
    "write_file": ("Write a file", "functions/write_file.py"),
    "run_python_file": ("Run a Python file", "functions/run_python_file.py"),
}


def inside_working_dir(path):
    """The same check every tool makes before it touches a file."""
    import os

    working_dir_abs = os.path.abspath(WORKING_DIR)
    target = os.path.normpath(os.path.join(working_dir_abs, path))
    return os.path.commonpath([working_dir_abs, target]) == working_dir_abs, target


def describe_call(step):
    label, _ = TOOL_INFO.get(step["name"], (step["name"], ""))
    args = ", ".join(f"{k}={json.dumps(v)}" for k, v in step["args"].items() if k != "content")
    if "content" in step["args"]:
        args = (args + ", " if args else "") + "content=…"
    return label, f"{step['name']}({args})"


st.set_page_config(page_title="Local AI Coding Agent", layout="wide")

st.title("Local AI Coding Agent")
st.write(
    "A command-line agent I built in Python on the Gemini API. You ask it something about a small "
    "calculator project, and it decides which **tools** to use: list files, read a file, write a file "
    "or run Python. It looks at each result and keeps going until it can answer."
)
st.info(
    "These are real runs, recorded from the agent and replayed here, so this page needs no API key "
    "and cannot change any files. The safety-guard tab runs my real code live.",
    icon=":material/info:",
)

tab_watch, tab_guard, tab_how = st.tabs(["Watch it work", "Try the safety guard", "How it works"])

# --- 1. Replay a recorded run ---------------------------------------------------
with tab_watch:
    prompt = st.selectbox("Pick a question", [run["prompt"] for run in RUNS])
    run = next(r for r in RUNS if r["prompt"] == prompt)
    steps = run["steps"]

    shown = st.slider(
        "Steps shown", 1, len(steps), 1, key=f"steps-{prompt}",
        help="Each step is one tool call, one tool result, or the final answer.",
    )

    with st.chat_message("user"):
        st.write(prompt)

    for step in steps[:shown]:
        if step["type"] == "call":
            label, signature = describe_call(step)
            with st.chat_message("assistant", avatar=":material/smart_toy:"):
                st.markdown(f"**Decides to use a tool:** {label}")
                st.code(signature, language="python")
                if "content" in step["args"]:
                    st.caption("Content it wants to write")
                    st.code(step["args"]["content"], language="text")
        elif step["type"] == "result":
            result = str(step["result"])
            blocked = result.startswith("Error:")
            with st.chat_message("tool", avatar=":material/build:"):
                st.markdown("**Tool result**" + (" (an error the agent has to deal with)" if blocked else ""))
                st.code(result if len(result) < 1500 else result[:1500] + "\n…", language="text")
        else:
            with st.chat_message("assistant", avatar=":material/smart_toy:"):
                st.markdown("**Final answer**")
                st.write(step["text"])

    if shown < len(steps):
        st.caption(f"Step {shown} of {len(steps)}. Move the slider to see what the agent does next.")
    else:
        calls = sum(1 for s in steps if s["type"] == "call")
        st.success(f"Done: {calls} tool call{'s' if calls != 1 else ''}, then an answer. Recorded with {run['model']}.")

# --- 2. The safety guard, live -------------------------------------------------
with tab_guard:
    st.write(
        "Every tool is locked to the `calculator` folder. Before touching a path, it joins it to that "
        "folder, normalises it, and checks that the result is still inside. Try to escape it."
    )
    col_tool, col_path = st.columns([1, 2])
    tool = col_tool.radio("Tool", list(TOOL_INFO), format_func=lambda t: TOOL_INFO[t][0])
    path = col_path.text_input("Path", value="../.env",
                               help="Try pkg/render.py, ., ../main.py, or /etc/passwd")
    col_path.caption("Ideas: `pkg`, `pkg/render.py`, `../.env`, `pkg/../../main.py`, `/etc/passwd`")

    if st.button("Check this path", type="primary"):
        allowed, target = inside_working_dir(path)
        if tool == "get_files_info":
            output = get_files_info(str(WORKING_DIR), path)
        elif tool == "get_file_content":
            output = get_file_content(str(WORKING_DIR), path)
        else:
            output = None

        if allowed:
            st.success("Allowed: this path stays inside the calculator folder.")
        else:
            st.error("Blocked: this path points outside the calculator folder.")

        if output is not None:
            st.caption("What the real tool returned")
            st.code(output if len(output) < 3000 else output[:3000] + "\n…", language="text")
        elif allowed:
            action = "write to" if tool == "write_file" else "run"
            extra = ""
            if tool == "run_python_file" and not path.endswith(".py"):
                extra = " It would still refuse, because only .py files can be run."
            st.caption(f"The agent would be allowed to {action} this path. This demo never does it.{extra}")

# --- 3. How it works -----------------------------------------------------------
with tab_how:
    col_text, col_code = st.columns([2, 3], gap="large")
    with col_text:
        st.subheader("The agent loop")
        st.markdown(
            """
1. Send the question to Gemini, along with a **description of each tool** (its name and inputs).
2. Gemini either answers, or replies with a **function call**: which tool, with which arguments.
3. My code runs that tool, safely inside `calculator/`, and sends the result back.
4. Repeat until Gemini answers in plain text, up to 20 rounds.

The model never touches files itself. It only *asks*, and my Python decides what actually runs.
That is why the safety guard matters: it is the line between what the model wants and what it gets.
"""
        )
    with col_code:
        st.subheader("call_functions.py")
        st.caption("Maps the model's function call to a real Python function, and locks the working directory.")
        st.code((ROOT / "call_functions.py").read_text(), language="python", line_numbers=True)

    st.subheader("One tool, in full")
    pick = st.selectbox("Tool", list(TOOL_INFO), format_func=lambda t: TOOL_INFO[t][0], key="code-tool")
    st.code((ROOT / TOOL_INFO[pick][1]).read_text(), language="python", line_numbers=True)

st.divider()
st.caption("Code on GitHub: [Tinasafaie004/MyFirstAIAgent](https://github.com/Tinasafaie004/MyFirstAIAgent)")
