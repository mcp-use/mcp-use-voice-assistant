"""
Voice-First AI Personal Assistant with MCP Integration (Improved Version)

This example demonstrates a voice-enabled personal assistant that uses:
- Speech-to-text for voice input (OpenAI Whisper)
- MCPAgent with multiple MCP servers (Linear, filesystem)
- Text-to-speech for voice output (ElevenLabs speak or system TTS)

This version includes better error handling and fallback options.
"""

import asyncio
import io
import json
import os
import sys
import tempfile
import wave

import numpy as np
import openai
import pyaudio
import pygame
import pyttsx3
from elevenlabs import play
from elevenlabs.client import ElevenLabs
from elevenlabs.types.voice_settings import VoiceSettings
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

TTS_ENGINE = pyttsx3.init()


class VoiceAssistant:
    """Improved voice-enabled AI assistant with better error handling."""

    def __init__(
        self,
        openai_api_key: str,
        elevenlabs_api_key: str | None = None,
        model: str = "o4-mini",
        elevenlabs_voice_id: str = "ZF6FPAbjXT4488VcRRnw",
        silence_threshold: int = 500,
        silence_duration: float = 1.5,
        mcp_config: dict | None = None,
        notes_dir: str | None = None,
        system_prompt: str | None = None,
    ):
        """Initialize the voice assistant.

        Args:
            openai_api_key: OpenAI API key for Whisper and GPT models
            elevenlabs_api_key: Optional ElevenLabs API key for TTS
            model: OpenAI model to use (default: gpt-4)
            elevenlabs_voice_id: ElevenLabs voice ID (default: Rachel)
            silence_threshold: Audio silence detection threshold
            silence_duration: How long to wait after speech stops
            mcp_config: Optional MCP server configuration dict
            notes_dir: Directory for storing notes (default: temp dir)
            system_prompt: Optional custom system prompt for the assistant
        """
        # Audio configuration
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration

        # Initialize audio components
        self.audio = pyaudio.PyAudio()
        pygame.mixer.init()

        # OpenAI client for speech-to-text
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.model = model

        # ElevenLabs client for text-to-speech
        self.elevenlabs_client = None
        self.elevenlabs_voice_id = elevenlabs_voice_id
        if elevenlabs_api_key:
            self.elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)

        # MCP configuration
        self.mcp_config = mcp_config
        self.mcp_client = None
        self.agent = None
        self.system_prompt = system_prompt or (
            "You are a helpful voice assistant with access to various tools. Your name is mcp-use."
            "Be concise in your responses since they will be spoken aloud. Summarize your results."
            "Behave like a great motivational speaker, and motivate me throughout the conversation."
        )

        # Create a proper notes directory
        if notes_dir:
            self.notes_dir = notes_dir
        else:
            self.notes_dir = os.path.join(tempfile.gettempdir(), "voice_assistant_notes")
        os.makedirs(self.notes_dir, exist_ok=True)

    def _substitute_env_vars(self, config: dict) -> dict:
        """Recursively substitute environment variable placeholders in config."""
        if isinstance(config, dict):
            result = {}
            for key, value in config.items():
                result[key] = self._substitute_env_vars(value)
            return result

    async def initialize_mcp(self):
        """Initialize MCP client and agent with proper error handling."""
        print("Initializing MCP servers...")

        # Use provided config or load from file
        if self.mcp_config:
            config = self.mcp_config
        else:
            # Try to load from mcp_servers.json
            config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_servers.json")
            if os.path.exists(config_file):
                with open(config_file) as f:
                    config = json.load(f)
                # Replace environment variable placeholders
                config = self._substitute_env_vars(config)

        try:
            # Create MCP client
            self.mcp_client = MCPClient.from_dict(config)

            # Create LLM
            llm = ChatOpenAI(model=self.model)

            # Create agent with memory
            self.agent = MCPAgent(
                llm=llm,
                client=self.mcp_client,
                max_steps=10,
                memory_enabled=True,
                system_prompt=self.system_prompt,
            )
            await self.agent.initialize()

            print("✓ MCP servers initialized successfully!")
            return True

        except Exception as e:
            print(f"✗ Error initializing MCP: {e}")
            return False

    def detect_silence(self, audio_data: bytes) -> bool:
        """Detect if audio contains silence."""
        audio_array = np.frombuffer(audio_data, dtype=np.int16)
        return np.max(np.abs(audio_array)) < self.silence_threshold

    def record_audio(self) -> bytes | None:
        """Record audio from microphone."""
        print("\nListening... (speak now)")

        try:
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk,
            )

            frames = []
            silence_frames = 0
            silence_frame_threshold = int(self.rate / self.chunk * self.silence_duration)
            has_speech = False

            while True:
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)

                if self.detect_silence(data):
                    silence_frames += 1
                    if has_speech and silence_frames > silence_frame_threshold:
                        break
                else:
                    silence_frames = 0
                    has_speech = True

                if len(frames) > self.rate / self.chunk * 30:
                    break

            stream.stop_stream()
            stream.close()

            if not has_speech:
                print("No speech detected.")
                return None

            print("Processing...")
            return b"".join(frames)

        except Exception as e:
            print(f"Error recording audio: {e}")
            return None

    def audio_to_text(self, audio_data: bytes) -> str | None:
        """Convert audio to text using OpenAI Whisper."""
        try:
            # Create WAV file in memory
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, "wb") as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(audio_data)

            wav_buffer.seek(0)
            wav_buffer.name = "audio.wav"

            # Transcribe using Whisper
            response = self.openai_client.audio.transcriptions.create(model="whisper-1", file=wav_buffer, language="en")

            return response.text.strip()

        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    async def text_to_speech(self, text: str) -> bool:
        """Convert text to speech using available methods."""
        # Try ElevenLabs first
        if self.elevenlabs_client:
            try:
                # Generate audio using ElevenLabs
                audio = self.elevenlabs_client.text_to_speech.convert(
                    text=text,
                    voice_id=self.elevenlabs_voice_id,
                    model_id="eleven_multilingual_v2",  # Best for high-quality output and multilingual
                    output_format="mp3_44100_128",  # Balanced quality + size
                    optimize_streaming_latency="2",  # Optional: best for real-time feel without delay
                    voice_settings=VoiceSettings(speed=1.1),
                )

                # Play the audio
                play(audio)
                return True
            except Exception as e:
                print(f"ElevenLabs TTS failed: {e}")

        # Final fallback: just print
        return False

    async def process_command(self, text: str) -> str:
        """Process user command with MCP agent."""
        print(f"\nYou said: {text}")

        # Special commands
        if text.lower() in ["exit", "quit", "goodbye"]:
            return "Goodbye! Have a great day!"

        if text.lower() == "clear":
            if self.agent:
                self.agent.clear_conversation_history()
            return "Conversation history cleared."

        # Process with MCP agent
        if not self.agent:
            return "Sorry, the assistant is not properly initialized."

        try:
            response = await self.agent.run(text)
            return response
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"

    async def run(self):
        """Main loop for the voice assistant."""
        print("\n===== Voice-First AI Assistant (Improved) =====")
        print("\nCommands: 'help', 'clear', 'exit'")
        print("===============================================\n")

        # Initialize MCP
        if not await self.initialize_mcp():
            print("Failed to initialize MCP. Exiting.")
            return

        try:
            while True:
                # Record audio or get text input
                audio_data = self.record_audio()
                if not audio_data:
                    continue

                # Convert to text
                text = self.audio_to_text(audio_data)
                if not text:
                    continue

                # Process command
                response = await self.process_command(text)
                print(f"\nAssistant: {response}")

                # Check for exit
                if text.lower() in ["exit", "quit", "goodbye"]:
                    break

                # Try to speak the response
                await self.text_to_speech(response)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
        finally:
            # Cleanup
            self.audio.terminate()
            pygame.mixer.quit()
            if self.mcp_client and self.mcp_client.sessions:
                await self.mcp_client.close_all_sessions()


