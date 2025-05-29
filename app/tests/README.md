# Tests for Khesht API

This directory contains the test suite for the Khesht API, specifically focusing on the `/user-prompt` endpoint.

## Setup

### Prerequisites

Make sure you have all the required dependencies installed:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (including test dependencies)
pip install -r requirements.txt
```

The test dependencies include:
- `pytest` (v7.4.3) - Testing framework
- `httpx` (v0.25.2) - HTTP client for FastAPI testing

## Running Tests

### Run all tests for the user-prompt endpoint:
```bash
python -m pytest app/tests/test_user_prompt.py -v
```

### Run all tests in the tests directory:
```bash
python -m pytest app/tests/ -v
```

### Run a specific test:
```bash
python -m pytest app/tests/test_user_prompt.py::TestUserPromptEndpoint::test_user_prompt_success -v
```

### Run tests with coverage (if you install pytest-cov):
```bash
pip install pytest-cov
python -m pytest app/tests/ --cov=app --cov-report=html
```

## Test Structure

### Test File: `test_user_prompt.py`

This file contains comprehensive tests for the `/user-prompt` endpoint, including:

#### Success Cases:
- **`test_user_prompt_success`** - Tests valid requests and proper response format
- **`test_user_prompt_empty_prompt`** - Tests handling of empty prompt strings
- **`test_user_prompt_empty_session_id`** - Tests handling of empty session IDs
- **`test_user_prompt_long_prompt`** - Tests handling of very long prompts (10k characters)
- **`test_user_prompt_special_characters`** - Tests Unicode characters and emojis
- **`test_user_prompt_response_schema_validation`** - Validates response adheres to schema

#### Error Cases:
- **`test_user_prompt_missing_prompt`** - Tests missing required prompt field (422 error)
- **`test_user_prompt_missing_session_id`** - Tests missing required session_id field (422 error)
- **`test_user_prompt_invalid_json`** - Tests malformed JSON requests (422 error)
- **`test_user_prompt_wrong_method`** - Tests using wrong HTTP method (405 error)

### Fixtures

The tests use several pytest fixtures for reusable test data:
- **`client`** - FastAPI TestClient instance
- **`valid_user_prompt_request`** - Valid request payload
- **`invalid_user_prompt_request_missing_prompt`** - Request missing prompt field
- **`invalid_user_prompt_request_missing_session_id`** - Request missing session_id field

## Response Schema Validation

The tests validate that the `/user-prompt` endpoint returns responses conforming to the `UserPromptResponse` schema:

```python
class UserPromptResponse(BaseModel):
    name: str
    description: str
    image_urls: list[str]
    urls: list[str]
```

## Configuration

The tests are configured via `pytest.ini` in the project root:
- Test discovery in `app/tests` directory
- Verbose output enabled
- Short traceback format
- Deprecation warnings filtered

## Adding New Tests

When adding new tests:

1. Follow the naming convention: `test_<functionality>`
2. Use descriptive docstrings
3. Group related tests in the `TestUserPromptEndpoint` class
4. Use fixtures for reusable test data
5. Test both success and error scenarios
6. Validate response structure and data types

## Best Practices

- **Test Independence**: Each test should be independent and not rely on others
- **Clear Assertions**: Use descriptive assertion messages when helpful
- **Edge Cases**: Test boundary conditions (empty strings, very long inputs, special characters)
- **Error Handling**: Test various error scenarios and status codes
- **Schema Validation**: Ensure responses match expected Pydantic models

## Continuous Integration

These tests are designed to run in CI/CD pipelines. The exit code will be:
- `0` for all tests passing
- `1` for any test failures

For CI environments, you may want to add:
```bash
python -m pytest app/tests/ --junitxml=test-results.xml
``` 