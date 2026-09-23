import os
import sys
import json
import subprocess
from openai import OpenAI

def run_shell(command: str) -> str:
    # Block broad recursive discovery that crawls the home drive
    if "pytest" in command and "--collect-only" in command:
        command = "python -m unittest discover -s . -p 'test_*.py'"

    print(f"\n⚡ [EXECUTING COMMAND]: {command}")
    try:
        res = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15  # Hard safety timeout
        )
        out = res.stdout.strip()
        err = res.stderr.strip()
        return f"STDOUT:\n{out}\nSTDERR:\n{err}\nEXIT_CODE: {res.returncode}"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 15 seconds. Broad disk crawls are restricted."

def write_workspace_file(filename: str, content: str) -> str:
    print(f"\n📝 [WRITING FILE]: {filename}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Successfully wrote {len(content)} characters to {filename}."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Execute a shell command locally in the workspace. Avoid root directory sweeps.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to execute."}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_workspace_file",
            "description": "Create or overwrite a file in the workspace directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string", "description": "Name of the file."},
                    "content": {"type": "string", "description": "Raw text/code to write into the file."}
                },
                "required": ["filename", "content"]
            }
        }
    }
]

def run_operator(objective: str):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY is not set.")
        return

    client = OpenAI(api_key=api_key)
    print(f"🎯 Starting Autonomous Operator Task: '{objective}'\n")

    messages = [
        {
            "role": "system",
            "content": (
                "You are an Autonomous Systems Engineer running on James's Mac. "
                "Always run unit tests using 'python -m unittest discover -s . -p \"test_*.py\"'. "
                "Never run raw pytest or wide glob searches across the root directory. "
                "Execute necessary shell commands, inspect results, and report back when finished."
            )
        },
        {"role": "user", "content": objective}
    ]

    for step in range(5):
        print(f"🤖 [Agent Operator Step {step + 1}] Processing...")
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        msg = res.choices[0].message
        messages.append(msg)

        if msg.tool_calls:
            for call in msg.tool_calls:
                fn_name = call.function.name
                args = json.loads(call.function.arguments)

                if fn_name == "run_shell":
                    result = run_shell(args["command"])
                elif fn_name == "write_workspace_file":
                    result = write_workspace_file(args["filename"], args["content"])
                else:
                    result = "Unknown function call"

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": result
                })
        else:
            print(f"\n✅ [Operator Completed Task]:\n{msg.content}\n")
            break

if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Check git status, check disk space, and verify unit tests"
    run_operator(task)
