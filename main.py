import streamlit as st
import asyncio
import os
import json
from datetime import datetime

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from elevenlabs.client import ElevenLabs
from pydantic import BaseModel
from dotenv import load_dotenv
import requests

from tools import generate_video

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="AI Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'workflow_running' not in st.session_state:
    st.session_state.workflow_running = False
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'workflow_messages' not in st.session_state:
    st.session_state.workflow_messages = []

# Initialize API clients
try:
    if 'OPENAI_API_KEY' in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        elevenlabs_api_key = st.secrets["ELEVENLABS_API_KEY"]
        stability_api_key = st.secrets["STABILITY_API_KEY"]
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        stability_api_key = os.getenv("STABILITY_API_KEY")
        
    elevenlabs_client = ElevenLabs(api_key=elevenlabs_api_key)
    voice_id = "onwK4e9ZLuTAKqWW03F9"
except Exception as e:
    st.error(f"Error initializing API clients: {e}")
    st.stop()

# Define output structure for the script
class ScriptOutput(BaseModel):
    topic: str
    takeaway: str
    captions: list[str]

def generate_voiceovers(messages: list[str]) -> list[str]:
    """
    Generate voiceovers for a list of messages using ElevenLabs API.
    
    Args:
        messages: List of messages to convert to speech
        
    Returns:
        List of file paths to the generated audio files
    """
    os.makedirs("voiceovers", exist_ok=True)
    
    # Find the next available file index to avoid overwriting
    existing_files = [f for f in os.listdir("voiceovers") if f.startswith("voiceover_") and f.endswith(".mp3")]
    next_index = len(existing_files) + 1
    
    print(f"Generating {len(messages)} voiceovers starting from index {next_index}")
    print(f"Messages: {messages}")
    
    # Generate files starting from the next available index
    audio_file_paths = []
    
    # Handle progress display (may not be available in all contexts)
    progress_bar = None
    status_text = None
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
    except:
        pass
    
    for i, message in enumerate(messages):
        try:
            # Use sequential numbering starting from next_index
            file_index = next_index + i
            save_file_path = f"voiceovers/voiceover_{file_index}.mp3"
            
            if os.path.exists(save_file_path):
                msg = f"File {save_file_path} already exists, skipping generation."
                try:
                    if 'workflow_messages' in st.session_state:
                        st.session_state.workflow_messages.append(msg)
                except:
                    pass
                print(msg)
                audio_file_paths.append(save_file_path)
                continue

            try:
                if status_text:
                    status_text.text(f"Generating voiceover {file_index} ({i+1}/{len(messages)})...")
                if progress_bar:
                    progress_bar.progress((i+1) / len(messages))
            except:
                pass
            # Always print for debugging
            print(f"Generating voiceover {file_index} ({i+1}/{len(messages)}): {message}")
            
            # Generate audio with ElevenLabs
            print(f"Calling ElevenLabs API for: {message}")
            try:
                response = elevenlabs_client.text_to_speech.convert(
                    text=message,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_22050_32",
                )
                print("ElevenLabs API call successful")
                
                # Collect audio chunks
                audio_chunks = []
                for chunk in response:
                    if chunk:
                        audio_chunks.append(chunk)
                
                print(f"Collected {len(audio_chunks)} audio chunks")
                
                # Save to file
                with open(save_file_path, "wb") as f:
                    for chunk in audio_chunks:
                        f.write(chunk)
                        
                print(f"Saved audio to: {save_file_path}")
                
            except Exception as api_error:
                raise Exception(f"ElevenLabs API error: {api_error}")
                        
            # Log progress (handle both Streamlit and non-Streamlit contexts)
            msg = f"Voiceover {file_index} generated successfully: {save_file_path}"
            try:
                if 'workflow_messages' in st.session_state:
                    st.session_state.workflow_messages.append(msg)
            except:
                pass
            print(msg)
            audio_file_paths.append(save_file_path)
        
        except Exception as e:
            error_msg = f"Error generating voiceover for message: {message}. Error: {e}"
            try:
                if 'workflow_messages' in st.session_state:
                    st.session_state.workflow_messages.append(error_msg)
            except:
                pass
            print(error_msg)
            continue
    
    # Update final progress if available
    try:
        if progress_bar:
            progress_bar.progress(1.0)
        if status_text:
            status_text.text("Voiceover generation complete!")
    except:
        pass
    
    print(f"Voiceover generation complete! Generated {len(audio_file_paths)} files: {audio_file_paths}")
    return audio_file_paths

