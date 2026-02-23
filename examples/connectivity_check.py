"""Example script demonstrating connectivity checking for OpenRouter and Tavily.

This script shows how to use the health checkers to verify that the external
services are accessible and properly configured.
"""

import asyncio
from stormer.config import get_config


async def main():
    """Check connectivity for both OpenRouter and Tavily services."""
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

    # Check Tavily
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

    print("\nConnectivity check complete!")


if __name__ == "__main__":
    asyncio.run(main())
