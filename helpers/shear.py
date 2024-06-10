import aiofiles

SHEAR_AZ_FILE = 'shear_az.txt'
SHEAR_RU_FILE = 'shear_ru.txt'
SHEAR_EN_FILE = 'shear_en.txt'

async def add_shear_word(word: str, lang):
    """Add a shear word to the file"""
    if lang == 'az':
        async with aiofiles.open(SHEAR_AZ_FILE, 'a') as f:
            await f.write(word.casefold() + '\n')
    elif lang == 'ru':
        async with aiofiles.open(SHEAR_RU_FILE, 'a') as f:
            await f.write(word.casefold() + '\n')
    elif lang == 'en':
        async with aiofiles.open(SHEAR_EN_FILE, 'a') as f:
            await f.write(word.casefold() + '\n')
    

async def is_shear(message: str, lang) -> bool:
    """Check if a given message contains any shear words"""
    if lang == 'az':
        SHEAR_WORDS_FILE = SHEAR_AZ_FILE
    elif lang == 'ru':
        SHEAR_WORDS_FILE = SHEAR_RU_FILE
    elif lang == 'en':
        SHEAR_WORDS_FILE = SHEAR_EN_FILE
    else:
        raise ValueError("Invalid language")
    async with aiofiles.open(SHEAR_WORDS_FILE, 'r') as f:
        content = await f.read()  # Read the content of the file into a string
    shear_words = {line.strip().casefold() for line in content.splitlines()}  # Split the string into lines and create a set of shear words
    words = message.casefold().split()
    return any(word in shear_words for word in words)

async def get_all_shear_words(lang) -> str:
    """Return a string of all shear words separated by tabs, max 3 words per line"""
    if lang == 'az':
        SHEAR_WORDS_FILE = SHEAR_AZ_FILE
    elif lang == 'ru':
        SHEAR_WORDS_FILE = SHEAR_RU_FILE
    elif lang == 'en':
        SHEAR_WORDS_FILE = SHEAR_EN_FILE
    else:
        raise ValueError("Invalid language")
    async with aiofiles.open(SHEAR_WORDS_FILE, 'r') as f:
        content = await f.read()
        words = [line.strip().casefold() for line in content.splitlines()]
        result = []
        for i in range(0, len(words), 3):
            result.append(','.join(words[i:i+3]) + '\t')
        return ''.join(result).strip()