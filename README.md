# pyqt_speech_recognition
PyQt speech recognition demonstrating example (using pydub and speech_recognition, very easy to use)

If you want to run this one

1. git clone
2. pip install -r requirements.txt
3. python main.py

You can find out how this works in script.py as always :)

Basically we have to convert mp3 file into wav file to use speech recognition

This GUI has basic thread to run the script and label(animated loading... label) to demonstrate mp3-to-text work is processing.

## Personal memo
whisper > speech_recognition

### Reason

1. whisper is much faster than speech-recognition

2. whisper can elaborate the sentence unlike speech-recognition (such as periods, capitalization, etc.)

== wav file ==

speech_recognition
0.83
hello my dog is cute

whisper
0.56
Hello, my dog is cute.

== mp3 file ==

speech_recognition
3.3
select a memory card select a file Adventure Mode start your 
adventure here

whisper
0.78
Select a memory card. Select a file. Adventure mode. Start your adventure here.
