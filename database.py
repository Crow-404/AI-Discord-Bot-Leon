import sqlite3
import logging
import json
from config import Config

logger = logging.getLogger('Database')

def init_db():
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        
        # Messages table
        c.execute('''CREATE TABLE IF NOT EXISTS messages
                     (id TEXT PRIMARY KEY, 
                      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                      user_id TEXT, 
                      content TEXT, 
                      language TEXT,
                      response TEXT)''')
        
        # Personality context table
        c.execute('''CREATE TABLE IF NOT EXISTS personality_context
                     (user_id TEXT PRIMARY KEY,
                      last_context TEXT,
                      personality_traits TEXT)''')
        
        conn.commit()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        conn.close()

def save_message(message, response=None):
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        c.execute('''INSERT OR IGNORE INTO messages 
                     (id, user_id, content, language, response)
                     VALUES (?, ?, ?, ?, ?)''',
                 (message['id'], 
                  message['author']['id'],
                  message['content'],
                  detect_language(message['content']),
                  response))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        return False
    finally:
        conn.close()

def detect_language(text):
    arabic_chars = set("ابتثجحخدذرزسشصضطظعغفقكلمنهويةىءأإئؤة")
    return "ar" if any(char in arabic_chars for char in text) else "en"

def get_conversation_history(user_id, limit=5):
    """Get recent conversation history for a user"""
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        c.execute('''SELECT content, response 
                     FROM messages 
                     WHERE user_id = ? 
                     ORDER BY timestamp DESC 
                     LIMIT ?''', (user_id, limit))
        rows = c.fetchall()
        return [{"user": row[0], "bot": row[1]} for row in rows] if rows else []
    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        return []
    finally:
        conn.close()

def save_personality_context(user_id, context, traits):
    """Save personality context for a user"""
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO personality_context 
                     (user_id, last_context, personality_traits) 
                     VALUES (?, ?, ?)''',
                 (user_id, json.dumps(context), json.dumps(traits)))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error saving context: {e}")
        return False
    finally:
        conn.close()

def get_personality_context(user_id):
    """Get saved personality context for a user"""
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        c.execute('''SELECT last_context, personality_traits 
                     FROM personality_context 
                     WHERE user_id = ?''', (user_id,))
        row = c.fetchone()
        if row:
            return {
                "last_context": json.loads(row[0]),
                "personality_traits": json.loads(row[1])
            }
        return None
    except Exception as e:
        logger.error(f"Error loading context: {e}")
        return None
    finally:
        conn.close()

def get_training_data():
    """
    Fetch all messages with responses and associated personality traits for training.
    Returns list of dicts: {'prompt', 'response', 'personality_traits'}
    """
    try:
        conn = sqlite3.connect(Config.DATABASE_FILE)
        c = conn.cursor()
        # Join messages with personality_context to get traits for each message's user
        c.execute('''
            SELECT m.content, m.response, pc.personality_traits
            FROM messages m
            LEFT JOIN personality_context pc ON m.user_id = pc.user_id
            WHERE m.response IS NOT NULL
        ''')
        rows = c.fetchall()
        conn.close()

        return [
            {
                "prompt": row[0],
                "response": row[1],
                "personality_traits": json.loads(row[2]) if row[2] else {}
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error fetching training data: {e}")
        return []