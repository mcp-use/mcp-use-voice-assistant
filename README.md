<h1 align="center"> MCP Voice Assistant </h1>

<div align="center" style="margin: 0 auto; max-width: 50%;">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="static/logo_white.svg">
    <source media="(prefers-color-scheme: light)" srcset="static/logo_black.svg">
    <img alt="mcp use logo" src="./static/logo-white.svg" width="80%" style="margin: 20px auto;">
  </picture>
</div>

<p align="center">
    <a href="https://pypi.org/project/mcp_use/" alt="PyPI Version">
        <img src="https://img.shields.io/pypi/v/mcp_use.svg"/></a>
    <a href="https://pypi.org/project/mcp_use/" alt="PyPI Downloads">
        <img src="https://static.pepy.tech/badge/mcp-use" /></a>
    <a href="https://pypi.org/project/mcp_use/" alt="Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/mcp_use.svg" /></a>
    <a href="https://docs.mcp-use.io" alt="Documentation">
        <img src="https://img.shields.io/badge/docs-mcp--use.io-blue" /></a>
    <a href="https://mcp-use.io" alt="Website">
        <img src="https://img.shields.io/badge/website-mcp--use.io-blue" /></a>
    <a href="https://github.com/pietrozullo/mcp-use/blob/main/LICENSE" alt="License">
        <img src="https://img.shields.io/github/license/pietrozullo/mcp-use" /></a>
    <a href="https://github.com/astral-sh/ruff" alt="Code style: Ruff">
        <img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" /></a>
    <a href="https://github.com/pietrozullo/mcp-use/stargazers" alt="GitHub stars">
        <img src="https://img.shields.io/github/stars/pietrozullo/mcp-use?style=social" /></a>
    </p>
    <p align="center">
    <a href="https://x.com/pietrozullo" alt="Twitter Follow - Pietro">
        <img src="https://img.shields.io/twitter/follow/Pietro?style=social" /></a>
    <a href="https://x.com/pederzh" alt="Twitter Follow - Luigi">
        <img src="https://img.shields.io/twitter/follow/Luigi?style=social" /></a>
    <a href="https://discord.gg/XkNkSkMz3V" alt="Discord">
        <img src="https://dcbadge.limes.pink/api/server/XkNkSkMz3V?style=flat" /></a>
</p>

# MCP Voice Assistant

A voice-enabled AI personal assistant that leverages the Model Context Protocol (MCP) to integrate multiple tools and services through natural voice interactions.

## Features

- 🎤 **Voice Input**: Real-time speech-to-text using OpenAI Whisper
- 🔊 **Voice Output**: High-quality text-to-speech using ElevenLabs (with pyttsx3 fallback)
- 🤖 **AI-Powered**: Conversational AI with memory persistence
- 🌐 **Multiple Model Providers**: Works with any LLM provider that supports tool calling (OpenAI, Anthropic, Groq, LLama, etc.)
- 🛠️ **Multi-Tool Integration**: Seamlessly connects to any MCP servers:
- 💾 **Conversational Memory**: Maintains context across interactions
- 🎯 **Extensible**: Easy to add new MCP servers and capabilities

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ User Voice  │ --> │ Speech-to-   │ --> │  LLM with   │ --> │ Text-to-     │
│   Input     │     │ Text (STT)   │     │  MCPAgent   │     │ Speech (TTS) │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                         Whisper                 │                ElevenLabs
                                                 │
                                          ┌──────▼──────┐
                                          │ MCP Servers │
                                          ├─────────────┤
                                          │ • Linear    │
                                          │ • Playwright│
                                          │ • Filesystem│
                                          └─────────────┘
```

## Installation

### Prerequisites

1. **Python 3.11+**
2. **uv** (Python package manager): `pip install uv` or `pipx install uv`
3. **Node.js** (for MCP servers)
4. **System dependencies**:
   - macOS: `brew install portaudio`
   - Ubuntu/Debian: `sudo apt-get install portaudio19-dev`
   - Windows: PyAudio wheel includes PortAudio


### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-voice-assistant.git
cd mcp-voice-assistant

# Create a virtual environment with uv
uv venv

# Activate the virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install in development mode
uv pip install -e .

# Or install directly
uv pip install .
```

## Configuration

### Environment Variables

Create a `.env` file in your project root (see `.env.example` for a complete template):