async def main():
    """Run the improved voice assistant."""
    # Example usage - in production, load these from environment or config
    import argparse

    from dotenv import load_dotenv

    # Load environment variables if .env exists
    load_dotenv()

    parser = argparse.ArgumentParser(description="Voice-enabled AI assistant")
    parser.add_argument("--openai-api-key", default=os.getenv("OPENAI_API_KEY"), help="OpenAI API key")
    parser.add_argument("--elevenlabs-api-key", default=os.getenv("ELEVENLABS_API_KEY"), help="ElevenLabs API key")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4"), help="OpenAI model to use")
    parser.add_argument(
        "--voice-id", default=os.getenv("ELEVENLABS_VOICE_ID", "ZF6FPAbjXT4488VcRRnw"), help="ElevenLabs voice ID"
    )
    parser.add_argument(
        "--silence-threshold",
        type=int,
        default=int(os.getenv("VOICE_SILENCE_THRESHOLD", "500")),
        help="Silence detection threshold",
    )
    parser.add_argument(
        "--silence-duration",
        type=float,
        default=float(os.getenv("VOICE_SILENCE_DURATION", "1.5")),
        help="Silence duration",
    )
    parser.add_argument(
        "--system-prompt", default=os.getenv("ASSISTANT_SYSTEM_PROMPT"), help="Custom system prompt for the assistant"
    )

    args = parser.parse_args()

    if not args.openai_api_key:
        print("Error: OpenAI API key is required")
        print("Set OPENAI_API_KEY environment variable or use --openai-api-key")
        sys.exit(1)

    assistant = VoiceAssistant(
        openai_api_key=args.openai_api_key,
        elevenlabs_api_key=args.elevenlabs_api_key,
        model=args.model,
        elevenlabs_voice_id=args.voice_id,
        silence_threshold=args.silence_threshold,
        silence_duration=args.silence_duration,
        system_prompt=args.system_prompt,
    )
    await assistant.run()


if __name__ == "__main__":
    asyncio.run(main())
