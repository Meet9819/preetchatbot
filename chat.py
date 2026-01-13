import ollama

# This list will store the entire conversation
messages = []

print("--- AI Chatbot with Memory (Type 'exit' to stop) ---")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == 'exit':
        break

    # 1. Add your message to the history
    messages.append({'role': 'user', 'content': user_input})

    # 2. Send the WHOLE history to the AI
    response = ollama.chat(model='llama3.2:1b', messages=messages)

    # 3. Get the AI's answer
    ai_response = response['message']['content']
    print(f"AI: {ai_response}")

    # 4. Add the AI's answer to the history so it remembers what it said
    messages.append({'role': 'assistant', 'content': ai_response})