#!/usr/bin/env python3
"""Test the greeting function after fix"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
from livekit.agents import RunContext

# Create a mock context
class MockContext:
    pass

async def test_greeting():
    from src.dental.dental_tools import get_time_based_greeting
    
    context = MockContext()
    try:
        greeting = await get_time_based_greeting(context)
        print(f"Success! Greeting received:")
        print(f"{greeting}")
    except Exception as e:
        print(f"ERROR in get_time_based_greeting: {e}")
        import traceback
        traceback.print_exc()

# Run the async test
asyncio.run(test_greeting())