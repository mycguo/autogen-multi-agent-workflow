# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains two multi-agent implementations for creating AI-powered short videos:

### AutoGen Implementation (`main.py`)
AutoGen 0.4 multi-agent system with four specialized agents:
- **Script Writer**: Generates structured JSON with topic, takeaway, and 5 captions (max 8 words each)
- **Voice Actor**: Converts captions to voiceovers using ElevenLabs API
- **Graphic Designer**: Creates images from captions using Stability AI API
- **Director**: Assembles final video with Ken Burns effects, text overlays, and background music

### CrewAI Implementation (`crewai_app.py`)
CrewAI framework with role-based agent collaboration:
- **Script Writer Agent**: Creative writer with compelling caption generation
- **Voice Actor Agent**: Professional voice actor using TTS technology
- **Graphic Designer Agent**: Digital artist specializing in abstract art
- **Video Director Agent**: Experienced director for final assembly

## Core Architecture

### Multi-Agent Workflow (`main.py`)
- Uses `RoundRobinGroupChat` with 4-agent sequential execution
- Each agent runs once per workflow cycle with `TextMentionTermination("TERMINATE")`
- Agents communicate through shared message context and file outputs
- Interactive console loop for user input

### Video Generation Pipeline (`tools.py`)
- **FFmpeg-based video assembly**: Ken Burns effects, text overlays, audio mixing
- **Text sanitization**: Handles FFmpeg drawtext filter escaping requirements
- **Temporary file management**: Creates isolated temp directories for processing
- **Audio synchronization**: Precisely times voiceovers with image segments

### API Integrations
- **OpenAI**: Primary LLM client (configurable to use Ollama for local execution)
- **ElevenLabs**: Text-to-speech with voice ID `onwK4e9ZLuTAKqWW03F9`
- **Stability AI**: Image generation with consistent "Abstract Art Style / Ultra High Quality" prompting

## Development Commands

### Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Applications
```bash
# AutoGen Streamlit App
streamlit run main.py

# CrewAI Streamlit App  
streamlit run crewai_app.py

# Direct Python execution (console mode)
python main.py
```

### Required Environment Variables
Create `.env` file with:
```
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
STABILITY_API_KEY=your-stability-ai-api-key
```

## Key Implementation Details

### Agent Configuration
- **Script Writer**: Returns structured `ScriptOutput` (Pydantic model) with exactly 5 captions
- **Voice Actor**: Uses `generate_voiceovers()` tool, saves to `voiceovers/` directory
- **Graphic Designer**: Uses `generate_images()` tool, saves to `images/` directory  
- **Director**: Uses `generate_video()` tool, outputs final `yt_shorts_video.mp4`

### File Output Structure
```
voiceovers/voiceover_1.mp3, voiceover_2.mp3, ...
images/image_1.webp, image_2.webp, ...
yt_shorts_video.mp4 (final output)
```

### LLM Model Switching
To use local Ollama instead of OpenAI:
- Change `model_client=openai_client` to `model_client=ollama_client` in agent definitions
- Ensure Ollama is running locally on port 11434
- Current Ollama model: `llama3.2:latest`

### FFmpeg Dependencies
The video generation requires FFmpeg with:
- `libx264` codec for video encoding
- System fonts (uses Verdana on macOS: `/System/Library/Fonts/Supplemental/Verdana.ttf`)
- Background music file at `music/cosmos.mp3` (not included)

### Error Handling Patterns
- File existence checks prevent duplicate API calls
- Graceful error continuation for individual voiceover/image generation failures
- Input validation ensures matching counts between captions, images, and voiceovers
- Temporary directory cleanup in finally blocks

## Framework Comparison

### AutoGen Features
- **Round-robin execution** with max turn limits
- **Function calling** integration with tools
- **Termination conditions** for workflow control
- **Streaming responses** with real-time updates
- **Flexible configuration** for different LLM providers

### CrewAI Features  
- **Role-based agents** with specialized backstories and goals
- **Sequential task execution** with dependency management
- **Context sharing** between tasks automatically
- **Built-in collaboration** patterns and delegation
- **Structured workflow** definition with expected outputs

## Agent System Messages

### AutoGen Agent Constraints
- **Script Writer**: Exactly 5 captions, max 8 words each, JSON output format
- **Voice Actor**: Only terminates after successful file saves
- **Graphic Designer**: Maintains "Abstract Art Style" consistency across images
- **Director**: Sanitizes caption text for FFmpeg compatibility

### CrewAI Agent Roles
- **Script Writer**: Creative writer with compelling storytelling background
- **Voice Actor**: Professional narrator with TTS expertise
- **Graphic Designer**: Digital artist specializing in abstract conceptual imagery
- **Video Director**: Experienced director focused on short-form content assembly