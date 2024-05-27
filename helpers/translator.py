from gpytranslate import SyncTranslator, Translator
from proxy_randomizer import RegisteredProviders
from json.decoder import JSONDecodeError

rp = RegisteredProviders()
rp.parse_providers()


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


async def translate_async(text, target_language):
    try:
        if target_language == 'English':
            return text
        elif target_language == "Russian":
            tr_lang = "ru"
        elif target_language == "Azerbejani":
            tr_lang = "az"
        else:
            tr_lang = target_language
        t = Translator()
        translation = await t.translate(text, targetlang=tr_lang)
        return translation.text
    except:
        try:
            # Get a new random proxy
            proxy = rp.get_random_proxy()
            print(f"Using new proxy: {proxy}")
            t = Translator(proxies=[proxy])
            translation = await t.translate(text, targetlang=tr_lang)
            return translation.text
        except Exception as e:
            print(f'Error occurred during translation: {e}\n {text}')
            return None
