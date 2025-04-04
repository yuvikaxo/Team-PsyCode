import speech_recognition as sr
import pyttsx3
from transformers import pipeline

recognizer = sr.Recognizer()
engine = pyttsx3.init()
chatbot = pipeline("text-generation", model="gpt2")

def listen():
    with sr.Microphone() as source:
        print("👂 Listening...")
        audio = recognizer.listen(source, phrase_time_limit=5)
        try:
            text = recognizer.recognize_sphinx(audio)
            print("🗣️ You said:", text)
            return text
        except:
            print("❌ Didn't catch that.")
            return ""

def speak(text):
    engine.say(text)
    engine.runAndWait()

def respond(prompt):
    result = chatbot(prompt, max_length=60, num_return_sequences=1)[0]['generated_text']
    return result.split("\n")[0]

print("🤖 Hello! I'm your fully offline AI assistant. Say something!")

while True:
    query = listen()
    if "stop" in query.lower():
        speak("Goodbye!")
        break
    if query:
        reply = respond(query)
        print("🤖", reply)
        speak(reply)
