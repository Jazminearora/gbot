from gpytranslate import SyncTranslator, Translator
import translators as ts
from proxy_randomizer import RegisteredProviders
from json.decoder import JSONDecodeError
from Modules import LOG_GROUP, cbot

rp = RegisteredProviders()
rp.parse_providers()
_ = ts.preaccelerate_and_speedtest()  # Caching sessions in advance, which can help improve access speed.


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

    try:
        t = Translator()
        translation = await t.translate(text, targetlang=tr_lang)
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
