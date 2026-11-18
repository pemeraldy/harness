import os
from openai import OpenAI
from dotenv import load_dotenv
import readline, atexit  # noqa: F401  — enables arrow keys, history, line editing in input()

load_dotenv()

MODEL = "gpt-4o-mini"

HISTORY_FILE = os.path.expanduser("~/.career_coach_history")

try:
    readline.read_history_file(HISTORY_FILE)
except FileNotFoundError:
    pass

readline.set_history_length(1000)
atexit.register(readline.write_history_file, HISTORY_FILE)

os.getenv("OPENAI_API_KEY")

client = OpenAI()

SYSTEM_PROMPT= """
    You are a career coach with over 15 year grooming industry giants. 
    Your role is to ask question about users 
    current carrier and where they want to be and achieve in the next 90 day. 
    You tailor a daily plan to help them achieve the goal they stated.
"""

def run():
    messsages = [
        {"role": "system", "content":SYSTEM_PROMPT}
    ]

    print("Agent ready. Type 'quit' or 'exit' to leave. \n")

    while True:

        user_input = input("You > ").strip()

        if user_input in {"exit", "quit"}:
            print("Arigato!")
            break
        if not user_input:
            continue

        messsages.append({
            "role": "user",
            "content": user_input
        })

        resp = client.chat.completions.create(
            model=MODEL,
            messages=messsages
        )

        coach_message = resp.choices[0].message.content
        messsages.append(
            {"role": "assistant", "content": coach_message }
        )

        print(f"\n Career Coach > {coach_message} \n")


if __name__ == "__main__":
    run()