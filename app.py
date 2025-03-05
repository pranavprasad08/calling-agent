# app.py

import logging
from flask import Flask, request, Response, redirect, render_template
from call_controller import start_outbound_call, handle_callback_events

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Simple home page
@app.route('/', methods=['GET'])
def index_handler():
<<<<<<< HEAD
=======
    # You can create a simple index.html in a 'templates' folder
>>>>>>> 0f43032 (agentic workflow)
    return render_template("index.html")

# Trigger an outbound call when visited
@app.route('/outboundCall', methods=['GET'])
def outbound_call_handler():
    call_connection_properties = start_outbound_call()
    call_id = call_connection_properties.call_connection_id
<<<<<<< HEAD
    app.logger.info(f"Outbound call initiated with call_connection_id = {call_id}")
    # Redirect back to home page or show a success page
=======
    app.logger.info(f"Outbound call initiated with call_connection_id={call_id}")
    # Optionally redirect back to home page
>>>>>>> 0f43032 (agentic workflow)
    return redirect("/")

# ACS will POST callback events here
@app.route('/api/callbacks', methods=['POST'])
def callbacks_handler():
    """
<<<<<<< HEAD
    Flask (or similar framework) route handler that receives and processes
    Azure Communication Services Call Automation callbacks.
    """
    # In many frameworks, request.json may be a dict if only one event is present;
    # convert it to a list so 'handle_callback_events' can process uniformly.
    events = request.json
    if not isinstance(events, list):
        events = [events]

=======
    Flask route that receives and processes ACS Call Automation callbacks.
    """
    events = request.json
    if not isinstance(events, list):
        events = [events]
    
    app.logger.info(f"callback")
>>>>>>> 0f43032 (agentic workflow)
    handle_callback_events(events)
    return Response(status=200)

if __name__ == '__main__':
    # Run Flask on port 8080 by default
<<<<<<< HEAD
=======
    # If you're deploying behind a reverse proxy, adjust accordingly
>>>>>>> 0f43032 (agentic workflow)
    app.run(port=8080)
