# STORMer

STORM (Structured Thoughts Outlining Research Methodology) implementation using PydanticAI.

## Installation

```bash
uv sync
```

## Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Required environment variables:
- `OPENROUTER_API_KEY`: Get from https://openrouter.ai/keys

Optional configuration:
- `OPENROUTER_MODEL`: Model to use (default: `anthropic/claude-3-5-sonnet`)
- `OPENROUTER_BASE_URL`: OpenRouter API base URL (default: `https://openrouter.ai/api/v1`)
- `TAVILY_API_KEY`: Get from https://tavily.com/ (optional, for enhanced search)
- `TAVILY_BASE_URL`: Tavily API base URL (default: `https://api.tavily.com`)

**Note:** DuckDuckGo search is available as a no-authentication-required alternative to Tavily.

## Connectivity Check

STORMer includes a connectivity check feature to verify that your API keys are valid and the services are accessible before running research tasks.

### Supported Services

- **OpenRouter**: LLM API (requires API key)
- **Tavily**: Search API (optional, requires API key)
- **DuckDuckGo**: Search API (no authentication required)

### Quick Check

```bash
# Run the connectivity check example
uv run python examples/connectivity_check.py

# Or use the quick test script
uv run python test_connectivity_quick.py
```

### Programmatic Usage

#### Check OpenRouter and Tavily

```python
import asyncio
from stormer.config import get_config

async def check_services():
    config = get_config()

    # Check OpenRouter
    openrouter_checker = config.create_openrouter_checker()
    result = await openrouter_checker.check_health()
    print(f"OpenRouter: {result.status.value}")
    print(f"Message: {result.message}")
    if result.details:
        print(f"Models available: {result.details['model_count']}")

    # Check Tavily (if API key is configured)
    if config.tavily_api_key:
        tavily_checker = config.create_tavily_checker()
        result = await tavily_checker.check_health()
        print(f"Tavily: {result.status.value}")
        print(f"Message: {result.message}")

asyncio.run(check_services())
```

#### Check DuckDuckGo (No API Key Required)

```python
import asyncio
from stormer.connectivity import DuckDuckGoHealthChecker

async def check_duckduckgo():
    # No API key needed!
    checker = DuckDuckGoHealthChecker(timeout=10.0)

    result = await checker.check_health()
    print(f"DuckDuckGo: {result.status.value}")
    print(f"Message: {result.message}")
    if result.response_time_ms:
        print(f"Response time: {result.response_time_ms:.2f}ms")
    if result.details:
        print(f"Results found: {result.details.get('result_count', 0)}")

asyncio.run(check_duckduckgo())
```

#### Check All Services

```python
import asyncio
from stormer.connectivity import (
    OpenRouterHealthChecker,
    TavilyHealthChecker,
    DuckDuckGoHealthChecker,
)
from stormer.config import get_config

async def check_all_services():
    config = get_config()

    # OpenRouter (requires API key)
    openrouter = config.create_openrouter_checker()
    result = await openrouter.check_health()
    print(f"OpenRouter: {result.status.value}")

    # Tavily (optional, requires API key)
    if config.tavily_api_key:
        tavily = config.create_tavily_checker()
        result = await tavily.check_health()
        print(f"Tavily: {result.status.value}")

    # DuckDuckGo (no API key required)
    ddg = DuckDuckGoHealthChecker()
    result = await ddg.check_health()
    print(f"DuckDuckGo: {result.status.value}")

asyncio.run(check_all_services())
```

### Service Status

The connectivity check returns one of the following statuses:
- `HEALTHY`: Service is fully operational
- `DEGRADED`: Service is operational but with limitations (e.g., rate limited)
- `UNHEALTHY`: Service is not operational (e.g., 4xx errors)
- `AUTHENTICATION_FAILED`: Invalid API credentials (401)
- `TIMEOUT`: Service did not respond within the timeout period
- `UNKNOWN`: Unable to determine service status

### Error Handling

```python
from stormer.connectivity.exceptions import (
    AuthenticationError,
    TimeoutError,
    NetworkError,
    ServiceUnavailableError,
)

try:
    result = await checker.check_health()
except AuthenticationError:
    print("Invalid API key")
except TimeoutError:
    print("Request timed out")
except NetworkError:
    print("Network connectivity issue")
except ServiceUnavailableError:
    print("Service is down")
```

## Running Tests

```bash
uv run pytest
```

## Development

```bash
# Run linting
uv run ruff check .

# Format code
uv run ruff format .
```

## Project Structure

```
stormer/
├── src/stormer/
│   ├── config.py              # Configuration management
│   └── connectivity/          # Connectivity checking module
│       ├── base.py            # Base abstractions
│       ├── exceptions.py      # Custom exceptions
│       ├── openrouter.py      # OpenRouter health checker
│       ├── tavily.py          # Tavily health checker
│       └── duckduckgo.py      # DuckDuckGo health checker (no auth)
├── tests/
│   ├── test_config.py         # Config tests
│   └── test_connectivity/     # Connectivity tests
│       ├── test_base.py
│       ├── test_exceptions.py
│       ├── test_openrouter.py
│       ├── test_tavily.py
│       └── test_duckduckgo.py
├── examples/
│   └── connectivity_check.py  # Connectivity check example
└── test_connectivity_quick.py # Quick test script
```
