# 🚀 AutoGen Multi-Agent Workflow Tutorial  

This repository contains a beginner-friendly **AutoGen 0.4** tutorial demonstrating how to create an AI-powered **multi-agent system** with **external API integrations** (text-to-speech, image generation) and Ollama integration.

🎥 **[Watch the YouTube video here](https://youtu.be/0PFexhfA4Pk)**  
📖 **[Read the blog post here](https://www.gettingstarted.ai/autogen-multi-agent-workflow-tutorial)**  

## 🛠️ Features  
- 🤖 **Multi-Agent System:** Script Writer, Voice Actor, Graphic Designer, and Director agents working together.  
- 🎙️ **Text-to-Speech:** Converts AI-generated text into voiceovers using **ElevenLabs API**.  
- 🖼️ **Image Generation:** Creates AI-generated visuals using **Stability AI**.  
- 🏡 **Local LLM Support:** Optional integration with **Ollama** for running AI models offline.  
- 🎮 **Interactive Console:** Type prompts and watch agents generate content dynamically.  

---

## 📂 Folder Structure  
```plaintext
autogen-multi-agent-workflow/
│── tools.py               # Utility functions (text-to-speech, image generation)
│── main.py                # Entry point for running the workflow
│── .env                   # API keys (not included, create your own)
│── .gitignore             # 
│── requirements.txt       # Dependencies for the project
│── README.md              # Documentation
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

### 6️⃣ Run the Workflow  
```bash
python main.py
```
You’ll be prompted to enter a task, and the agents will collaborate to generate a script, voiceover, and images dynamically.

---

## 🛠️ How It Works  
1️⃣ **Script Writer Agent** generates structured captions.  
2️⃣ **Voice Actor Agent** converts text to speech.  
3️⃣ **Graphic Designer Agent** creates images based on captions.  
4️⃣ **Director Agent** orchestrates the final output.  

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

## 🔧 Customization  
- **Use a different LLM:** Swap OpenAI for **Ollama** to run locally. (See blog for more)
- **Modify agent behaviors:** Edit the `system_message` for each agent.  
- **Integrate new APIs:** Extend `tools.py` for additional functionality.  

---

## 🤝 Contributing  
Pull requests are welcome! If you find issues or want to improve the workflow, feel free to open an issue.  

---

## 📜 License  
This project is licensed under the **MIT License**.  
You are free to **use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software**,  
as long as the original copyright notice and permission notice appear in all copies.  

For full details, see the [LICENSE](LICENSE) file.

---

## 🌟 Support & Feedback  
If you find this project helpful, **⭐️ star the repo** and share your thoughts!  