import os
import logging
from flask import Flask, render_template, request, jsonify, stream_with_context, Response
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from assistant import Assistant
from database import init_vector_store
from database import init_vector_store
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
app.secret_key = 'another_super_secret_key_for_chat'

# Initialize globals
assistant = None

def init_assistant():
    """Initializes the Assistant instance."""
    global assistant
    try:
        print("Initializing Chat Assistant...")
        vector_store = init_vector_store()
        llm = ChatGroq(model="llama-3.3-70b-versatile")
        history = [{"role": "ai", "content": WELCOME_MESSAGE}]
        
        assistant = Assistant(
            system_prompt=SYSTEM_PROMPT,
            llm=llm,
            message_history=history,
            vector_store=vector_store,
        )
        print("Assistant initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {e}")
        print(f"Error initializing assistant: {e}")

@app.route('/')
def chat_ui():
    return render_template('chat.html')

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    global assistant
    if not assistant:
        return jsonify({"error": "Assistant not initialized"}), 500

    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Append user message to history
    assistant.message_history.append({"role": "user", "content": user_message})

    def generate():
        full_response = ""
        try:
            # Stream response
            for chunk in assistant.get_response(user_message):
                yield chunk
                full_response += chunk
            
            # Append AI response to history after streaming is done
            assistant.message_history.append({"role": "ai", "content": full_response})
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            yield f"\n[Error: {str(e)}]"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == '__main__':
    init_assistant()
    print("Starting Chat App on port 5001...")
    # Admin app runs on port 5000
    app.run(debug=True, port=5001)
