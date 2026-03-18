# NOVA — Neural Orchestrated Voice Assistant
### Deployed on Streamlit Cloud · Powered by Groq + LLaMA3

> A fully functional AI voice assistant you can use from any browser, anywhere in the world.

---

## Live Demo
[nova-assistant.streamlit.app](https://nova-assistant.streamlit.app)

---

## Features

| Skill | How it works |
|---|---|
| Web search | Opens Google in new tab |
| YouTube search | Opens YouTube results |
| Weather | Live data from wttr.in |
| Time & Date | Real-time |
| Calculator | Evaluates math expressions |
| Dictionary | Free Dictionary API |
| Jokes | Official Joke API |
| News | Google News |
| Translate | Google Translate |
| Unit conversion | Built-in (km, miles, °C, °F, kg, lbs) |
| Currency | Open Exchange Rates API |
| Motivational quotes | ZenQuotes API |
| Random facts | Useless Facts API |
| Open websites | Opens any URL |
| Reminders | Browser-based timer |
| Voice input | Web Speech API (Chrome/Edge) |

---

## Run Locally

```bash
git clone https://github.com/yourusername/nova-assistant
cd nova-assistant
pip install -r requirements.txt
streamlit run app.py
```

Get a free Groq API key at https://console.groq.com

---

## Deploy to Streamlit Cloud (free)

1. Push this folder to a GitHub repo
2. Go to https://share.streamlit.io
3. Click New app → select your repo → set main file to `app.py`
4. Go to Settings → Secrets → add:
   ```
   GROQ_API_KEY = "gsk_your_key_here"
   ```
5. Click Deploy — live in 2 minutes

---

## Tech Stack

- **Frontend**: Streamlit + custom CSS
- **AI**: Groq Cloud API (LLaMA3-70B)
- **Voice**: Web Speech API (browser-native)
- **APIs**: wttr.in, Dictionary API, Joke API, ZenQuotes, Open Exchange Rates
- **Deployment**: Streamlit Community Cloud (free)

---

## Architecture

```
User speaks/types
      ↓
Browser (Web Speech API → text)
      ↓
Streamlit app (Python)
      ↓
Groq API (LLaMA3-70B) → intent parsing
      ↓
Action executor → result
      ↓
Response displayed + spoken (browser TTS)
```

---

*Built for placement portfolio — demonstrates end-to-end AI system with speech, LLM, and real-world actions*
