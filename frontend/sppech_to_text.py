import speech_recognition as sr

# Initialize recognizer
recognizer = sr.Recognizer()

# Use the microphone as the audio source
with sr.Microphone() as source:
    print("Please speak something:")
    # Listen for the first phrase and extract it into audio data
    audio_data = recognizer.listen(source)
    print("Recognizing...")

    # Convert the audio to text
    try:
        text = recognizer.recognize_google(audio_data)
        print(f"You said: {text}")
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
