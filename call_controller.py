<<<<<<< HEAD
=======
# call_controller.py

>>>>>>> 0f43032 (agentic workflow)
import logging
from azure.core.messaging import CloudEvent
from azure.communication.callautomation import (
    CallAutomationClient,
<<<<<<< HEAD
    CallConnectionClient,
    RecognizeInputType,
    TextSource,
=======
>>>>>>> 0f43032 (agentic workflow)
    PhoneNumberIdentifier
)

from config import (
    ACS_CONNECTION_STRING,
    ACS_PHONE_NUMBER,
<<<<<<< HEAD
    TARGET_PHONE_NUMBER,  # Number for the insurance helpline
=======
    TARGET_PHONE_NUMBER,
>>>>>>> 0f43032 (agentic workflow)
    CALLBACK_EVENTS_URI,
    COGNITIVE_SERVICES_ENDPOINT
)
from conversation_state import get_call_state, clear_call_state
<<<<<<< HEAD
from ai_service import query_llm

logging.basicConfig(level=logging.INFO)
=======
from agent_service import agent_respond
>>>>>>> 0f43032 (agentic workflow)

call_automation_client = CallAutomationClient.from_connection_string(ACS_CONNECTION_STRING)

def start_outbound_call():
<<<<<<< HEAD
    target_participant = PhoneNumberIdentifier(TARGET_PHONE_NUMBER)
    source_caller = PhoneNumberIdentifier(ACS_PHONE_NUMBER)

    # Create the call using the ACS client
    call_connection_properties = call_automation_client.create_call(
        target_participant,          # positional #1: the insurance helpline
        CALLBACK_EVENTS_URI,         # positional #2: callback URL
        source_caller_id_number=source_caller,
        cognitive_services_endpoint=COGNITIVE_SERVICES_ENDPOINT
    )

    return call_connection_properties

def handle_callback_events(events):
    """
    Process a list of event dictionaries from Azure Communication Services Call Automation,
    specifically for gathering additional insurance eligibility details.
    """
    for event_dict in events:
        # Convert the dictionary to a CloudEvent instance
        event = CloudEvent.from_dict(event_dict)
        event_type = event.type
        data = event.data
        
        call_connection_id = data.get('callConnectionId')
=======
    """
    Initiate an outbound call to the insurance helpline
    """
    target_participant = PhoneNumberIdentifier(TARGET_PHONE_NUMBER)
    source_caller = PhoneNumberIdentifier(ACS_PHONE_NUMBER)

    call_connection_properties = call_automation_client.create_call(
        target_participant,
        CALLBACK_EVENTS_URI,
        source_caller_id_number=source_caller,
        cognitive_services_endpoint=COGNITIVE_SERVICES_ENDPOINT
    )
    return call_connection_properties


def handle_callback_events(events):
    """
    Process incoming callback events from ACS,
    passing them to the LLM agent so it can decide the next step.
    """
    for event_dict in events:
        event = CloudEvent.from_dict(event_dict)
        event_type = event.type
        data = event.data

        call_connection_id = data.get("callConnectionId")
>>>>>>> 0f43032 (agentic workflow)
        if not call_connection_id:
            logging.warning("Received event with no callConnectionId. Skipping.")
            continue

