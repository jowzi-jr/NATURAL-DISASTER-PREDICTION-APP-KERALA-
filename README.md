
# DisasterAI — Integration Guide

A professional AI assistant for natural disaster safety, preparedness, and emergency response. Built with **Streamlit** and **Google Gemini 2.5 Flash**.

---

## What It Does

- Answers questions about earthquakes, floods, cyclones, tsunamis, wildfires, and landslides
- Provides step-by-step safety protocols and evacuation procedures
- Gives first-aid guidance and emergency kit checklists
- References NDMA, FEMA, Red Cross, and UN-OCHA standards
- Maintains full multi-turn conversation memory per session

---

## Project Structure

```
disaster ai/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── secrets.toml        # API key (never commit this)
└── .gitignore
```

---

## Requirements

- Python 3.10 or higher
- Google Gemini API key — get one free at https://aistudio.google.com/apikey

---

## Setup

### 1. Clone or copy the project files

Place `app.py` and `requirements.txt` into your project folder.

### 2. Install dependencies

```bash
pip install streamlit google-genai
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

### 3. Add your API key

Create a folder called `.streamlit` inside your project directory, then create `secrets.toml` inside it:

```
disaster ai/
└── .streamlit/
    └── secrets.toml
```

Add your Gemini API key to `secrets.toml`:

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

> **Important:** Never share or commit this file. Add `.streamlit/secrets.toml` to your `.gitignore`.

### 4. Run the app

```bash
streamlit run app.py
```

Or using the full Python path (Windows):

```bash
C:\Users\YourName\AppData\Local\Programs\Python\Python314\python.exe -m streamlit run app.py
```

The app opens at **http://localhost:8501** in your browser.

---

## Integrating Into an Existing Project

### Option 1 — Run as a standalone page (recommended)

If your main project is a website or web app, run DisasterAI as a separate Streamlit service and embed it via an `<iframe>`:

```html
<iframe
  src="http://localhost:8501"
  width="100%"
  height="700px"
  frameborder="0"
  style="border-radius: 12px;">
</iframe>
```

For production, deploy DisasterAI on a server (see Deployment section below) and replace `localhost:8501` with your live URL.

### Option 2 — Import the AI logic into your own Python app

Extract the core AI function from `app.py` and call it from your own code:

```python
from google import genai
from google.genai import types

client = genai.Client(api_key="your_gemini_api_key")

SYSTEM_PROMPT = """You are DisasterAI, a professional emergency response assistant
specialising in natural disasters — earthquakes, floods, cyclones, tsunamis,
wildfires, and landslides. Provide calm, accurate, actionable guidance."""

def create_chat():
    return client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0.4,
            max_output_tokens=1024,
        ),
    )

def ask_disasterai(chat, user_message: str) -> str:
    response = chat.send_message(user_message)
    return response.text


# Usage example
chat = create_chat()

reply = ask_disasterai(chat, "What should I do during a flash flood?")
print(reply)

# Continue the conversation (chat remembers history)
reply2 = ask_disasterai(chat, "What if I am in a car?")
print(reply2)
```

### Option 3 — Add as a route in a Flask or FastAPI app

```python
# Flask example
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

app = Flask(__name__)
client = genai.Client(api_key="your_key")
chat_sessions = {}

@app.route("/disasterai/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    message = data.get("message", "")

    if session_id not in chat_sessions:
        chat_sessions[session_id] = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction="You are DisasterAI...",
                temperature=0.4,
                max_output_tokens=1024,
            ),
        )

    response = chat_sessions[session_id].send_message(message)
    return jsonify({"reply": response.text})
```

---

## Environment Variables

If you are not using Streamlit's `secrets.toml`, you can load the API key from a `.env` file instead:

```bash
pip install python-dotenv
```

Create a `.env` file:

```
GEMINI_API_KEY=your_gemini_api_key_here
```

Load it in your code:

```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
```

---

## Deployment

### Streamlit Cloud (free)

1. Push your project to a GitHub repository
2. Make sure `.streamlit/secrets.toml` is in `.gitignore`
3. Go to https://streamlit.io/cloud and connect your repo
4. Add `GEMINI_API_KEY` under **App Settings → Secrets**
5. Deploy — you get a public URL instantly

### Railway / Render / Fly.io

Set `GEMINI_API_KEY` as an environment variable in your platform dashboard, then deploy with:

```bash
streamlit run app.py --server.port=8080 --server.address=0.0.0.0
```

---

## Customisation

| What to change | Where in `app.py` |
|---|---|
| AI personality and scope | `SYSTEM_PROMPT` variable |
| Gemini model | `model="gemini-2.5-flash"` in `get_chat()` |
| Quick topic buttons | `quick_prompts` dictionary in sidebar |
| UI colors | CSS variables in `st.markdown("""<style>...</style>""")` |
| Response length | `max_output_tokens=1024` in `get_chat()` |
| Creativity level | `temperature=0.4` in `get_chat()` (0 = strict, 1 = creative) |

---

## Troubleshooting

| Error | Fix |
|---|---|
| `429 RESOURCE_EXHAUSTED` | Free quota exceeded. Wait until midnight PT or create a new API key at aistudio.google.com |
| `404 NOT_FOUND` | Model name is wrong. Use `gemini-2.5-flash` |
| `No module named 'google'` | Run `pip install google-genai` |
| `ModuleNotFoundError: streamlit` | Run `pip install streamlit` |
| App opens but shows blank page | Check that your `secrets.toml` path is correct and the key is valid |

---

## Security Notes

- Never hardcode your API key directly in `app.py`
- Always use `secrets.toml` (Streamlit) or environment variables
- Add `.streamlit/secrets.toml` and `.env` to `.gitignore` before pushing to GitHub
- If your key is accidentally exposed, regenerate it immediately at https://aistudio.google.com/apikey

---

## Tech Stack

| Component | Technology |
|---|---|
| UI Framework | Streamlit |
| AI Model | Google Gemini 2.5 Flash |
| AI SDK | google-genai |
| Font | Inter (Google Fonts) |
| Language | Python 3.10+ |
