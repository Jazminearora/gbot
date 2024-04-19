from gpytranslate import SyncTranslator

def translate_text(text, target_language):
    try:
        t = SyncTranslator()
        translation = t.translate(text, targetlang=target_language)
        return translation.text
    except Exception as e:
        print(f'Error occurred during translation: {e}')
        return None
    
