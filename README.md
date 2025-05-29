# Khesht API

A simple MVP FastAPI application with CRUD operations for managing items and OpenAI integration with structured data.

## Features

- ✅ FastAPI framework
- ✅ Pydantic for data validation
- ✅ Ruff for code formatting and linting
- ✅ In-memory storage (perfect for MVP)
- ✅ RESTful API endpoints
- ✅ Interactive API documentation
- ✅ Health check endpoint
- ✅ **OpenAI integration with structured data**
- ✅ **Message dataclass and Role StrEnum**
- ✅ **Structured OpenAI responses**

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip
- OpenAI API key (optional, for AI features)

### Installation

1. Clone this repository or navigate to the project directory
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp env.example .env
# Edit .env and add your OpenAI API key
```

### Running the Application

Start the development server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check (includes OpenAI service status)

### OpenAI Integration Endpoints

- `POST /chat` - Send single message to OpenAI with structured response
- `POST /chat/conversation` - Send multi-message conversation to OpenAI

### Items Management

- `GET /items` - Get all items
- `GET /items/{item_id}` - Get item by ID
- `POST /items` - Create new item
- `PUT /items/{item_id}` - Update item
- `DELETE /items/{item_id}` - Delete item

## OpenAI Integration Examples

### Simple Chat Request

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Hello, how are you?",
       "system_prompt": "You are a helpful assistant.",
       "model": "gpt-3.5-turbo",
       "max_tokens": 1000,
       "temperature": 0.7
     }'
```

### Conversation Request

```bash
curl -X POST "http://localhost:8000/chat/conversation" \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {"role": "system", "content": "You are a helpful assistant."},
         {"role": "user", "content": "Hello!"},
         {"role": "assistant", "content": "Hi there! How can I help you?"},
         {"role": "user", "content": "What is FastAPI?"}
       ],
       "model": "gpt-3.5-turbo",
       "max_tokens": 1000,
       "temperature": 0.7
     }'
```

### Structured Response Example

```json
{
  "message": "FastAPI is a modern, fast web framework for building APIs with Python...",
  "model": "gpt-3.5-turbo-0613",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  },
  "finish_reason": "stop"
}
```

## Data Structures

### Message Dataclass

```python
@dataclass
class Message:
    role: MessageRole
    content: str
```

### MessageRole StrEnum

```python
class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
```

### ChatResponse Model

```python
class ChatResponse(BaseModel):
    message: str
    model: str
    usage: dict
    finish_reason: str
```

### Example Usage

#### Create an item:
```bash
curl -X POST "http://localhost:8000/items" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Sample Item",
       "description": "This is a sample item",
       "price": 29.99,
       "is_available": true
     }'
```

#### Get all items:
```bash
curl -X GET "http://localhost:8000/items"
```

## Development

### Code Formatting with Ruff

Format your code:
```bash
ruff format .
```

Lint your code:
```bash
ruff check .
```

Fix auto-fixable lint issues:
```bash
ruff check . --fix
```

### Project Structure

```
khesht-api/
├── main.py              # FastAPI application
├── helper/
│   └── openai_service.py # OpenAI service with structured data
├── requirements.txt     # Python dependencies
├── pyproject.toml      # Ruff configuration
├── env.example         # Environment variables example
└── README.md           # This file
```

## Data Models

### Item
- `id`: Integer (auto-generated)
- `name`: String (required)
- `description`: String (optional)
- `price`: Float (required)
- `is_available`: Boolean (default: true)

### Message (OpenAI)
- `role`: MessageRole enum (system, user, assistant)
- `content`: String (message content)

## Environment Variables

Copy `env.example` to `.env` and configure:

```bash
OPENAI_API_KEY=your_openai_api_key_here
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Next Steps for Production

This is an MVP with in-memory storage. For production, consider:

- [ ] Database integration (PostgreSQL, SQLite, etc.)
- [ ] Authentication and authorization
- [ ] Input validation and sanitization
- [ ] Error handling and logging
- [ ] Testing suite
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API rate limiting
- [ ] Monitoring and metrics
- [ ] OpenAI usage tracking and billing controls
- [ ] Conversation history storage
- [ ] User session management

## License

This project is open source and available under the MIT License. 