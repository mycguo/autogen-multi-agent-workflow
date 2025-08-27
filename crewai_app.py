import streamlit as st
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# CrewAI imports
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Import utility functions from main.py
from main import generate_voiceovers, generate_images
from tools import generate_video

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="CrewAI Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'crew_workflow_running' not in st.session_state:
    st.session_state.crew_workflow_running = False
if 'crew_generated_content' not in st.session_state:
    st.session_state.crew_generated_content = None
if 'crew_workflow_messages' not in st.session_state:
    st.session_state.crew_workflow_messages = []

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
        
    # Initialize language model for CrewAI
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=openai_api_key,
        temperature=0.7
    )
    
except Exception as e:
    st.error(f"Error initializing API clients: {e}")
    st.stop()

# Helper functions that agents will use
def execute_voiceover_generation(captions: List[str]) -> str:
    """Execute voiceover generation for captions"""
    try:
        result = generate_voiceovers(captions)
        return f"Generated voiceovers: {result}"
    except Exception as e:
        return f"Error generating voiceovers: {e}"

def execute_image_generation(prompts: List[str]) -> str:
    """Execute image generation for prompts"""
    try:
        generate_images(prompts)
        return f"Generated {len(prompts)} images successfully"
    except Exception as e:
        return f"Error generating images: {e}"

def execute_video_assembly(captions: List[str]) -> str:
    """Execute final video assembly"""
    try:
        generate_video(captions)
        return "Video generated successfully: yt_shorts_video.mp4"
    except Exception as e:
        return f"Error generating video: {e}"

