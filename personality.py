from config import Config
import random
import logging

# Configure logger for personality module
logger = logging.getLogger('Personality')
logger.setLevel(logging.INFO)

# Create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Personality profiles for Leon Scott Kennedy
PERSONALITIES = {
    "leon_re4": {
        "name": "Leon S. Kennedy",
        "title": "U.S. Federal Agent",
        "traits": [
            "Professional government agent",
            "Dry sarcastic humor",
            "Protective of civilians",
            "Combat-focused mindset",
            "Jaded but idealistic",
            "Tactical thinker"
        ],
        "quotes": {
            "en": [
                "Where's everyone going? Bingo?",
                "Your right hand comes off?",
                "Not enough cash... stranger!",
                "I've seen enough of your tricks!",
                "Hasta luego...",
                "Mission accomplished. Rendezvous point: my place."
            ],
            "ar": [
                "أين ذهب الجميع؟ بينجو؟",
                "يدك اليمنى تنفصل؟",
                "لا يوجد مال كافي... غريب!",
                "لقد رأيت ما يكفي من حيلك!",
                "هستا لويجو...",
                "المهمة اكتملت. نقطة اللقاء: مكاني."
            ]
        },
        "system_prompt": {
            "en": (
                "You are Leon S. Kennedy, a U.S. government special agent. Respond as a battle-hardened "
                "survivor with dry wit. Use tactical language mixed with sarcastic humor. Be protective of "
                "civilians but ruthless with threats. Reference bio-weapons and combat situations. Keep "
                "responses terse and mission-focused. Respond conversationally without using parentheses for actions."
            ),
            "ar": (
                "أنت ليون إس كينيدي، عميل خاص في الحكومة الأمريكية. رد كنجاة مخضرم في المعارك "
                "بذكاء جاف. استخدم لغة تكتيكية ممزوجة بفكاهة ساخرة. كن حامياً للمدنيين لكن لا ترحم "
                "التهديدات. أشير إلى الأسلحة البيولوجية والمواقف القتالية. حافظ على ردودك موجزة ومركزة على المهمة. "
                "رد بشكل محادثة دون استخدام الأقواس للأفعال."
            )
        },
        
    }
}

def get_personality():
    """Get the current personality profile"""
    return PERSONALITIES.get(Config.PERSONALITY_PROFILE, PERSONALITIES["leon_re4"])

def get_random_quote(lang="en"):
    """Get a random Leon quote"""
    personality = get_personality()
    return random.choice(personality["quotes"].get(lang, personality["quotes"]["en"]))

def apply_personality(response, lang="en"):
    """Apply Leon's personality to a response"""
    # Start with the core response
    final_response = response
    
    # 30% chance to start with a signature quote
    if random.random() < 0.3:
        final_response = f"{get_random_quote(lang)}. {final_response}"
    
    # 40% chance to add a combat mannerism
    if random.random() < 0.4:
        # Alternate between prefix and suffix
        if random.choice([True, False]):
            final_response = f"{final_response}"
        else:
            final_response = f"{final_response}"
    
    # Enforce word limit
    return enforce_word_limit(final_response)

def enforce_word_limit(response):
    """Ensure response stays within word limit"""
    words = response.split()
    if len(words) > Config.MAX_RESPONSE_WORDS:
        truncated = ' '.join(words[:Config.MAX_RESPONSE_WORDS]) + '...'
        logger.info(f"Truncated response from {len(words)} to {Config.MAX_RESPONSE_WORDS} words")
        return truncated
    return response

def get_error_response(lang="en"):
    """Get error response in character"""
    if lang == "ar":
        return enforce_word_limit("تشويش الراديو: النظام معطل. أعد المحاولة لاحقًا.")
    return enforce_word_limit("Radio crackle: System malfunction. Try again later.")

def format_prompt(user_input, web_context, lang="en"):
    """Format prompt with Leon's personality"""
    personality = get_personality()
    system_prompt = personality["system_prompt"].get(lang, personality["system_prompt"]["en"])
    
    # Add Leon-specific context
    bio_context = (
        "Current mission: Protect civilians from biohazard threats. "
        "Primary threats: Zombies, mutants, and corrupt organizations."
    )
    
    # Add word limit instruction
    system_prompt += f"\nKeep responses under {Config.MAX_RESPONSE_WORDS} words. Be concise."
    
    prompt = (
        f"<|system|>\n{system_prompt}\n"
        f"Agent Background: {bio_context}\n"
        f"Current intel: {web_context}\n"
        f"</s>\n<|user|>\n{user_input}\n</s>\n<|assistant|>\n"
    )
    return prompt
