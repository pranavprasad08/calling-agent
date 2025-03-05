# call_controller.py

import logging
from azure.core.messaging import CloudEvent
from azure.communication.callautomation import (
    CallAutomationClient,
    PhoneNumberIdentifier
)

from config import (
    ACS_CONNECTION_STRING,
    ACS_PHONE_NUMBER,
    TARGET_PHONE_NUMBER,
    CALLBACK_EVENTS_URI,
    COGNITIVE_SERVICES_ENDPOINT
)
from conversation_state import get_call_state, clear_call_state
from agent_service import agent_respond

call_automation_client = CallAutomationClient.from_connection_string(ACS_CONNECTION_STRING)

def start_outbound_call():
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
        if not call_connection_id:
            logging.warning("Received event with no callConnectionId. Skipping.")
            continue

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
