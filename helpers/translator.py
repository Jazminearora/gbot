from gpytranslate import SyncTranslator, Translator

from googletrans import Translator

def translate_text(text, target_language):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        print(f'Error occurred during translation: {e}')
        return None
    
async def translate_async(text, target_language):
    try:
        if target_language == 'English':
            tr_lang = "en"
        elif target_language == "Russian":
            tr_lang = "ru"
        elif target_language == "Azerbejani":
            tr_lang = "az"
        else:
            tr_lang = target_language
        t = Translator()
        translation = await t.translate(text, targetlang=tr_lang)
        return translation.text
    except Exception as e:
        print(f'Error occurred during translation: {e}')
        translate_text(text, tr_lang)