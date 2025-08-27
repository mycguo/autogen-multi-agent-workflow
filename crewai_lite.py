import streamlit as st
import os
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Use OpenAI directly instead of CrewAI for Streamlit Cloud compatibility
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Import utility functions
from main import generate_voiceovers, generate_images
from tools import generate_video

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="CrewAI-Style Video Generator",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'crew_lite_workflow_running' not in st.session_state:
    st.session_state.crew_lite_workflow_running = False
if 'crew_lite_generated_content' not in st.session_state:
    st.session_state.crew_lite_generated_content = None

# Initialize API clients
try:
    if 'OPENAI_API_KEY' in st.secrets:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
    else:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
    # Initialize language model
    llm = ChatOpenAI(
        model="gpt-4o",
        api_key=openai_api_key,
        temperature=0.7
    )
    
except Exception as e:
    st.error(f"Error initializing API clients: {e}")
    st.stop()

# Agent personas using direct LLM calls instead of CrewAI
class CrewAIStyleAgent:
    def __init__(self, role: str, goal: str, backstory: str, llm):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.llm = llm
    
    def execute_task(self, task_description: str, context: str = "") -> str:
        """Execute a task using the agent's persona"""
        system_prompt = f"""
        You are a {self.role}.
        
        Your goal: {self.goal}
        
        Your backstory: {self.backstory}
        
        Context from previous tasks: {context}
        
        Execute the following task according to your role and expertise.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=task_description)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

def run_crewai_style_workflow(topic: str) -> Dict[str, Any]:
    """Run a CrewAI-style workflow without ChromaDB dependencies"""
    
    try:
        print(f"Starting CrewAI-style workflow for topic: {topic}")
        
        # Create agents
        script_writer = CrewAIStyleAgent(
            role="Script Writer",
            goal="Create engaging video scripts with exactly 5 short captions",
            backstory="You are a creative script writer specialized in creating compelling short-form video content.",
            llm=llm
        )
        
        voice_actor = CrewAIStyleAgent(
            role="Voice Actor", 
            goal="Coordinate voiceover production",
            backstory="You are a professional voice actor who coordinates text-to-speech production.",
            llm=llm
        )
        
        graphic_designer = CrewAIStyleAgent(
            role="Graphic Designer",
            goal="Design visual specifications for abstract art",
            backstory="You are a digital artist specializing in abstract art and conceptual imagery.",
            llm=llm
        )
        
        video_director = CrewAIStyleAgent(
            role="Video Director",
            goal="Coordinate final video assembly",
            backstory="You are an experienced video director who coordinates short-form content assembly.",
            llm=llm
        )
        
        # Task 1: Script Writing
        st.info("🖋️ Script Writer is creating the video script...")
        script_task = f"""Create a script for a short video about: {topic}

        Requirements:
        1. Generate exactly 5 captions, each no more than 8 words
        2. Start with a compelling question or statement
        3. Create a natural narrative flow
        4. Include topic and takeaway
        
        Output in JSON format:
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
        }}"""
        
        script_result = script_writer.execute_task(script_task)
        
        # Parse the JSON response
        try:
            # Extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', script_result, re.DOTALL)
            if json_match:
                script_data = json.loads(json_match.group())
            else:
                # Fallback if JSON parsing fails
                script_data = {
                    "topic": topic,
                    "takeaway": f"Insights about {topic}",
                    "captions": [
                        "What lies beyond our understanding?",
                        "Exploring new frontiers of knowledge", 
                        "Discovering hidden patterns and connections",
                        "Innovation shapes our future path",
                        "The journey continues endlessly"
                    ]
                }
        except:
            # Fallback data
            script_data = {
                "topic": topic,
                "takeaway": f"Key insights about {topic}",
                "captions": [
                    "What mysteries await discovery?",
                    "Pushing boundaries of possibility",
                    "Uncovering secrets of the universe", 
                    "Technology shapes our destiny",
                    "The future is limitless"
                ]
            }
        
        st.success(f"✅ Generated script: {script_data['topic']}")
        
        # Task 2: Voice Acting Coordination
        st.info("🎙️ Voice Actor is coordinating voiceover production...")
        voice_task = f"""Coordinate voiceover production for these captions: {script_data['captions']}
        
        Confirm that voiceovers should be generated for all captions and return 'VOICEOVERS_READY'"""
        
        voice_result = voice_actor.execute_task(voice_task, str(script_data))
        st.success("✅ Voice Actor ready for production")
        
        # Task 3: Graphic Design
        st.info("🎨 Graphic Designer is creating image specifications...")
        design_task = f"""Design image specifications for these captions: {script_data['captions']}
        
        Create optimized prompts maintaining 'Abstract Art Style / Ultra High Quality' and return 'IMAGES_READY'"""
        
        design_result = graphic_designer.execute_task(design_task, str(script_data))
        st.success("✅ Graphic Designer completed specifications")
        
        # Task 4: Video Direction
        st.info("🎬 Video Director is coordinating final assembly...")
        director_task = f"""Direct the final video assembly for: {script_data['captions']}
        
        Coordinate all elements and return 'VIDEO_ASSEMBLY_COMPLETE'"""
        
        director_result = video_director.execute_task(director_task, 
                                                    f"Script: {script_data}, Voice: {voice_result}, Design: {design_result}")
        st.success("✅ Video Director completed coordination")
        
        # Execute actual generation
        st.info("🔧 Executing actual content generation...")
        
        # Generate voiceovers
        voiceover_result = generate_voiceovers(script_data["captions"])
        
        # Generate images
        image_prompts = [
            f"Abstract Art Style / Ultra High Quality. {caption}"
            for caption in script_data["captions"]
        ]
        generate_images(image_prompts)
        
        # Generate video
        generate_video(script_data["captions"])
        
        return {
            'success': True,
            'script_data': script_data,
            'agent_results': {
                'script': script_result,
                'voice': voice_result,
                'design': design_result,
                'director': director_result
            },
            'topic': topic,
            'timestamp': datetime.now()
        }
        
    except Exception as e:
        print(f"Error in CrewAI-style workflow: {e}")
        return {
            'success': False,
            'error': str(e),
            'topic': topic,
            'timestamp': datetime.now()
        }

def main():
    """Main CrewAI-Style Streamlit application"""
    
    # Title and description
    st.title("🎬 CrewAI-Style Video Generator")
    st.markdown("""
    Create AI-powered short videos using **CrewAI-inspired** multi-agent collaboration! 
    This version is optimized for Streamlit Cloud deployment without ChromaDB dependencies.
    """)
    
    # Info about compatibility
    st.info("📋 **Streamlit Cloud Optimized**: This version avoids ChromaDB dependencies for better cloud compatibility.")
    
    # Sidebar configuration
    st.sidebar.title("⚙️ Configuration")
    st.sidebar.info("CrewAI-style agents using direct LLM coordination")
    
    # Agent status display
    with st.sidebar.expander("👥 Agent Crew", expanded=True):
        st.write("**🖋️ Script Writer** - Creates engaging captions")
        st.write("**🎙️ Voice Actor** - Coordinates voiceovers") 
        st.write("**🎨 Graphic Designer** - Designs visual specs")
        st.write("**🎬 Video Director** - Assembles final video")
    
    # Clear content button
    if st.sidebar.button("🗑️ Clear Generated Content"):
        st.session_state.crew_lite_generated_content = None
        # Clean up files
        for folder in ["voiceovers", "images"]:
            if os.path.exists(folder):
                import shutil
                shutil.rmtree(folder)
        if os.path.exists("yt_shorts_video.mp4"):
            os.remove("yt_shorts_video.mp4")
        st.success("All content cleared!")
        st.rerun()
    
    # Main input form
    with st.form("crewai_lite_form"):
        user_input = st.text_area(
            "Enter your video topic:",
            placeholder="Create a short video about artificial intelligence and the future",
            height=100
        )
        
        submitted = st.form_submit_button(
            "🚀 Generate Video (CrewAI-Style)", 
            disabled=st.session_state.crew_lite_workflow_running,
            width='stretch'
        )
    
    # Run workflow
    if submitted and user_input.strip():
        st.session_state.crew_lite_workflow_running = True
        
        with st.spinner("Running CrewAI-style multi-agent workflow..."):
            result = run_crewai_style_workflow(user_input)
            st.session_state.crew_lite_generated_content = result
            
            if result['success']:
                st.success("✅ CrewAI-style video generation complete!")
            else:
                st.error(f"❌ Error: {result['error']}")
                
        st.session_state.crew_lite_workflow_running = False
        st.rerun()
    
    # Display results
    if st.session_state.crew_lite_generated_content:
        content = st.session_state.crew_lite_generated_content
        
        st.subheader("🎬 Generated Content")
        st.info(f"**Topic:** {content['topic']}")
        st.caption(f"Generated: {content['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if content['success']:
            # Show script data
            if 'script_data' in content:
                with st.expander("📝 Generated Script", expanded=True):
                    script = content['script_data']
                    st.write(f"**Topic:** {script['topic']}")
                    st.write(f"**Takeaway:** {script['takeaway']}")
                    st.write("**Captions:**")
                    for i, caption in enumerate(script['captions'], 1):
                        st.write(f"{i}. {caption}")
        
        # Display generated files
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🎵 Voiceovers")
            if os.path.exists("voiceovers"):
                audio_files = [f for f in os.listdir("voiceovers") if f.endswith(".mp3")]
                for audio_file in sorted(audio_files):
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
                
                # Download button
                with open("yt_shorts_video.mp4", "rb") as video_file:
                    st.download_button(
                        label="📥 Download Video",
                        data=video_file.read(),
                        file_name="crewai_style_video.mp4",
                        mime="video/mp4",
                        width='stretch'
                    )
            else:
                st.info("Video not found. Check logs for errors.")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using CrewAI-style coordination, Streamlit, OpenAI, ElevenLabs, and Stability AI")

if __name__ == "__main__":
    main()