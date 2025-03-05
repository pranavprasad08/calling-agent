# agent_service.py

import json
import logging
from pydantic import BaseModel
from langchain.chat_models.azure_openai import AzureChatOpenAI
from langchain.agents import AgentType, initialize_agent
from langchain.tools import StructuredTool
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage

from config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_MODEL_NAME
)
from tools import play_text_acstool, start_speech_recognition_acstool, hang_up_acstool

##############################################
# 1) Define Pydantic Schemas for Tool Inputs
##############################################

class PlayTextInput(BaseModel):
    call_connection_id: str
    text: str

class StartSpeechRecognitionInput(BaseModel):
    call_connection_id: str
    prompt: str
    initial_silence: int
    end_silence: int

class HangUpInput(BaseModel):
    call_connection_id: str

##############################################
# 2) Create Structured Tools Using StructuredTool.from_function
##############################################

PLAY_TEXT_TOOL = StructuredTool.from_function(
    func=play_text_acstool,
    name="play_text",
    description=(
        "Play text-to-speech in the call. "
        "Input must be a JSON object with keys: call_connection_id (str) and text (str)."
    ),
    args_schema=PlayTextInput
)

START_SPEECH_RECOGNITION_TOOL = StructuredTool.from_function(
    func=start_speech_recognition_acstool,
    name="start_speech_recognition",
    description=(
        "Prompt the user for speech and begin recognition. "
        "Input must be a JSON object with keys: call_connection_id (str), prompt (str), "
        "initial_silence (int), and end_silence (int)."
    ),
    args_schema=StartSpeechRecognitionInput
)

HANG_UP_TOOL = StructuredTool.from_function(
    func=hang_up_acstool,
    name="hang_up",
    description=(
        "Hang up the call. "
        "Input must be a JSON object with key: call_connection_id (str)."
    ),
    args_schema=HangUpInput
)

tools = [PLAY_TEXT_TOOL, START_SPEECH_RECOGNITION_TOOL, HANG_UP_TOOL]

##############################################
# 3) Setup Conversation Memory with System Instructions
##############################################

policy_no = "12345678"
treatment = "root canal"
SYSTEM_PROMPT_TEXT = f"""\
You are a phone-based AI assistant tasked with calling an insurance helpline to verify dental insurance eligibility details.
You are the caller, start by introducing yourself and tell the callee why you called. Always use professional clear language.
The patient's policy number is {policy_no} and they need to get {treatment}.
YOU MUST ONLY output function calls using the provided tools.
DO NOT output plain text.
Available tools:
- play_text: to speak to the user. Input: call_connection_id (str) and text (str).
- start_speech_recognition: to prompt the user. Input: call_connection_id (str), prompt (str), initial_silence (int), and end_silence (int).
- hang_up: to end the call. Input: call_connection_id (str).
"""

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory.chat_memory.add_message(SystemMessage(content=SYSTEM_PROMPT_TEXT))

##############################################
# 4) Create the Azure Chat LLM Client
##############################################

llm = AzureChatOpenAI(
    openai_api_base=AZURE_OPENAI_ENDPOINT,    # e.g., "https://your-resource.openai.azure.com/"
    openai_api_key=AZURE_OPENAI_API_KEY,
    openai_api_type="azure",
    openai_api_version="2023-07-01-preview",
    deployment_name=AZURE_OPENAI_MODEL_NAME,  # e.g., "gpt-35-turbo"
    temperature=0.7,
)

##############################################
# 5) Initialize the Agent with Structured Tools and Memory
##############################################

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    memory=memory,
)

##############################################
# 6) Expose the Agent Response Function
##############################################

def agent_respond(call_state: dict, user_input: str) -> dict:
    """
    Pass recognized text or event info to the agent.
    The agent input includes the call_connection_id from call_state,
    so that tool calls will include it in their structured input.
    """
    call_connection_id = call_state.get("call_connection_id", "")
    if not call_connection_id:
        logging.warning("No call_connection_id found in call_state!")
        return call_state

    # Construct input including the call_connection_id.
    agent_input = f"CallConnectionID: {call_connection_id}\nUser: {user_input}"
    logging.info(f"[Agent] Received input: {agent_input}")
    try:
        # Use agent.invoke (preferred over deprecated agent.run)
        result = agent.invoke(agent_input)
        logging.info(f"[Agent] Result: {result}")
    except Exception as e:
        logging.error(f"[Agent] Error during agent execution: {e}", exc_info=True)

    return call_state
