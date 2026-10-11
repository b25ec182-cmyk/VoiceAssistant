import speech_recognition as sr
import pyttsx3


class SpeechInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def listen_once(self):
        try:
            with sr.Microphone() as microphone:
                self.recognizer.adjust_for_ambient_noise(microphone, duration=0.5)
                audio = self.recognizer.listen(microphone, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError as error:
            raise RuntimeError("No speech detected. Press Start listening and try again.") from error
        except OSError as error:
            raise RuntimeError(
                "I could not access a microphone. Check that one is connected and enabled."
            ) from error

        try:
            return self.recognizer.recognize_google(audio)
        except sr.UnknownValueError as error:
            raise RuntimeError("I could not understand that. Please try again.") from error
        except sr.RequestError as error:
            raise RuntimeError(
                "Speech recognition is unavailable. Check your internet connection."
            ) from error


def speak_text(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()