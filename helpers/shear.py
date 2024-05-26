import aiofiles

SHEAR_WORDS_FILE = 'shear_words.txt'

async def add_shear_word(word: str):
    """Add a shear word to the file"""
    async with aiofiles.open(SHEAR_WORDS_FILE, 'a') as f:
        await f.write(word.casefold() + '\n')

async def is_shear(message: str) -> bool:
    """Check if a given message contains any shear words"""
    async with aiofiles.open(SHEAR_WORDS_FILE, 'r') as f:
        content = await f.read()  # Read the content of the file into a string
    shear_words = {line.strip().casefold() for line in content.splitlines()}  # Split the string into lines and create a set of shear words
    words = message.casefold().split()
    return any(word in shear_words for word in words)

async def get_all_shear_words() -> str:
    """Return a string of all shear words separated by tabs, max 3 words per line"""
    async with aiofiles.open(SHEAR_WORDS_FILE, 'r') as f:
        content = await f.read()
        words = [line.strip().casefold() for line in content.splitlines()]
        result = []
        for i in range(0, len(words), 3):
            result.append(','.join(words[i:i+3]) + '\t')
        return ''.join(result).strip()