<<<<<<< HEAD
        # Acquire a client for the active call
        call_connection_client = call_automation_client.get_call_connection(call_connection_id)
        logging.info("Processing event: %s | callConnectionId=%s", event_type, call_connection_id)

        if event_type == "Microsoft.Communication.CallConnected":
            prompt_text = (
                "Hello, I'm calling regarding a dental insurance verification. "
                "We already have the patient's policy number on file. "
                "Could you please provide the details regarding the copay amount, percentage of coverage, deductible, and any other relevant coverage information?"
            )
            _start_speech_recognition(
                call_connection_client=call_connection_client,
                target_number=TARGET_PHONE_NUMBER,
                prompt_text=prompt_text,
                operation_context="initial_prompt",
            )

        elif event_type == "Microsoft.Communication.RecognizeCompleted":
            # Retrieve speech results; fallback to empty dict to avoid KeyError
            speech_result = data.get('speechResult', {})
            recognized_text = speech_result.get('speech', '')
            logging.info("Recognized text: '%s' (callConnectionId=%s)", recognized_text, call_connection_id)

            # Fetch conversation state which contains our insurance details context
            call_state = get_call_state(call_connection_id)
            if not call_state:
                logging.warning("No call state found for %s. Creating empty state.", call_connection_id)
                call_state = {"messages": []}

            # Use recognized text to generate an AI-driven reply (could include parsing the details)
            ai_reply = query_llm(recognized_text, call_state["messages"])
            logging.info("AI Reply: '%s'", ai_reply)

            # Play the AI-generated reply back to the insurance helpline representative
            _play_text(call_connection_client, ai_reply)

            # Optionally, prompt for any further clarifications
            followup_text = "Is there any additional coverage detail or clarification you can provide regarding the patient's dental insurance?"
            _start_speech_recognition(
                call_connection_client=call_connection_client,
                target_number=TARGET_PHONE_NUMBER,
                prompt_text=followup_text,
                operation_context="followup_prompt",
            )

        elif event_type == "Microsoft.Communication.RecognizeFailed":
            logging.info("RecognizeFailed event for callConnectionId=%s", call_connection_id)
            _play_text(call_connection_client, "Sorry, I didn’t catch that.")
            retry_text = (
                "Could you please repeat the insurance details regarding the copay, coverage percentage, and deductible?"
            )
            _start_speech_recognition(
                call_connection_client=call_connection_client,
                target_number=TARGET_PHONE_NUMBER,
                prompt_text=retry_text,
                operation_context="retry_prompt",
            )

        elif event_type in ["Microsoft.Communication.PlayCompleted", "Microsoft.Communication.PlayFailed"]:
            logging.info("%s event for callConnectionId=%s", event_type, call_connection_id)

        elif event_type == "Microsoft.Communication.CallDisconnected":
            logging.info("CallDisconnected event for callConnectionId=%s", call_connection_id)
            clear_call_state(call_connection_id)

        else:
            logging.debug("Unhandled event type: %s (callConnectionId=%s)", event_type, call_connection_id)

def _start_speech_recognition(call_connection_client, target_number, prompt_text, operation_context):
    participant = PhoneNumberIdentifier(target_number)
    play_source = TextSource(text=prompt_text, voice_name="en-US-NancyNeural")
    call_connection_client.start_recognizing_media(
        input_type=RecognizeInputType.SPEECH,
        target_participant=participant,
        play_prompt=play_source,
        interrupt_prompt=True,
        initial_silence_timeout=5,
        operation_context=operation_context
    )

def _play_text(call_connection_client, text):
    play_source = TextSource(text=text, voice_name="en-US-NancyNeural")
    call_connection_client.play_media_to_all(play_source)
=======
        # Retrieve or create call state
        call_state = get_call_state(call_connection_id)
        call_state["call_connection_id"] = call_connection_id

        logging.info(f"Processing event: {event_type} | callConnectionId={call_connection_id}")

        if event_type == "Microsoft.Communication.CallConnected":
            # Let the agent know the call connected
            agent_respond(call_state, "Event: Call connected.")

        elif event_type == "Microsoft.Communication.RecognizeCompleted":
            speech_result = data.get('speechResult', {})
            recognized_text = speech_result.get('speech', "")
            logging.info(f"Recognized text: '{recognized_text}'")
            agent_respond(call_state, recognized_text)

        elif event_type == "Microsoft.Communication.RecognizeFailed":
            logging.info("RecognizeFailed event")
            agent_respond(call_state, "Event: Recognize failed.")

        elif event_type in ["Microsoft.Communication.PlayCompleted", "Microsoft.Communication.PlayFailed"]:
            # Let the agent know playback ended or failed
            agent_respond(call_state, f"Event: {event_type}")

        elif event_type == "Microsoft.Communication.CallDisconnected":
            logging.info(f"Call disconnected for callConnectionId={call_connection_id}")
            clear_call_state(call_connection_id)

        else:
            logging.debug(f"Unhandled event type: {event_type}")
>>>>>>> 0f43032 (agentic workflow)
