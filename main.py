import logging
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from assistant import Assistant
from database import init_vector_store, load_pdf_to_vector_store
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE

logging.basicConfig(level=logging.ERROR)

def main():
    load_dotenv()

    print("Initializing system...")
    try:
        vector_store = init_vector_store()
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        return

    llm = ChatGroq(model="llama-3.3-70b-versatile")
    history = [{"role": "ai", "content": WELCOME_MESSAGE}]

    assistant = Assistant(
        system_prompt=SYSTEM_PROMPT,
        llm=llm,
        message_history=history,
        vector_store=vector_store,
    )

    print(f"\nAI: {WELCOME_MESSAGE}\n")

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ('exit', 'quit'):
                break

            history.append({"role": "user", "content": user_input})

            print("AI: ", end="", flush=True)
            full_response = ""
            for chunk in assistant.get_response(user_input):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n")

            history.append({"role": "ai", "content": full_response})
    except (KeyboardInterrupt, EOFError):
        pass
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
