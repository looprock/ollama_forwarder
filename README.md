# Ollama Chat Service

A simple Flask service that receives POST requests with speaker/message payloads, sends them to Ollama, and returns the AI response.

## Installation

Install dependencies:
```bash
cd python
uv sync
# or: pip install flask requests
```

## Usage

### Start the Service

```bash
./ollama_service.py --api-key "my-secret-key"
```

Options:
- `--host`: Host to bind to (default: 0.0.0.0)
- `--port`: Port to bind to (default: 5000)
- `--ollama-url`: Ollama API URL (default: http://localhost:11434/api/generate)
- `--model`: Ollama model to use (default: granite4:latest)
- `--prepend`: Statement to prepend to all prompts (default: empty)
- `--api-key`: API key for authentication (default: "your-secret-api-key-here")

Example with custom settings:
```bash
./ollama_service.py --port 8080 --model mistral --prepend "Answer concisely." --api-key "secret123"
```

### API Endpoints

#### POST /chat

Send a message to Ollama and get a response.

**Request:**
```json
{
  "user": "username",
  "message": "What is the capital of France?"
}
```

**Response:**
```json
{
  "user": "username",
  "response": [
    "The capital of France is Paris.",
    "It is located in the north-central part of the country."
  ]
}
```

Note: The response is an array of strings split by newlines, with empty lines filtered out.

**Example with curl:**
```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secret-api-key-here" \
  -d '{"user": "Alice", "message": "What is the meaning of life?"}'
```

**Example with Python:**
```python
import requests

response = requests.post(
    'http://localhost:5000/chat',
    headers={'Authorization': 'Bearer your-secret-api-key-here'},
    json={
        'user': 'Bob',
        'message': 'Explain quantum computing'
    }
)

data = response.json()
print(f"User: {data['user']}")
print(f"Response lines: {len(data['response'])}")
for line in data['response']:
    print(f"  - {line}")
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

## Error Handling

The service returns appropriate HTTP status codes:
- 400: Bad request (missing required fields)
- 401: Missing or invalid Authorization header
- 403: Invalid API key
- 503: Ollama API unavailable
- 500: Internal server error

Error response format:
```json
{
  "error": "Error description"
}
```

## Security

The service requires API key authentication via the `Authorization` header:
```
Authorization: Bearer your-secret-api-key-here
```

Set your API key using:
- The `--api-key` command-line argument
- Or edit the `API_KEY` constant in the source code

## Prepend Statement

You can configure a statement to be prepended to all prompts. This is useful for:
- Setting a consistent tone or style
- Adding system instructions
- Providing context for all queries

Example:
```bash
./ollama_service.py --prepend "You are a helpful assistant. Answer concisely."
```

## Requirements

- Python 3.13+
- Flask
- requests
- Ollama running locally (default: http://localhost:11434)
