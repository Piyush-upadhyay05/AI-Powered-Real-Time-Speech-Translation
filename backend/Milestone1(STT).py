import os
import time
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# -------------------- CONFIGURATION --------------------
BASE_DIR = r"D:\Project Title AI-Powered Real-Time Speech Translation"
INPUT_FOLDER = os.path.join(BASE_DIR, "backend", "assets")

# Load environment variables
load_dotenv()
speech_key = os.getenv("Speech_key")
service_region = os.getenv("Speech_region")

# Azure Speech configuration
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
auto_detect_source_language = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["hi-IN", "en-IN"]
)

# -------------------- SPEECH RECOGNITION --------------------
def recognize_speech_from_file(file_path: str, timeout: int = 60) -> str:
    """Recognize speech from an audio file with Azure Speech SDK."""
    audio_input = speechsdk.AudioConfig(filename=file_path)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        audio_config=audio_input,
        auto_detect_source_language_config=auto_detect_source_language
    )

    recognized_text = []
    done = False

    def on_recognized(evt):
        if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            text = evt.result.text.strip()
            if text:
                recognized_text.append(text)

    def on_stop(evt):
        nonlocal done
        done = True

    recognizer.recognized.connect(on_recognized)
    recognizer.session_stopped.connect(on_stop)
    recognizer.canceled.connect(on_stop)

    recognizer.start_continuous_recognition()

    start_time = time.time()
    while not done and time.time() - start_time < timeout:
        time.sleep(0.5)

    recognizer.stop_continuous_recognition()

    return " ".join(recognized_text)


# -------------------- MAIN PROCESS --------------------
def process_audio_files():
    if not os.path.exists(INPUT_FOLDER):
        return  # silently exit if folder doesn't exist

    wav_files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(".wav")]
    if not wav_files:
        return  # no output if no files found

    for filename in wav_files:
        file_path = os.path.join(INPUT_FOLDER, filename)
        recognized_text = recognize_speech_from_file(file_path)
        if recognized_text:
            print(recognized_text)  # ✅ Only print the recognized speech


if __name__ == "__main__":
    process_audio_files()