def generate_images(prompts: list[str]):
    """
    Generate images based on text prompts using Stability AI API.
    
    Args:
        prompts: List of text prompts to generate images from
    """
    seed = 42
    output_dir = "images"
    os.makedirs(output_dir, exist_ok=True)

    # API config
    stability_api_url = "https://api.stability.ai/v2beta/stable-image/generate/core"
    headers = {
        "Authorization": f"Bearer {stability_api_key}",
        "Accept": "image/*"
    }

    # Handle progress display (may not be available in all contexts)
    progress_bar = None
    status_text = None
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()
    except:
        pass
    
    for i, prompt in enumerate(prompts, 1):
        # Update progress display if available
        try:
            if status_text:
                status_text.text(f"Generating image {i}/{len(prompts)} for prompt: {prompt}")
            if progress_bar:
                progress_bar.progress(i / len(prompts))
        except:
            pass
        
        print(f"Generating image {i}/{len(prompts)} for prompt: {prompt}")

        # Skip if image already exists
        image_path = os.path.join(output_dir, f"image_{i}.webp")
        if not os.path.exists(image_path):
            # Prepare request payload
            payload = {
                "prompt": (None, prompt),
                "output_format": (None, "webp"),
                "height": (None, "1920"),
                "width": (None, "1080"),
                "seed": (None, str(seed))
            }

            try:
                response = requests.post(stability_api_url, headers=headers, files=payload)
                if response.status_code == 200:
                    with open(image_path, "wb") as image_file:
                        image_file.write(response.content)
                    msg = f"Image saved to {image_path}"
                    try:
                        if 'workflow_messages' in st.session_state:
                            st.session_state.workflow_messages.append(msg)
                    except:
                        pass
                    print(msg)
                else:
                    error_msg = f"Error generating image {i}: {response.json()}"
                    try:
                        if 'workflow_messages' in st.session_state:
                            st.session_state.workflow_messages.append(error_msg)
                    except:
                        pass
                    print(error_msg)
            except Exception as e:
                error_msg = f"Error generating image {i}: {e}"
                try:
                    if 'workflow_messages' in st.session_state:
                        st.session_state.workflow_messages.append(error_msg)
                except:
                    pass
                print(error_msg)
    
    # Update final progress if available
    try:
        if progress_bar:
            progress_bar.progress(1.0)
        if status_text:
            status_text.text("Image generation complete!")
    except:
        pass
    
    print("Image generation complete!")

async def run_workflow(user_input: str, use_ollama: bool = False):
    """Run the multi-agent workflow with the given user input."""
    
    # Initialize OpenAI client
    openai_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=openai_api_key
    )
    
    # Initialize Ollama client (if needed)
    ollama_client = OpenAIChatCompletionClient(
        model="llama3.2:latest",
        api_key="placeholder",
        response_format=ScriptOutput,
        base_url="http://localhost:11434/v1",
        model_info={
            "function_calling": True,
            "json_output": True,
            "vision": False,
            "family": "unknown"
        }
    )

    model_client = ollama_client if use_ollama else openai_client

    # Create agents
    script_writer = AssistantAgent(
        name="script_writer",
        model_client=model_client,
        system_message='''
            You are a creative assistant tasked with writing a script for a short video. 
            The script should consist of captions designed to be displayed on-screen, with the following guidelines:
                1.	Each caption must be short and impactful (no more than 8 words) to avoid overwhelming the viewer.
                2.	The script should have exactly 5 captions, each representing a key moment in the story.
                3.	The flow of captions must feel natural, like a compelling voiceover guiding the viewer through the narrative.
                4.	Always start with a question or a statement that keeps the viewer wanting to know more.
                5.  You must also include the topic and takeaway in your response.
                6.  The caption values must ONLY include the captions, no additional meta data or information.

                Output your response in the following JSON format:
                {
                    "topic": "topic",
                    "takeaway": "takeaway",
                    "captions": [
                        "caption1",
                        "caption2",
                        "caption3",
                        "caption4",
                        "caption5"
                    ]
                }
        '''
    )

    voice_actor = AssistantAgent(
        name="voice_actor",
        model_client=model_client,
        tools=[generate_voiceovers],
        system_message='''
            You are a helpful agent tasked with generating and saving voiceovers.
            Only respond with 'TERMINATE' once files are successfully saved locally.
        '''
    )

    graphic_designer = AssistantAgent(
        name="graphic_designer",
        model_client=model_client,
        tools=[generate_images],
        system_message='''
            You are a helpful agent tasked with generating and saving images for a short video.
            You are given a list of captions.
            You will convert each caption into an optimized prompt for the image generation tool.
            Your prompts must be concise and descriptive and maintain the same style and tone as the captions while ensuring continuity between the images.
            Your prompts must mention that the output images MUST be in: "Abstract Art Style / Ultra High Quality." (Include with each prompt)
            You will then use the prompts list to generate images for each provided caption.
            Only respond with 'TERMINATE' once the files are successfully saved locally.
        '''
    )

    director = AssistantAgent(
        name="director",
        model_client=model_client,
        tools=[generate_video],
        system_message='''
            You are a helpful agent tasked with generating a short video.
            You are given a list of captions which you will use to create the short video.
            Remove any characters that are not alphanumeric or spaces from the captions.
            You will then use the captions list to generate a video.
            Only respond with 'TERMINATE' once the video is successfully generated and saved locally.
        '''
    )

    # Set up termination condition
    termination = TextMentionTermination("TERMINATE")
    
    # Create sequential execution order
    agent_team = RoundRobinGroupChat(
        [script_writer, voice_actor, graphic_designer, director],
        termination_condition=termination,
        max_turns=4
    )

    # Run the team with the user input
    try:
        stream = agent_team.run_stream(task=user_input)
        messages = []
        async for message in stream:
            messages.append(message)
            # Update Streamlit with progress
            if hasattr(message, 'content') and message.content:
                st.session_state.workflow_messages.append(f"{message.source}: {message.content}")
        
        return messages
    except Exception as e:
        st.error(f"Error running workflow: {e}")
        return []

