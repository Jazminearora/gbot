from gpytranslate import SyncTranslator, Translator
import translators as ts
from proxy_randomizer import RegisteredProviders
from json.decoder import JSONDecodeError
from Modules import LOG_GROUP, cbot

rp = RegisteredProviders()
rp.parse_providers()

MAX_CACHE_LENGTH = 250  # adjust this value to your needs

cache = {}

def get_cached_translation(text, target_language):
    key = f"{text}:{target_language}"
    if key in cache:
        return cache[key]
    return None

def set_cache_translation(text, target_language, translation):
    if len(text) <= MAX_CACHE_LENGTH:
        key = f"{text}:{target_language}"
        cache[key] = translation


##================================================================================================##
##================================================================================================##


async def translate_async(text: str, target_language):
    if target_language == 'English':
        return text
    elif target_language == "Russian":
        tr_lang = "ru"
    elif target_language == "Azerbejani":
        tr_lang = "az"
    else:
        tr_lang = target_language
    cached_translation = get_cached_translation(text, tr_lang)
    if cached_translation:
        return cached_translation

    try:
        t = Translator()
        translation = await t.translate(text, targetlang=tr_lang)
        set_cache_translation(text, tr_lang, translation.text)
        return translation.text
    except Exception as e:
        if isinstance(e, Exception):  # catch all exceptions
            try:
                translation = ts.translate_text(text, translator="google", to_language=tr_lang)
                return translation
            except Exception as e:
                try:
                    translation = ts.translate_text(text, translator="bing", to_language=tr_lang)
                    return translation
                except Exception as e:
                    try:
                        # Get a new random proxy
                        proxy = rp.get_random_proxy()
                        print(f"Using new proxy: {proxy}")
                        t = Translator(proxies=[proxy])
                        translation = await t.translate(text, targetlang=tr_lang)
                        return translation.text
                    except Exception as e:
                        await cbot.send_message(LOG_GROUP, f'Error occurred during translation: {e}')
                        return text


##================================================================================================##
##================================================================================================##


def translate_text(text, target_language):
    try:
        if target_language == 'English':
            tr_lang = "en"
        elif target_language == "Russian":
            tr_lang = "ru"
        elif target_language == "Azerbejani":
            tr_lang = "az"
        else:
            tr_lang = target_language
        t = SyncTranslator()
        translation = t.translate(text, targetlang=tr_lang)
        return translation.text
    except Exception as e:
        print(f'Error occurred during translation: {e}')
        return None
    
