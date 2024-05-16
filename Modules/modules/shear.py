SHEAR_WORDS = set()

async def add_shear_word(word: str):
    """Add a shear word to the list asynchronously"""
    SHEAR_WORDS.add(word.lower())

async def is_shear(message: str) -> bool:
    """Check if a given message contains any shear words asynchronously"""
    words = message.split(' ')
    return any(word.lower() in SHEAR_WORDS for word in words)

