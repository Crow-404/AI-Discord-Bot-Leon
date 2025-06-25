import logging
from discord_app import main_loop
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    print("""
    ██████╗ ██╗███████╗ ██████╗  ██████╗ ██████╗ 
    ██╔══██╗██║██╔════╝██╔════╝ ██╔═══██╗██╔══██╗
    ██║  ██║██║███████╗██║  ███╗██║   ██║██████╔╝
    ██║  ██║██║╚════██║██║   ██║██║   ██║██╔══██╗
    ██████╔╝██║███████║╚██████╔╝╚██████╔╝██║  ██║
    ╚═════╝ ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝
    AI-BOT
    """)
    print(f"Personality: {Config.PERSONALITY_PROFILE}")
    print(f"Cooldown: {Config.COOLDOWN_SECONDS}s | Model: {Config.MODEL_NAME}")
    main_loop()
