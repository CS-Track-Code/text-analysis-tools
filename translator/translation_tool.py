from polyglot.text import Text
from translate import Translator


def translate(text, original_language, target_languange):
    translator = Translator(target_languange, original_language)
    chunks = []
    changed = True
    while len(text) > 500 and changed:
        changed = False
        for c in [".", "?", "!"]:
            if 0 < text.find(c) < 500:
                t = text.split(".", 1)
                if len(t[0]) < 500:
                    chunks.append(t[0] + c)
                    text = t[1]
                    changed = True
        if not changed:
            for c in [";", ","]:
                if 0 < text.find(c) < 500 and not changed:
                    t = text.split(".", 1)
                    if len(t[0]) < 500:
                        chunks.append(t[0] + c)
                        text = t[1]
                        changed = True

    if len(text) > 0:
        chunks.append(text)
    translated = ""
    for chunk in chunks:
        translated += translator.translate(chunk) + " "
    return translated


def get_language(input_text):
    text = Text(input_text)
    lang = text.language.code
    return lang

