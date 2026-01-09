#!/usr/bin/env python

import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Ollama configuration from environment variables
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.getenv("MODEL", "granite4:latest")
PREPEND_STATEMENT = os.getenv("PREPEND_STATEMENT", "")
API_KEY = os.getenv("API_KEY", "change-me-in-production")


@app.route("/chat", methods=["POST"])
def chat():
    """
    Handle POST request with payload:
    {"user": "[username]", "message": "[a question]", "prepend": "[optional prepend statement]"}

    Returns:
    {"user": "[original user]", "response": "[ollama response]"}
    """
    try:
        # Check API key
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        provided_key = auth_header.split("Bearer ", 1)[1]
        if provided_key != API_KEY:
            return jsonify({"error": "Invalid API key"}), 403

        # Parse incoming JSON
        data = request.get_json()

        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400

        user = data.get("user")
        message = data.get("message")
        prepend = data.get("prepend")

        if not user or not message:
            return jsonify(
                {"error": "Both 'user' and 'message' fields are required"}
            ), 400

        # Build the full prompt with optional prepended statement
        # Use request's prepend if provided, otherwise fall back to PREPEND_STATEMENT
        prepend_text = prepend if prepend is not None else PREPEND_STATEMENT
        full_prompt = f"{prepend_text}\n{message}" if prepend_text else message

        # Send message to Ollama using native API format
        ollama_payload = {
            "model": DEFAULT_MODEL,
            "prompt": full_prompt,
            "stream": False,
        }

        response = requests.post(OLLAMA_URL, json=ollama_payload, timeout=60)
        response.raise_for_status()

        # Extract the response from Ollama
        ollama_data = response.json()
        ollama_response = ollama_data.get("response", "")

        # Split response by newlines and filter out empty lines
        response_lines = [line for line in ollama_response.split("\n") if line.strip()]

        # Return formatted response with lines as ordered list
        return jsonify({"user": user, "response": response_lines})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Ollama API error: {str(e)}"}), 503

    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ollama Chat Service")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")

    args = parser.parse_args()

    print(f"Starting Ollama Chat Service on {args.host}:{args.port}")
    print(f"Using Ollama at {OLLAMA_URL} with model {DEFAULT_MODEL}")
    if PREPEND_STATEMENT:
        print(f"Prepending to all prompts: {PREPEND_STATEMENT[:50]}...")
    print(f"API key authentication: {'enabled' if API_KEY else 'disabled'}")

    app.run(host=args.host, port=args.port, debug=True)
