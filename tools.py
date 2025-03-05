# tools.py

import logging
from azure.communication.callautomation import (
    CallAutomationClient,
    TextSource,
    RecognizeInputType,
    PhoneNumberIdentifier
)
from config import ACS_CONNECTION_STRING, TARGET_PHONE_NUMBER
from conversation_state import clear_call_state

# Initialize a global ACS CallAutomationClient
call_automation_client = CallAutomationClient.from_connection_string(ACS_CONNECTION_STRING)

def play_text_acstool(args: dict) -> str:
    """
    Plays text-to-speech in the call.
    
    Expects:
      args: dict with keys:
         - "call_connection_id": str
         - "text": str
         
    Returns a descriptive string for logging/debugging.
    """
    call_connection_id = args.get("call_connection_id")
    text = args.get("text")
    if not call_connection_id or not text:
        return "Missing required parameters: 'call_connection_id' and 'text'."
    
    logging.info(f"[ACS-Tool] Playing TTS: {text}")
    call_conn_client = call_automation_client.get_call_connection(call_connection_id)
    play_source = TextSource(text=text, voice_name="en-US-Ava:DragonHDLatestNeural")
    call_conn_client.play_media_to_all(play_source)
    return f"Played TTS: '{text}'"

def start_speech_recognition_acstool(args: dict) -> str:
    """
    Prompts the user for speech and starts recognition.
    
    Expects:
      args: dict with keys:
         - "call_connection_id": str
         - "prompt": str
         - "initial_silence": int  (seconds to wait for speech start)
         - "end_silence": int      (seconds to wait after speech stops)
         
    Returns a descriptive string for logging/debugging.
    """
    call_connection_id = args.get("call_connection_id")
    prompt = args.get("prompt")
    initial_silence = args.get("initial_silence")
    end_silence = args.get("end_silence")
    if not call_connection_id or not prompt or initial_silence is None or end_silence is None:
        return "Missing required parameters: 'call_connection_id', 'prompt', 'initial_silence', and 'end_silence'."
    
    logging.info(f"[ACS-Tool] Starting speech recognition with prompt: {prompt}")
    call_conn_client = call_automation_client.get_call_connection(call_connection_id)
    participant = PhoneNumberIdentifier(TARGET_PHONE_NUMBER)
    play_source = TextSource(text=prompt, voice_name="en-US-Ava:DragonHDLatestNeural")
    
    call_conn_client.start_recognizing_media(
        input_type=RecognizeInputType.SPEECH,
        target_participant=participant,
        play_prompt=play_source,
        interrupt_prompt=True,
        initial_silence_timeout=initial_silence,
        end_silence_timeout=end_silence,
        operation_context="agent_prompt"
    )
    return f"Started speech recognition with prompt: '{prompt}'"

def hang_up_acstool(args: dict) -> str:
    """
    Ends the call and clears the conversation state.
    
    Expects:
      args: dict with key:
         - "call_connection_id": str
         
    Returns a descriptive string for logging/debugging.
    """
    call_connection_id = args.get("call_connection_id")
    if not call_connection_id:
        return "Missing required parameter: 'call_connection_id'."
    
    logging.info("[ACS-Tool] Hanging up")
    call_conn_client = call_automation_client.get_call_connection(call_connection_id)
    call_conn_client.hang_up()
    clear_call_state(call_connection_id)
    return "Call ended."