def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("🎬 AI Video Generator")
    st.markdown("""
    Create AI-powered short videos with our multi-agent system! 
    Enter a topic and watch as our agents collaborate to generate a script, voiceovers, images, and final video.
    """)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    use_ollama = st.sidebar.checkbox("Use Ollama (Local LLM)", value=False)
    
    if use_ollama:
        st.sidebar.info("Make sure Ollama is running locally on port 11434")
    
    # Clear generated content button
    if st.sidebar.button("🗑️ Clear All Generated Content"):
        st.session_state.generated_content = None
        st.session_state.workflow_messages = []
        # Clean up generated files
        for folder in ["voiceovers", "images"]:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
        if os.path.exists("yt_shorts_video.mp4"):
            os.remove("yt_shorts_video.mp4")
        st.success("All generated content cleared!")
        st.rerun()
    
    # Main input
    with st.form("video_generation_form"):
        user_input = st.text_area(
            "Enter your video topic or description:",
            placeholder="Create a short AI-generated video about space exploration",
            height=100
        )
        
        submitted = st.form_submit_button(
            "🚀 Generate Video", 
            disabled=st.session_state.workflow_running,
            width='stretch'
        )
    
    # Run workflow when form is submitted
    if submitted and user_input.strip():
        st.session_state.workflow_running = True
        st.session_state.workflow_messages = []
        
        with st.spinner("Running multi-agent workflow..."):
            
            # Run the async workflow
            try:
                messages = asyncio.run(run_workflow(user_input, use_ollama))
                st.session_state.generated_content = {
                    'input': user_input,
                    'timestamp': datetime.now(),
                    'messages': messages
                }
                st.success("✅ Video generation complete!")
            except Exception as e:
                st.error(f"❌ Error during workflow: {e}")
            finally:
                st.session_state.workflow_running = False
        
        st.rerun()
    
    # Display workflow messages
    if st.session_state.workflow_messages:
        st.subheader("📝 Workflow Log")
        for msg in st.session_state.workflow_messages:
            st.text(msg)
    
    # Display results
    if st.session_state.generated_content:
        st.subheader("🎬 Generated Content")
        
        # Show input and timestamp
        content = st.session_state.generated_content
        st.info(f"**Topic:** {content['input']}")
        st.caption(f"Generated on: {content['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display generated files
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎵 Voiceovers")
            if os.path.exists("voiceovers"):
                voiceover_files = [f for f in os.listdir("voiceovers") if f.endswith(".mp3")]
                for audio_file in sorted(voiceover_files):
                    st.audio(f"voiceovers/{audio_file}")
        
        with col2:
            st.subheader("🖼️ Images")
            if os.path.exists("images"):
                image_files = [f for f in os.listdir("images") if f.endswith((".webp", ".png", ".jpg"))]
                for img_file in sorted(image_files):
                    st.image(f"images/{img_file}", caption=img_file, width='stretch')
        
        with col3:
            st.subheader("🎥 Final Video")
            if os.path.exists("yt_shorts_video.mp4"):
                st.video("yt_shorts_video.mp4")
                
                # Download button for video
                with open("yt_shorts_video.mp4", "rb") as video_file:
                    st.download_button(
                        label="📥 Download Video",
                        data=video_file.read(),
                        file_name="generated_video.mp4",
                        mime="video/mp4",
                        width='stretch'
                    )
            else:
                st.info("Video file not found. Check the workflow log for errors.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using Streamlit, AutoGen, OpenAI, ElevenLabs, and Stability AI"
    )

if __name__ == "__main__":
    main()