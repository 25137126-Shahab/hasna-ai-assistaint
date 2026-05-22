import os
import re
import sqlite3
import webbrowser
from playsound import playsound
import eel

from engine.command import speak
from engine.config import ASSISTANT_NAME, ASSISTANT_NAME_URDU
from engine.language_detector import detect_language, is_urdu
import pywhatkit as kit

conn = sqlite3.connect("hansa.db")
cursor = conn.cursor()

def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

@eel.expose
def playClickSound():
    music_dir = "www\\assets\\audio\\click_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace(ASSISTANT_NAME_URDU, "")
    query = query.replace("open", "").replace("کھولیں", "").strip().lower()

    if query != "":
        try:
            cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening " + query)
                os.startfile(results[0][0])
                return

            cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (query,))
            results = cursor.fetchall()
            
            if len(results) != 0:
                speak("Opening " + query)
                webbrowser.open(results[0][0])
                return

            speak("Opening " + query)
            try:
                os.system('start ' + query)
            except Exception as e:
                speak(f"Unable to open {query}. Error: {str(e)}")

        except Exception as e:
            speak(f"Something went wrong: {str(e)}")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    if search_term:
        speak("Playing " + search_term + " on YouTube")
        kit.playonyt(search_term)
    else:
        speak("Sorry, I couldn't find what to play on YouTube.")

def extract_yt_term(command):
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    if match:
        return match.group(1)
    
    urdu_pattern = r'یوٹیوب پر\s+(.*?)\s+چلائیں'
    urdu_match = re.search(urdu_pattern, command, re.IGNORECASE)
    return urdu_match.group(1) if urdu_match else None