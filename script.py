from pydub import AudioSegment
import speech_recognition as sr


def mp3_to_wav(mp3_file, wav_file):
    sound = AudioSegment.from_mp3(mp3_file)
    sound.export(wav_file, format="wav")

def wav_to_text(mp3_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(mp3_file) as source:
        audio = recognizer.record(source)

    try:
        transcribed_text = recognizer.recognize_google(audio)
        return transcribed_text
    except sr.UnknownValueError:
        return "Speech Recognition could not understand the audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"