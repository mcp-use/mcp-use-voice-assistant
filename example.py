#!/usr/bin/env python3
"""Example usage of the MCP Voice Assistant."""

import asyncio
import os
import sys
from dotenv import load_dotenv
from voice_assistant import VoiceAssistant

async def main():
    """Run the voice assistant with custom configuration."""
    # Load environment variables
    load_dotenv()
    
    # Get API keys from environment
    openai_key = os.getenv("OPENAI_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not openai_key:
        print("Error: Please set OPENAI_API_KEY in your .env file")
        sys.exit(1)
    
    # MCP configuration will be loaded from mcp_servers.json by default
    # You can still provide a custom config if needed:
    # custom_mcp_config = {"mcpServers": {...}}
    
    # Custom system prompt (optional)
    custom_prompt = os.getenv("ASSISTANT_SYSTEM_PROMPT") or (
        "You are a friendly and helpful AI assistant named Claude. "
        "Be concise but warm in your responses. "
        "You have access to various tools to help users with tasks."
    )
    
    # Create assistant instance
    assistant = VoiceAssistant(
        openai_api_key=openai_key,
        elevenlabs_api_key=elevenlabs_key,
        model=os.getenv("OPENAI_MODEL", "gpt-4"),  # or "gpt-3.5-turbo" for faster responses
        elevenlabs_voice_id=os.getenv("ELEVENLABS_VOICE_ID", "ZF6FPAbjXT4488VcRRnw"),  # Rachel voice
        silence_threshold=int(os.getenv("VOICE_SILENCE_THRESHOLD", "500")),
        silence_duration=float(os.getenv("VOICE_SILENCE_DURATION", "1.5")),
        system_prompt=custom_prompt,
        # mcp_config=custom_mcp_config,  # Optional: override default config
    )
    
    # Run the assistant
    await assistant.run()

if __name__ == "__main__":
    asyncio.run(main())