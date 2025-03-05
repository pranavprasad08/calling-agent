# app.py

import logging
from flask import Flask, request, Response, redirect, render_template
from call_controller import start_outbound_call, handle_callback_events

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Simple home page
@app.route('/', methods=['GET'])
def index_handler():
    # You can create a simple index.html in a 'templates' folder
    return render_template("index.html")

# Trigger an outbound call when visited
@app.route('/outboundCall', methods=['GET'])
def outbound_call_handler():
    call_connection_properties = start_outbound_call()
    call_id = call_connection_properties.call_connection_id
    app.logger.info(f"Outbound call initiated with call_connection_id={call_id}")
    # Optionally redirect back to home page
    return redirect("/")

# ACS will POST callback events here
@app.route('/api/callbacks', methods=['POST'])
def callbacks_handler():
    """
    Flask route that receives and processes ACS Call Automation callbacks.
    """
    events = request.json
    if not isinstance(events, list):
        events = [events]
    
    app.logger.info(f"callback")
    handle_callback_events(events)
    return Response(status=200)

if __name__ == '__main__':
    # Run Flask on port 8080 by default
    # If you're deploying behind a reverse proxy, adjust accordingly
    app.run(port=8080)
