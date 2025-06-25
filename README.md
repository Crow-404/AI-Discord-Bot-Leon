# AI-Discord-Bot-Leon

A personality-driven, AI-powered Discord user bot based on Leon S. Kennedy from Resident Evil.  
Built with a local LLM (Ollama), this bot responds to mentions in real-time with witty, tactical replies — in Arabic or English — while simulating human-like typing behavior.

---

## Features

- Responds to mentions in a Discord channel.
- Roleplay-style personality: Leon S. Kennedy (RE4).
- Powered by local LLM (via Ollama) — no API keys required.
- Dual-language support: Arabic and English.
- SQLite-based database for storing messages and context.
- Dynamic persona system: customize traits, quotes, and style.
- Built-in logging, typing animation, and cooldown control.

---

## Tech Stack

| Component       | Tech/Library         |
|-----------------|----------------------|
| Language        | Python               |
| Discord API     | requests (user token method) |
| LLM Backend     | Ollama               |
| Database        | SQLite               |
| Personality     | Custom profile file (`personality.py`) |
| Logging         | Python `logging`     |


---

## How to Run

### 1. Clone the Repo and Install Requirements :

```bash
git clone https://github.com/Crow-404/discord-leon-bot.git
cd discord-leon-bot
pip install -r requirements.txt
```
--- 
3. Configure Settings
Open config.py and set your:

USER_TOKEN (user bot account token)

CHANNEL_ID and USER_ID

Optional: change MODEL_NAME, PERSONALITY_PROFILE, etc.

4. Start Ollama
Download and run Ollama:
[https://ollama.com/download](https://ollama.com/download)

Then pull the model:

```bash
ollama pull llama3
```
5. Run the Bot
```bash
python main.py
```
## Customizing Personality
Edit personality.py:

Change traits, quotes (both English and Arabic)

Modify the system prompt to control the tone of replies

Supports future profiles like "mysterious", "friendly", etc.

## Example Interaction
User: @Leon help me with this mess!
Bot (Leon): Where's everyone going? Bingo? Stay sharp. This place reeks of trouble.

## Database
All messages and bot responses are stored in chat_history.db

Personality context is also saved per user

Useful for training, analytics, or fine-tuning

## Author
Built by [Crow-404] — Inspired by Resident Evil and AI agent roleplay.
