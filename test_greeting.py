#!/usr/bin/env python3
"""Test the greeting function to see what error is occurring"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test the basic datetime function first
from src.dental.dental_tools import get_current_datetime_info

try:
    print("Testing get_current_datetime_info()...")
    info = get_current_datetime_info()
    print(f"Success! Current time info:")
    print(f"  Time: {info['time_formatted']}")
    print(f"  Date: {info['date_formatted']}")
    print(f"  Hour: {info['hour']}")
    print(f"  Weekday: {info['weekday']}")
except Exception as e:
    print(f"ERROR in get_current_datetime_info: {e}")
    import traceback
    traceback.print_exc()

# Now test the greeting function
print("\n" + "="*50)
print("Testing get_time_based_greeting()...")

from livekit.agents import RunContext

# Create a mock context
class MockContext:
    pass

async def test_greeting():
    from src.dental.dental_tools import get_time_based_greeting
    
    context = MockContext()
    try:
        greeting = await get_time_based_greeting(context)
        print(f"Success! Greeting: {greeting}")
    except Exception as e:
        print(f"ERROR in get_time_based_greeting: {e}")
        import traceback
        traceback.print_exc()

# Run the async test
import asyncio
asyncio.run(test_greeting())