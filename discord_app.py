import requests
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import TypedDict

from llm_handler import LLMHandler
from database import init_db, save_message, detect_language
from config import Config

logger = logging.getLogger('DiscordApp')
llm = LLMHandler()

# Global state for cooldown management
last_reply_time = None
typing_animations = {}

# Define safe state structure
class BotState(TypedDict):
    last_processed_id: str
    last_run: str

def load_state() -> BotState:
    try:
        with open(Config.STATE_FILE, 'r') as f:
            raw_state = json.load(f)
            return {
                "last_processed_id": str(raw_state.get("last_processed_id", "")),
                "last_run": str(raw_state.get("last_run", ""))
            }
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            "last_processed_id": "",
            "last_run": ""
        }

def save_state(state: BotState) -> None:
    try:
        with open(Config.STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving state: {e}")

def fetch_messages(after=None):
    try:
        params = {"limit": 10}
        if after:
            params["after"] = after

        headers = {
            "Authorization": Config.USER_TOKEN,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"https://discord.com/api/v9/channels/{Config.CHANNEL_ID}/messages",
            headers=headers,
            params=params,
            timeout=15
        )

        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            logger.warning(f"Rate limited. Retrying after {retry_after}s")
            time.sleep(retry_after)
            return fetch_messages(after)

        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return []

def send_typing_indicator():
    try:
        headers = {
            "Authorization": Config.USER_TOKEN,
            "User-Agent": Config.USER_AGENT
        }

        requests.post(
            f"https://discord.com/api/v9/channels/{Config.CHANNEL_ID}/typing",
            headers=headers,
            timeout=5
        )
    except Exception as e:
        logger.warning(f"Typing indicator failed: {e}")

def simulate_typing(response, message_id):
    global typing_animations
    session_id = f"{Config.CHANNEL_ID}-{message_id}"
    typing_animations[session_id] = True

    typing_time = len(response) * Config.TYPING_ANIMATION_DELAY
    start_time = time.time()

    while typing_animations.get(session_id) and (time.time() - start_time) < typing_time:
        send_typing_indicator()
        time.sleep(2)

    typing_animations.pop(session_id, None)

def send_reply(original_message, reply_text):
    """Send reply mentioning the original author"""
    # Get the author ID from the original message
    author_id = original_message['author']['id']
    message_id = original_message['id']
    
    threading.Thread(
        target=simulate_typing,
        args=(reply_text, message_id),
        daemon=True
    ).start()

    min_wait = min(len(reply_text) * Config.TYPING_ANIMATION_DELAY, Config.COOLDOWN_SECONDS)
    time.sleep(min_wait)

    try:
        headers = {
            "Authorization": Config.USER_TOKEN,
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/json"
        }

        # Mention the original author instead of the bot
        data = {
            "content": f"<@{author_id}> {reply_text}",
            "message_reference": {
                "channel_id": Config.CHANNEL_ID,
                "message_id": message_id
            }
        }

        response = requests.post(
            f"https://discord.com/api/v9/channels/{Config.CHANNEL_ID}/messages",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 429:
            retry_after = response.json().get('retry_after', 5)
            logger.warning(f"Rate limited on reply. Retrying after {retry_after}s")
            time.sleep(retry_after)
            return send_reply(original_message, reply_text)

        response.raise_for_status()
        logger.info(f"Replied to {message_id}")
        return True
    except Exception as e:
        logger.error(f"Reply failed: {e}")
        return False

def can_reply():
    global last_reply_time
    if last_reply_time is None:
        return True
    return (datetime.now() - last_reply_time) >= timedelta(seconds=Config.COOLDOWN_SECONDS)

def process_messages(messages, last_processed_id):
    global last_reply_time
    new_messages = 0

    for msg in reversed(messages):
        if last_processed_id and msg['id'] == last_processed_id:
            continue

        if any(str(mention.get("id")) == Config.USER_ID for mention in msg.get("mentions", [])):
            try:
                if not can_reply():
                    logger.info("Skipping reply due to cooldown")
                    continue

                lang = detect_language(msg['content'])
                response = llm.generate_response(msg['content'], lang)

                if response and send_reply(msg, response):  # Pass the entire message object
                    last_reply_time = datetime.now()
                    new_messages += 1
                    save_message(msg, response)

            except Exception as e:
                logger.error(f"Processing error: {e}")

        last_processed_id = msg['id']

    return new_messages, last_processed_id

def main_loop():
    logger.info("Starting Discord User App")
    init_db()
    state: BotState = load_state()
    last_processed_id = state.get("last_processed_id") or None

    while True:
        try:
            start_time = time.time()
            messages = fetch_messages(last_processed_id)

            if messages:
                new_count, last_processed_id = process_messages(messages, last_processed_id)
                logger.info(f"Processed {new_count} new mentions")

                state["last_processed_id"] = str(last_processed_id) if last_processed_id else ""
                state["last_run"] = datetime.now().isoformat()
                save_state(state)

            elapsed = time.time() - start_time
            sleep_time = max(1, Config.POLL_INTERVAL - elapsed)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("App stopped by user")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(60)
