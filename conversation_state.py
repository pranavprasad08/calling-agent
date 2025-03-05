# conversation_state.py

call_states = {}  # For demonstration only (not thread-safe)

def get_call_state(call_connection_id: str) -> dict:
    """
    Retrieve or create conversation state for a given call connection ID.
    """
    if call_connection_id not in call_states:
        call_states[call_connection_id] = {
            "messages": []
        }
    return call_states[call_connection_id]

def clear_call_state(call_connection_id: str):
    """
    Remove conversation state when the call ends.
    """
    if call_connection_id in call_states:
        del call_states[call_connection_id]