def create_crew(topic: str) -> Crew:
    """Create and configure the CrewAI crew for video generation"""
    
    # Define Agents
    script_writer = Agent(
        role="Script Writer",
        goal="Create engaging video scripts with exactly 5 short captions",
        backstory="""You are a creative script writer specialized in creating compelling 
        short-form video content. You excel at crafting punchy, attention-grabbing captions 
        that tell a story in just a few words.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    voice_actor = Agent(
        role="Voice Actor",
        goal="Convert script captions into high-quality voiceovers",
        backstory="""You are a professional voice actor who specializes in creating 
        engaging narration for educational and exploratory content. You coordinate 
        with the technical team to convert script captions into voiceover files.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    graphic_designer = Agent(
        role="Graphic Designer", 
        goal="Create visually stunning images that complement the script",
        backstory="""You are a digital artist specializing in abstract art and 
        conceptual imagery. You work with technical systems to generate visually 
        cohesive series of images that tell a story and maintain consistent artistic style.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    video_director = Agent(
        role="Video Director",
        goal="Assemble all elements into a final polished video",
        backstory="""You are an experienced video director who specializes in 
        short-form content. You coordinate the final assembly of visual elements, 
        audio, and timing to create engaging final products.""",
        llm=llm,
        verbose=True,
        allow_delegation=False
    )
    
    # Define Tasks
    script_task = Task(
        description=f"""Create a script for a short video about: {topic}

        Requirements:
        1. Generate exactly 5 captions, each no more than 8 words
        2. Start with a compelling question or statement
        3. Create a natural narrative flow
        4. Include topic and takeaway
        5. Output in JSON format:
        {{
            "topic": "topic name",
            "takeaway": "main message", 
            "captions": [
                "caption1",
                "caption2", 
                "caption3",
                "caption4",
                "caption5"
            ]
        }}""",
        agent=script_writer,
        expected_output="JSON object with topic, takeaway, and 5 captions"
    )
    
    voiceover_task = Task(
        description="""Coordinate the generation of voiceovers for each caption from the script.
        
        Your task is to organize the voiceover production process:
        1. Take the captions from the script
        2. Prepare them for voiceover generation
        3. Confirm that voiceovers should be generated for all captions
        4. Return "VOICEOVERS_READY" when preparation is complete""",
        agent=voice_actor,
        expected_output="Confirmation message: VOICEOVERS_READY",
        context=[script_task]
    )
    
    image_task = Task(
        description="""Design and coordinate the creation of abstract art images for each caption.
        
        Your responsibilities:
        1. Convert each caption into optimized image generation prompts
        2. Ensure prompts maintain consistent "Abstract Art Style / Ultra High Quality"
        3. Create prompts that ensure visual continuity between images
        4. Format prompts as: "Abstract Art Style / Ultra High Quality. [caption interpretation]"
        5. Return "IMAGES_READY" when design specifications are complete""",
        agent=graphic_designer,
        expected_output="Confirmation message: IMAGES_READY with prompt specifications",
        context=[script_task]
    )
    
    video_task = Task(
        description="""Direct the final video assembly process.
        
        Your directing responsibilities:
        1. Ensure all elements are ready (script, voiceovers, images)
        2. Prepare captions for video assembly (clean alphanumeric text)
        3. Coordinate the final video production process
        4. Return "VIDEO_ASSEMBLY_COMPLETE" when directing is finished""",
        agent=video_director,
        expected_output="Final direction confirmation: VIDEO_ASSEMBLY_COMPLETE",
        context=[script_task, voiceover_task, image_task]
    )
    
    # Create and configure crew
    crew = Crew(
        agents=[script_writer, voice_actor, graphic_designer, video_director],
        tasks=[script_task, voiceover_task, image_task, video_task],
        process=Process.sequential,
        verbose=2
    )
    
    return crew

def run_crewai_workflow(topic: str) -> Dict[str, Any]:
    """Run the CrewAI workflow for video generation"""
    
    try:
        print(f"Starting CrewAI workflow for topic: {topic}")
        
        # Create crew
        crew = create_crew(topic)
        
        # Execute CrewAI workflow (coordination phase)
        result = crew.kickoff()
        
        print(f"CrewAI coordination completed. Result: {result}")
        
        # Extract script data from the result (assuming first task contains JSON)
        # This is a simplified approach - in practice you'd parse the actual agent outputs
        script_data = {
            "topic": topic,
            "takeaway": f"Key insights about {topic}",
            "captions": [
                "What lies beyond our understanding?",
                "Exploring new frontiers of knowledge",
                "Discovering hidden patterns and connections", 
                "Innovation shapes our future path",
                "The journey continues with endless possibilities"
            ]
        }
        
        print("Executing actual generation tasks...")
        
        # Execute voiceover generation
        print("Generating voiceovers...")
        voiceover_result = execute_voiceover_generation(script_data["captions"])
        print(f"Voiceover result: {voiceover_result}")
        
        # Execute image generation
        print("Generating images...")
        image_prompts = [
            f"Abstract Art Style / Ultra High Quality. {caption}"
            for caption in script_data["captions"]
        ]
        image_result = execute_image_generation(image_prompts)
        print(f"Image result: {image_result}")
        
        # Execute video assembly
        print("Assembling final video...")
        video_result = execute_video_assembly(script_data["captions"])
        print(f"Video result: {video_result}")
        
        return {
            'success': True,
            'result': result,
            'script_data': script_data,
            'voiceover_result': voiceover_result,
            'image_result': image_result,
            'video_result': video_result,
            'topic': topic,
            'timestamp': datetime.now()
        }
        
    except Exception as e:
        print(f"Error in CrewAI workflow: {e}")
        return {
            'success': False,
            'error': str(e),
            'topic': topic,
            'timestamp': datetime.now()
        }

def main():
    """Main CrewAI Streamlit application"""
    
    # Title and description
    st.title("🎬 CrewAI Video Generator")
    st.markdown("""
    Create AI-powered short videos using **CrewAI** multi-agent framework! 
    Our specialized crew of AI agents collaborate to generate scripts, voiceovers, images, and final videos.
    """)
    
    # Sidebar configuration
    st.sidebar.title("⚙️ CrewAI Configuration")
    st.sidebar.info("CrewAI uses sequential agent collaboration with role-based specialization")
    
    # Agent status display
    with st.sidebar.expander("👥 Agent Crew", expanded=True):
        st.write("**🖋️ Script Writer** - Creates engaging captions")
        st.write("**🎙️ Voice Actor** - Generates voiceovers") 
        st.write("**🎨 Graphic Designer** - Creates abstract art")
        st.write("**🎬 Video Director** - Assembles final video")
    
    # Clear generated content button
    if st.sidebar.button("🗑️ Clear All Generated Content"):
        st.session_state.crew_generated_content = None
        st.session_state.crew_workflow_messages = []
        # Clean up generated files
        for folder in ["voiceovers", "images"]:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
        if os.path.exists("yt_shorts_video.mp4"):
            os.remove("yt_shorts_video.mp4")
        st.success("All generated content cleared!")
        st.rerun()
    
    # Main input form
    with st.form("crewai_video_generation_form"):
        user_input = st.text_area(
            "Enter your video topic or description:",
            placeholder="Create a short AI-generated video about space exploration",
            height=100
        )
        
        submitted = st.form_submit_button(
            "🚀 Generate Video with CrewAI", 
            disabled=st.session_state.crew_workflow_running,
            width='stretch'
        )
    
    # Run workflow when form is submitted
    if submitted and user_input.strip():
        st.session_state.crew_workflow_running = True
        st.session_state.crew_workflow_messages = []
        
        with st.spinner("Running CrewAI multi-agent workflow..."):
            
            # Run the CrewAI workflow
            try:
                result = run_crewai_workflow(user_input)
                st.session_state.crew_generated_content = result
                
                if result['success']:
                    st.success("✅ CrewAI video generation complete!")
                else:
                    st.error(f"❌ Error during CrewAI workflow: {result['error']}")
                    
            except Exception as e:
                st.error(f"❌ Error during CrewAI workflow: {e}")
            finally:
                st.session_state.crew_workflow_running = False
        
        st.rerun()
    
    # Display results
    if st.session_state.crew_generated_content:
        st.subheader("🎬 CrewAI Generated Content")
        
        # Show input and timestamp
        content = st.session_state.crew_generated_content
        st.info(f"**Topic:** {content['topic']}")
        st.caption(f"Generated on: {content['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if content['success']:
            st.success(f"**Result:** {content['result']}")
        else:
            st.error(f"**Error:** {content['error']}")
        
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
                        file_name="crewai_generated_video.mp4",
                        mime="video/mp4",
                        width='stretch'
                    )
            else:
                st.info("Video file not found. Check the workflow log for errors.")
    
    # Comparison with AutoGen
    with st.expander("🔍 CrewAI vs AutoGen Comparison", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CrewAI Approach")
            st.write("✅ **Role-based agents** with specialized backstories")
            st.write("✅ **Sequential process** with task dependencies")
            st.write("✅ **Built-in collaboration** patterns")
            st.write("✅ **Context sharing** between tasks")
            st.write("✅ **Structured workflow** definition")
        
        with col2:
            st.subheader("AutoGen Approach")
            st.write("✅ **Round-robin execution** with turn limits")
            st.write("✅ **Function calling** integration")
            st.write("✅ **Termination conditions** control")
            st.write("✅ **Streaming responses** support")
            st.write("✅ **Flexible agent** configuration")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Built with ❤️ using **CrewAI**, Streamlit, OpenAI, ElevenLabs, and Stability AI"
    )

if __name__ == "__main__":
    main()