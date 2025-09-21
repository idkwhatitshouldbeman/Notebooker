# NTBK_AI

An independent AI agentic automation microservice powered by Google's FLAN-T5 Small model. This service provides autonomous multi-step workflows, task decomposition, and external tool integration through a REST API interface.

## Features

- **Autonomous Agentic Workflows**: Multi-step writing, reasoning, and querying capabilities
- **Stateful Task Management**: Maintains context across multi-turn interactions
- **External Tool Integration**: Supports dynamic tool endpoint configuration
- **REST API Interface**: Clean API for task submission and progress tracking
- **Comprehensive Logging**: Machine-readable logs for debugging and monitoring
- **Security & Validation**: Input sanitization and security measures
- **Resource Management**: Timeout and concurrency controls

## API Endpoints

### POST /agentic-task

Submit a new agentic task for processing.

**Request Body:**
```json
{
  "task_id": "unique-id",
  "prompt_context": "full prompt or prior conversation",
  "agent_config": {
    "temperature": 0.7,
    "max_tokens": 1000,
    "stop_sequences": ["\n\n"]
  },
  "external_tool_endpoints": {
    "web_search": "https://api.example.com/search",
    "calculator": "https://api.example.com/calc"
  }
}
```

**Response Body:**
```json
{
  "task_id": "unique-id",
  "status": "in_progress|completed|failed",
  "agent_reply": "text or structured data",
  "next_step": {
    "action": "continue|complete|wait_for_tool",
    "instructions": "next action description"
  },
  "logs": "detailed execution logs",
  "error": null
}
```

## Deployment

This service is designed to be deployed on Render with automatic scaling and health monitoring.

## Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run locally: `uvicorn main:app --host 0.0.0.0 --port 8000`
3. Test API: `curl -X POST http://localhost:8000/agentic-task -H "Content-Type: application/json" -d @example_request.json`

## Architecture

The service implements a modular architecture with:
- FastAPI for REST API handling
- Google FLAN-T5 Small (80M parameters, 300MB) for language model processing
- Redis for task state management
- Comprehensive logging and monitoring
- Security middleware and input validation

## Why FLAN-T5 Small?

FLAN-T5 Small is an excellent choice for this microservice because:

- **Efficient**: Only 80M parameters (300MB download) - much smaller than larger models
- **Excellent Reasoning**: Fine-tuned on over 1000 tasks, achieving 75.2% on five-shot MMLU benchmark
- **Multilingual**: Supports English, Spanish, Japanese, and many other languages
- **Apache 2.0 License**: Free to use and modify
- **Fast Inference**: Optimized for quick response times
- **Strong Performance**: Achieves state-of-the-art results even with fewer parameters

Based on [Dataloop's FLAN-T5 documentation](https://dataloop.ai/library/model/google_flan-t5-small/) and [local setup guides](https://heidloff.net/article/running-llm-flan-t5-locally/), this model excels at reasoning, translation, and text generation tasks.
