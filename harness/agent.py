import os
from dotenv import load_dotenv
from openai import OpenAI
import json
import readline, atexit  # noqa: F401  — enables arrow keys, history, line editing in input()

from harness.tools import registry

HISTORY_FILE = os.path.expanduser("~/.agent_history")

try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass

readline.set_history_length(1000)


load_dotenv()


# MODEL = "gpt-4o-mini"

if os.getenv("KIMI_API_KEY"):
    MODEL = "kimi-k2.6"
    client = OpenAI(
        api_key=os.getenv("KIMI_API_KEY"),
        base_url=os.getenv("KIMI_BASE_URL"),
    )
    EXTRA_BODY = {"thinking": {"type": "disabled"}}
else:
    MODEL = "gpt-4o-mini"
    client = OpenAI()  # Reads OPENAI_API_KEY from environment, default base URL.
    EXTRA_BODY = {}

# client = OpenAI()

SYSTEM_PROMPT = """
    You are a coding assistant running in a terminal, helping a developer with software engineering tasks.

    Be concise. Prefer short, direct answers over long ones. When the user asks for code, return the code with minimal explanation unless they ask for more.

    When returning code, use fenced code blocks and specify the language.

    You have access to five filesystem tools — read, write, list_dir, mkdir, delete — operating on a workspace directory. Use them whenever a task involves reading, modifying, or organizing files. Paths are relative to
    the workspace root. Prefer reading and writing real files over describing them in conversation.

    You also have git tools — git_status, and more
"""

def run():
    """Run the agent's conversation loop until user quits. """

    # The conversation history
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    print("Agent ready. Type 'quit' or 'exit' to leave. \n")

    while True:

        # 1. Get user input
        user_input = input("You > ").strip()

        # 2. Allow user exit
        if user_input in {"quit", "exit"}:
            print("GoodBye")
            break
       
        # Skip empty lines
        if not user_input:
            continue

        # 3. Append user message to history
        messages.append({
            "role": "user",
            "content": user_input
        })

        # 4. Call the model, running any requested tools, until it gives a final reply
        while True:
            response = client.chat.completions.create(model=MODEL, messages=messages, tools=registry.get_schemas())
            msg = response.choices[0].message
            messages.append(msg)
            if not msg.tool_calls:
                break
            for call in msg.tool_calls:
                result = registry.dispatch(call.function.name, json.loads(call.function.arguments))
                messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

        print(f"\nagent > {msg.content}\n")

if __name__ == "__main__":
    run()