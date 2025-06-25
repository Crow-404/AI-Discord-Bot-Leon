import logging
import personality
from config import Config
import re

logger = logging.getLogger('LLMHandler')

class LLMHandler:
    def __init__(self):
        try:
            # Initialize Ollama client properly
            import ollama
            self.ollama = ollama
            logger.info(f"LLM initialized with model: {Config.MODEL_NAME}")
            
            # Test connection
            response = self.ollama.generate(model=Config.MODEL_NAME, prompt="Test connection")
            logger.info("Ollama connection successful")
        except ImportError:
            logger.critical("Ollama module not installed. Please install with 'pip install ollama'")
            self.ollama = None
        except Exception as e:
            logger.critical(f"LLM initialization failed: {e}")
            self.ollama = None

    def generate_response(self, user_input: str, lang: str = "en") -> str:
        """Generate response with personality and word limit"""
        if self.ollama is None:
            return personality.get_error_response(lang)
            
        try:
            # Get web context
            
            
            # Format prompt with personality
            system_prompt = personality.get_personality()["system_prompt"].get(
                lang, 
                personality.get_personality()["system_prompt"]["en"]
            )
            
            # Add word limit instruction to prompt
            system_prompt += f"\nKeep response under {Config.MAX_RESPONSE_WORDS} words. Be concise."
            
            prompt = (
                f"<|system|>\n{system_prompt}\n"
                f"</s>\n<|user|>\n{user_input}\n</s>\n<|assistant|>\n"
            )
            
            # Generate actual response
            response = self.ollama.generate(
                model=Config.MODEL_NAME,
                prompt=prompt,
                options={
                    "temperature": Config.TEMPERATURE,
                    "num_predict": Config.MAX_TOKENS
                }
            )['response'].strip()
            
            # Apply personality styling
            styled_response = personality.apply_personality(response, lang)
            
            # Remove parenthetical actions like "(Checking ammo)"
            cleaned_response = self.remove_parenthetical_actions(styled_response)
            
            # Enforce word limit
            final_response = self.enforce_word_limit(cleaned_response)
            
            logger.info(f"Generated response: {final_response[:100]}...")
            return final_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return personality.get_error_response(lang)

    def remove_parenthetical_actions(self, text):
        """Remove text in parentheses that appear at the beginning of the response"""
        # Pattern to match parentheses at start of string
        return re.sub(r'^\s*\([^)]*\)\s*', '', text)

    def enforce_word_limit(self, text):
        """Truncate response to MAX_RESPONSE_WORDS"""
        words = text.split()
        if len(words) > Config.MAX_RESPONSE_WORDS:
            return ' '.join(words[:Config.MAX_RESPONSE_WORDS]) + '...'
        return text
