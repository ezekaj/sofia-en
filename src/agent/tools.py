"""
Sofia Base Agent Tools - Generic Voice Assistant Functions

This file contains basic tools that any Sofia agent can use, regardless
of specialization. These are the core building blocks for all Sofia variants.
"""

from datetime import datetime
from typing import Dict, Any
from livekit.agents import function_tool
from livekit.agents.llm import RunContext


@function_tool
async def get_basic_info(ctx: RunContext) -> Dict[str, str]:
    """
    Get basic information about Sofia's capabilities.

    Returns basic information about what Sofia can help with.
    """
    return {
        "status": "success",
        "info": {
            "name": "Sofia",
            "role": "AI Voice Assistant",
            "capabilities": [
                "General conversation and assistance",
                "Time and date information",
                "Basic help and guidance",
                "Professional communication"
            ],
            "availability": "24/7 voice assistance",
            "language": "English"
        }
    }


@function_tool
async def get_current_datetime_info(ctx: RunContext) -> Dict[str, Any]:
    """
    Get comprehensive current date and time information.

    Provides complete temporal awareness including current time, date,
    day of week, and contextual information for conversations.
    """
    try:
        now = datetime.now()

        # Format date and time
        current_date = now.strftime("%A, %B %d, %Y")  # Monday, January 15, 2024
        current_time = now.strftime("%I:%M %p")       # 2:30 PM
        current_day = now.strftime("%A")              # Monday
        current_month = now.strftime("%B")            # January

        # Time period for greetings
        hour = now.hour
        if 5 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 17:
            time_period = "afternoon"
        elif 17 <= hour < 21:
            time_period = "evening"
        else:
            time_period = "late night"

        return {
            "status": "success",
            "datetime_info": {
                "current_date": current_date,
                "current_time": current_time,
                "current_day": current_day,
                "current_month": current_month,
                "time_period": time_period,
                "hour_24": now.hour,
                "minute": now.minute,
                "is_weekend": now.weekday() >= 5,  # Saturday=5, Sunday=6
                "iso_timestamp": now.isoformat(),
                "context": f"It is currently {current_time} on {current_date}"
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Unable to get current date/time: {str(e)}"
        }


@function_tool
async def get_time_based_greeting(ctx: RunContext) -> Dict[str, str]:
    """
    Generate an appropriate greeting based on current time.

    Returns a professional greeting appropriate for the current time of day.
    """
    try:
        now = datetime.now()
        hour = now.hour

        # Determine appropriate greeting
        if 5 <= hour < 12:
            greeting = "Good morning"
            time_context = "morning"
        elif 12 <= hour < 17:
            greeting = "Good afternoon"
            time_context = "afternoon"
        elif 17 <= hour < 21:
            greeting = "Good evening"
            time_context = "evening"
        else:
            greeting = "Hello"  # Late night/early morning
            time_context = "late hours"

        current_time = now.strftime("%I:%M %p")

        return {
            "status": "success",
            "greeting_info": {
                "greeting": greeting,
                "time_context": time_context,
                "current_time": current_time,
                "full_greeting": f"{greeting}! I'm Sofia, your AI voice assistant. How can I help you today?",
                "professional_greeting": f"{greeting}! This is Sofia. How may I assist you?"
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Unable to generate greeting: {str(e)}",
            "default_greeting": "Hello! I'm Sofia, your AI voice assistant. How can I help you today?"
        }


@function_tool
async def general_help(ctx: RunContext) -> Dict[str, Any]:
    """
    Provide general help information about Sofia's capabilities.

    Returns information about what Sofia can do and how users can interact with her.
    """
    return {
        "status": "success",
        "help_info": {
            "introduction": "I'm Sofia, your AI voice assistant. I'm here to help you with various tasks.",
            "capabilities": [
                "Answer general questions and provide information",
                "Help with basic tasks and guidance",
                "Provide current time and date information",
                "Engage in professional conversation",
                "Assist with various inquiries"
            ],
            "interaction_tips": [
                "Speak clearly and at a normal pace",
                "Feel free to ask questions or request help",
                "Let me know if you need clarification on anything",
                "Say 'goodbye' or 'thank you' when you're ready to end our conversation"
            ],
            "availability": "I'm available 24/7 to assist you"
        }
    }


@function_tool
async def end_conversation(ctx: RunContext) -> Dict[str, str]:
    """
    End the conversation politely and professionally.

    This tool signals the end of the conversation and provides a polite closing.
    """
    return {
        "status": "success",
        "message": "Thank you for speaking with me today. Have a great day!",
        "end_signal": "*[CALL_END_SIGNAL]*",
        "action": "conversation_ended"
    }