```bash
# Required
OPENAI_API_KEY=your-openai-api-key

# Optional but recommended for better voice output
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Optional - Model Provider Settings
# You can use any model provider that supports tool calling
OPENAI_API_KEY=your-openai-api-key              # For OpenAI models
ANTHROPIC_API_KEY=your-anthropic-api-key        # For Claude models
GROQ_API_KEY=your-groq-api-key                  # For Groq models

# Model selection (defaults to gpt-4)
OPENAI_MODEL=gpt-4                              # OpenAI: gpt-4, gpt-4-turbo, gpt-3.5-turbo
# Or use other providers:
# ANTHROPIC_MODEL=claude-3-5-sonnet-20240620   # Anthropic Claude
# GROQ_MODEL=llama3-8b-8192                    # Groq LLama

# Voice Settings
ELEVENLABS_VOICE_ID=ZF6FPAbjXT4488VcRRnw      # Default: Rachel voice

# Optional - Audio Configuration
VOICE_SILENCE_THRESHOLD=500                     # Lower = more sensitive
VOICE_SILENCE_DURATION=1.5                      # Seconds to wait after speech

# Optional - Assistant Configuration
ASSISTANT_SYSTEM_PROMPT="You are a helpful voice assistant..."  # Customize personality

# Optional - MCP Server Specific
LINEAR_API_KEY=your-linear-api-key              # For Linear integration
```

All environment variables can be overridden via command-line arguments when using the CLI.

### MCP Server Configuration

The assistant loads MCP server configurations from `mcp_servers.json` in the project root. By default, it includes:

- **playwright**: Web automation and browser control
- **linear**: Task and project management

To add more servers, edit `mcp_servers.json` or copy `mcp_servers.example.json` which includes additional servers like:
- filesystem, github, gitlab, google-drive, postgres, sqlite, slack, memory, puppeteer, brave-search, fetch

Environment variables in the config (like `${GITHUB_PERSONAL_ACCESS_TOKEN}`) are automatically substituted from your `.env` file.

To override the default configuration programmatically:

```python
config = {
    "mcpServers": {
        "your_server": {
            "command": "npx",
            "args": ["-y", "@your-org/mcp-server"],
            "env": {"YOUR_API_KEY": "${YOUR_API_KEY}"}
        }
    }
}
```


### Command Line

After installation, you can run the assistant directly:

```bash
# Using environment variables from .env file
mcp-voice-assistant

# Override specific settings via command line
mcp-voice-assistant --model gpt-3.5-turbo --silence-threshold 300

# Provide all settings via command line (no .env needed)
mcp-voice-assistant \
  --openai-api-key YOUR_KEY \
  --elevenlabs-api-key YOUR_ELEVENLABS_KEY \
  --model gpt-4 \
  --voice-id ZF6FPAbjXT4488VcRRnw \
  --silence-threshold 500 \
  --silence-duration 1.5

# See all available options
mcp-voice-assistant --help
```

**Note**: Command-line arguments take precedence over environment variables.


### Changing Model Provider

The voice assistant supports multiple LLM providers through LangChain. Any model with tool calling capabilities can be used:

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_groq import ChatGroq

# Using OpenAI (default)
assistant = VoiceAssistant(
    openai_api_key="your-key",
    model="gpt-4"  # or gpt-4-turbo, gpt-3.5-turbo
)

# Using Anthropic Claude
llm = ChatAnthropic(
    api_key="your-anthropic-key",
    model="claude-3-5-sonnet-20240620"
)
assistant = VoiceAssistant(
    llm=llm,  # Pass custom LLM instance
    elevenlabs_api_key="your-key"
)

# Using Groq
llm = ChatGroq(
    api_key="your-groq-key",
    model="llama3-8b-8192"
)
assistant = VoiceAssistant(
    llm=llm,
    elevenlabs_api_key="your-key"
)
```

**Note**: Only models with tool calling capabilities can be used. Check your model provider's documentation for supported models.

### Changing Voice Settings

Pass different parameters when initializing:

```python
assistant = VoiceAssistant(
    openai_api_key="your-key",
    elevenlabs_api_key="your-key",
    elevenlabs_voice_id="different-voice-id",  # Change voice
    silence_threshold=300,  # More sensitive
    silence_duration=2.0,   # Wait longer
    model="gpt-3.5-turbo"  # Faster model
)
```

## Troubleshooting

### Common Issues

1. **No Audio Input Detected**
   - Check microphone permissions
   - Lower the `silence_threshold` value
   - Verify PyAudio: `python -c "import pyaudio; pyaudio.PyAudio()"`

2. **TTS Not Working**
   - Verify API keys are set correctly
   - Check API quotas
   - System will fall back to pyttsx3 if ElevenLabs fails

3. **MCP Server Connection Issues**
   - Ensure Node.js is installed
   - Check internet connection for npx downloads
   - Verify API keys for specific servers

4. **High Latency**
   - Use faster LLM model (e.g., `gpt-3.5-turbo`)
   - Reduce `max_steps` in MCPAgent
   - Consider using local models

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on top of [mcp-use](https://github.com/modelcontextprotocol/mcp-use)
- Uses [OpenAI Whisper](https://openai.com/research/whisper) for speech recognition
- Voice synthesis powered by [ElevenLabs](https://elevenlabs.io)
- MCP servers from the [Model Context Protocol](https://modelcontextprotocol.org) ecosystem

## Support

- 📧 Email: your.email@example.com
- 💬 Discord: [Join our server](https://discord.gg/yourinvite)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/mcp-voice-assistant/issues)
- 📖 Documentation: [Full Docs](https://docs.yourproject.com)