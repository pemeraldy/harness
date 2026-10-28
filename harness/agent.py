import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gpt-4o-mini"


client = OpenAI()

def run():
    """Run the agent's conversation loop until user quits. """

    # The conversation history
    messages = []

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

        # 4. Call model with the full conversation
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
        )

        # 5. Extract the assistant's reply
        assistant_message = response.choices[0].message.content

        # 6. Append the assistant's reply to the history
        messages.append({"role": "assistant", "content": assistant_message})

        # 7. show user chats
        print(f"\nagent >  {assistant_message}\n")



if __name__ == "__main__":
    run()