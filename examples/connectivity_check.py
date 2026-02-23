"""Example script demonstrating connectivity checking for STORMer services.

This script shows how to use the health checkers to verify that the external
services are accessible and properly configured.
"""

import asyncio
from stormer.config import get_config
from stormer.connectivity import DuckDuckGoHealthChecker


async def main():
    """Check connectivity for OpenRouter, Tavily, and DuckDuckGo services."""
    config = get_config()

    print("Checking service connectivity...\n")

    # Check OpenRouter
    print("Checking OpenRouter...")
    openrouter_checker = config.create_openrouter_checker()
    try:
        result = await openrouter_checker.check_health()
        print(f"  Status: {result.status.value}")
        print(f"  Message: {result.message}")
        if result.response_time_ms:
            print(f"  Response time: {result.response_time_ms:.2f}ms")
        if result.details:
            print(f"  Details: {result.details}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # Check Tavily (if API key is configured)
    if config.tavily_api_key:
        print("Checking Tavily...")
        tavily_checker = config.create_tavily_checker()
        try:
            result = await tavily_checker.check_health()
            print(f"  Status: {result.status.value}")
            print(f"  Message: {result.message}")
            if result.response_time_ms:
                print(f"  Response time: {result.response_time_ms:.2f}ms")
            if result.details:
                print(f"  Details: {result.details}")
        except Exception as e:
            print(f"  Error: {e}")
    else:
        print("Skipping Tavily (no API key configured)")

    print()

    # Check DuckDuckGo (no API key required)
    print("Checking DuckDuckGo...")
    ddg_checker = DuckDuckGoHealthChecker(timeout=10.0)
    try:
        result = await ddg_checker.check_health()
        print(f"  Status: {result.status.value}")
        print(f"  Message: {result.message}")
        if result.response_time_ms:
            print(f"  Response time: {result.response_time_ms:.2f}ms")
        if result.details:
            print(f"  Details: {result.details}")
    except Exception as e:
        print(f"  Error: {e}")

    print("\nConnectivity check complete!")


if __name__ == "__main__":
    asyncio.run(main())
