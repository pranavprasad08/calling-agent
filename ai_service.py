# ai_service.py

from openai import AzureOpenAI

from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_MODEL_NAME
)

client = AzureOpenAI(api_key=AZURE_OPENAI_API_KEY,
azure_endpoint=AZURE_OPENAI_ENDPOINT,
api_version="2023-07-01-preview")

def query_llm(user_input: str, conversation_messages: list) -> str:
    """
    Submits user input to Azure OpenAI ChatCompletion.
    
    :param user_input: The transcription or recognized text from the caller.
    :param conversation_messages: A running list of dicts representing the chat history 
                                 (including system, user, and assistant messages).
    :return: The assistant's text response.
    """
    # Append the user’s latest input
    conversation_messages.append({"role": "user", "content": user_input})

    # Call the Azure OpenAI ChatCompletion endpoint
    response = client.chat.completions.create(
        model=AZURE_OPENAI_MODEL_NAME,
        messages=conversation_messages,
        temperature=0.7
    )

    # Extract the AI’s reply
    ai_reply = response.choices[0].message.content
    # Add the AI's response to our conversation history
    conversation_messages.append({"role": "assistant", "content": ai_reply})

    return ai_reply
