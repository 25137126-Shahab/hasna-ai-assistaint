import time
import pyttsx3
import speech_recognition as sr
import eel
from engine.language_detector import detect_language, is_urdu

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 170)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

@eel.expose
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening...')
        eel.DisplayMessage('Listening...')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=10, phrase_time_limit=6)
    
    try:
        print('Recognizing...')
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en')
        print(f'User said: {query}')
        time.sleep(2)
        eel.DisplayMessage(query)
        
    except Exception as e:
        return ""
    
    return query.lower()

@eel.expose
def allCommands():
    query = takeCommand()
    print(query)
    
    lang = detect_language(query)
    print(f'Detected language: {lang}')

    if 'open' in query or 'کھولیں' in query:
        from engine.features import openCommand
        openCommand(query)

    elif 'on youtube' in query or 'یوٹیوب پر' in query:
        from engine.features import PlayYoutube
        PlayYoutube(query)
    else:
        print('Not run')

    eel.ShowHood()