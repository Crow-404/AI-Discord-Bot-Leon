class Config: 
    # Discord user account settings 
    USER_TOKEN = "user_token" 
    USER_ID = "user_id" 
    CHANNEL_ID = "channel_id" 
     
    # Response settings 
    COOLDOWN_SECONDS = 0.05  # Minimum time between replies 
    TYPING_ANIMATION_DELAY = 0.05  # Seconds per character for typing effect 
    MAX_RESPONSE_WORDS = 25  # Maximum words in response 
     
    # LLM settings 
    MODEL_NAME = "llama3" 
    TEMPERATURE = 0.6 
    MAX_TOKENS = 240 
