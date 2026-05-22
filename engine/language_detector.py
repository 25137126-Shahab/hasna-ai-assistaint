import re

def is_urdu(text):
    """
    Detect if the given text contains Urdu characters.
    Urdu Unicode range: U+0600 to U+06FF
    """
    urdu_pattern = r'[\u0600-\u06FF]'
    return bool(re.search(urdu_pattern, text))

def detect_language(text):
    """
    Detect the language of the given text.
    Returns 'urdu' if Urdu characters are found, otherwise 'english'
    """
    if is_urdu(text):
        return 'urdu'
    return 'english'

def contains_urdu_keyword(text, keyword_urdu):
    """
    Check if text contains a Urdu keyword
    """
    return keyword_urdu in text