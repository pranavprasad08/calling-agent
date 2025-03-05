# conversation_state.py

<<<<<<< HEAD
# For demonstration only; not thread-safe for high concurrency.
# For production, store in an external DB/cache.

call_states = {}
=======
call_states = {}  # For demonstration only (not thread-safe)
>>>>>>> 0f43032 (agentic workflow)

def get_call_state(call_connection_id: str) -> dict:
    """
    Retrieve or create conversation state for a given call connection ID.
    """
    if call_connection_id not in call_states:
<<<<<<< HEAD
        # Start with a "system" message giving the AI context for phone-based interactions.
        call_states[call_connection_id] = {
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a phone-based AI assistant tasked with calling an insurance helpline to verify dental insurance eligibility details. "
                        "The patient's policy number is already stored in our records. "
                        "Please ask for additional information including the copay amount, percentage of coverage, deductible, and any other pertinent details regarding their dental insurance coverage. "
                        "Speak clearly, professionally, and ensure you confirm all the details."
                    )
                }
            ]
=======
        call_states[call_connection_id] = {
            "messages": []
>>>>>>> 0f43032 (agentic workflow)
        }
    return call_states[call_connection_id]

def clear_call_state(call_connection_id: str):
    """
<<<<<<< HEAD
    Remove conversation state when call ends.
=======
    Remove conversation state when the call ends.
>>>>>>> 0f43032 (agentic workflow)
    """
    if call_connection_id in call_states:
        del call_states[call_connection_id]
