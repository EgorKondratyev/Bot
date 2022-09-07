from aiogoogletrans import Translator

from databases.client_side import LanguageDB


async def translate_from_lang_russian(user_id: int, text: str | list) -> str | list:
    """Перевод из русского языка в предпочтительный для текущего пользователя"""
    language_db = LanguageDB()
    to_language = language_db.get_language_user(user_id=user_id)
    if to_language != 'ru':
        translator = Translator()
        translate_text = await translator.translate(text=text, src='russian', dest=to_language)
        return translate_text.text
    return text
