# 🚀 Multi-Agent Video Generation Framework  

This repository demonstrates two different approaches to creating AI-powered **multi-agent systems** for automated video generation with **external API integrations** (text-to-speech, image generation). Compare **AutoGen 0.4** and **CrewAI** frameworks side-by-side!

🎥 **[Watch the YouTube video here](https://youtu.be/0PFexhfA4Pk)**  
📖 **[Read the blog post here](https://www.gettingstarted.ai/autogen-multi-agent-workflow-tutorial)**  

## 🛠️ Features  
- 🤖 **Dual Framework Implementation:** Compare AutoGen vs CrewAI approaches  
- 👥 **Multi-Agent Collaboration:** Script Writer, Voice Actor, Graphic Designer, and Director agents  
- 🎙️ **Text-to-Speech:** Converts AI-generated text into voiceovers using **ElevenLabs API**  
- 🖼️ **Image Generation:** Creates AI-generated visuals using **Stability AI**  
- 🎬 **Video Assembly:** Automated video creation with Ken Burns effects and audio mixing  
- 🏡 **Local LLM Support:** Optional integration with **Ollama** for running AI models offline  
- 🌐 **Streamlit Web Interface:** Interactive web apps for both frameworks  
- 📱 **YouTube Shorts Format:** Optimized 9:16 aspect ratio vertical videos  

---

## 📂 Folder Structure  
```plaintext
autogen-multi-agent-workflow/
├── main.py                 # AutoGen implementation with Streamlit UI
├── crewai_app.py          # CrewAI implementation with Streamlit UI  
├── tools.py               # Video generation utilities (FFmpeg, Ken Burns effects)
├── requirements.txt       # Dependencies for both frameworks
├── CLAUDE.md              # Development documentation
├── .env                   # API keys (create your own)
├── .gitignore            # Git ignore rules
├── voiceovers/           # Generated audio files (auto-created)
├── images/               # Generated image files (auto-created)
└── README.md             # This documentation
```

---

## 🚀 Quick Start  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/gswithjeff/autogen-multi-agent-workflow.git
cd autogen-multi-agent-workflow
```

### 2️⃣ Create & Activate a Virtual Environment  
#### **For macOS/Linux:**  
```bash
python -m venv venv
source venv/bin/activate
```
#### **For Windows:**  
```bash
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ Install Dependencies  
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up API Keys  
Create a `.env` file and add your API keys:  
```plaintext
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
STABILITY_API_KEY=your-stability-ai-api-key
```

### 5️⃣ Create Required Accounts  
Before running the workflow, you'll need to create accounts for the following services:  

- **ElevenLabs (Text to Speech)**: [Sign up here](https://try.elevenlabs.io/)
- **Stability AI (Image Generation)**: [Sign up here](https://platform.stability.ai/)  

These accounts provide API access for text-to-speech and image generation, which are required for the agents to function.

### 6️⃣ Run the Applications  

#### **AutoGen Streamlit App:**
```bash
streamlit run main.py
```

#### **CrewAI Streamlit App:**  
```bash  
streamlit run crewai_app.py
```

#### **AutoGen Console Mode:**
```bash
python main.py
```

Open your browser and navigate to the provided local URL (typically http://localhost:8501) to access the web interface.

---

## 🛠️ How It Works  

### 🔄 **AutoGen Workflow (Round-Robin Execution)**
1️⃣ **Script Writer Agent** generates structured JSON with 5 captions  
2️⃣ **Voice Actor Agent** converts captions to MP3 voiceovers via ElevenLabs  
3️⃣ **Graphic Designer Agent** creates abstract art images via Stability AI  
4️⃣ **Director Agent** assembles final MP4 video with FFmpeg  

### ⚙️ **CrewAI Workflow (Sequential Task Execution)**  
1️⃣ **Script Writer Agent** creates compelling video narrative structure  
2️⃣ **Voice Actor Agent** coordinates voiceover production process  
3️⃣ **Graphic Designer Agent** designs visual specifications and prompts  
4️⃣ **Video Director Agent** oversees final assembly coordination  

### 🎬 **Video Generation Pipeline**
- **Ken Burns Effect**: Slow zoom/pan on images for cinematic feel
- **Text Overlays**: Captions with custom styling and positioning  
- **Audio Mixing**: Voiceovers timed to image segments (background music optional)
- **Output Format**: 1080x1920 (9:16) MP4 optimized for social media  

---

## 🎯 Example Usage  

### **User Prompt:**  
```plaintext
Create a short AI-generated video about space exploration.
```

### **Generated JSON Response:**  
```json
{
    "topic": "Space Exploration",
    "takeaway": "The future of space travel is closer than we think!",
    "captions": [
        "What lies beyond our galaxy?",
        "Humans are reaching new frontiers.",
        "AI is shaping space exploration.",
        "New planets are waiting to be discovered.",
        "The universe is limitless!"
    ]
}
```

✅ **Voiceovers are generated**  
✅ **Images are created**  
✅ **Final video assembly is handled**  

---

## 🔧 Framework Comparison

| Feature | AutoGen | CrewAI |
|---------|---------|---------|
| **Execution Pattern** | Round-robin turns | Sequential tasks |
| **Agent Communication** | Function calls + termination | Context sharing |
| **Configuration** | System messages | Roles + backstories |
| **Process Control** | Max turns + conditions | Task dependencies |
| **Tool Integration** | Direct function calling | Coordination-based |
| **Workflow Flexibility** | High (dynamic turns) | Structured (predefined) |
| **Learning Curve** | Moderate | Easy |

## 🔧 Customization  
- **Use a different LLM:** Swap OpenAI for **Ollama** to run locally
- **Modify agent behaviors:** Edit system messages (AutoGen) or backstories (CrewAI)  
- **Extend functionality:** Add new tools in `tools.py` or create custom agent functions
- **Adjust video settings:** Modify duration, resolution, effects in video generation pipeline
- **Background Music:** Add `music/cosmos.mp3` file for background audio (optional)  

---

## 🛠️ Technical Requirements

### **System Dependencies**
- **Python 3.8+** (Python 3.13 recommended)
- **FFmpeg** for video processing and audio mixing
- **Virtual environment** support

### **API Requirements**  
- **OpenAI API Key** for LLM agents (GPT-4 recommended)
- **ElevenLabs API Key** for text-to-speech conversion
- **Stability AI API Key** for image generation

### **Hardware Recommendations**
- **4GB+ RAM** for video processing
- **2GB+ storage** for generated content
- **Internet connection** for API services

## 🧪 Testing & Development

### **Run Tests**
```bash
# Test AutoGen implementation
python -c "from main import generate_voiceovers, generate_images; print('✅ AutoGen imports working')"

# Test CrewAI implementation  
python -c "from crewai import Agent, Task, Crew; print('✅ CrewAI imports working')"

# Test video generation
python -c "from tools import generate_video; print('✅ Video tools working')"
```

### **Debug Mode**
Set environment variable for verbose logging:
```bash
export AUTOGEN_DEBUG=1
streamlit run main.py
```

## 🤝 Contributing  
Pull requests are welcome! If you find issues or want to improve the workflow, feel free to open an issue.

**Areas for contribution:**
- Additional multi-agent frameworks (LangGraph, etc.)
- Enhanced video effects and transitions  
- Performance optimizations
- Additional API integrations
- Mobile-responsive UI improvements  

---

## 📜 License  
This project is licensed under the **MIT License**.  
You are free to **use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software**,  
as long as the original copyright notice and permission notice appear in all copies.  

For full details, see the [LICENSE](LICENSE) file.

---

## 🌟 Support & Feedback  
If you find this project helpful, **⭐️ star the repo** and share your thoughts!

### **Useful Resources**
- **AutoGen Documentation**: [https://microsoft.github.io/autogen/](https://microsoft.github.io/autogen/)
- **CrewAI Documentation**: [https://docs.crewai.com/](https://docs.crewai.com/)
- **ElevenLabs API Docs**: [https://elevenlabs.io/docs](https://elevenlabs.io/docs)
- **Stability AI API Docs**: [https://platform.stability.ai/docs](https://platform.stability.ai/docs)
- **FFmpeg Documentation**: [https://ffmpeg.org/documentation.html](https://ffmpeg.org/documentation.html)

### **Community**
- **Issues**: Report bugs or request features
- **Discussions**: Share your generated videos and improvements
- **Pull Requests**: Contribute code improvements

---

**🎬 Happy video generating with AI agents! 🤖✨**  