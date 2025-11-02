import azure.cognitiveservices.speech as speechsdk
from langdetect import detect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure Speech Configuration
speech_key = os.getenv("Speech_key")
service_region = os.getenv("Speech_region")

print("Speech Key:", speech_key)  # (for testing only, remove later)
print("Region:", service_region)


speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)


#  File Paths

input_file = r"D:\Project Title AI-Powered Real-Time Speech Translation\venv\Data\translated.txt"
output_folder = r"D:\Project Title AI-Powered Real-Time Speech Translation\venv\Data\tts_output"
os.makedirs(output_folder, exist_ok=True)


#  Voice Mapping (Azure Neural Voices)

voice_mapping = {
    "en": "en-US-AriaNeural",
    "hi": "hi-IN-SwaraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural",
    "it": "it-IT-ElsaNeural",
    "ja": "ja-JP-NanamiNeural",
    "ko": "ko-KR-SunHiNeural",
    "ru": "ru-RU-DariyaNeural",
    "pt-PT": "pt-PT-FernandaNeural",
    "pt-BR": "pt-BR-FranciscaNeural",
    "zh-CN": "zh-CN-XiaoxiaoNeural",
    "zh-TW": "zh-TW-HsiaoChenNeural",
    "ar": "ar-EG-SalmaNeural",
    "tr": "tr-TR-EmelNeural",
    "th": "th-TH-PremwadeeNeural",
    "nl": "nl-NL-ColetteNeural",
    "sv": "sv-SE-HilleviNeural",
    "pl": "pl-PL-ZofiaNeural",
    "ta": "ta-IN-PallaviNeural"
}


#  Read Text

with open(input_file, "r", encoding="utf-8") as file:
    text = file.read().strip()

if not text:
    print("⚠️ No text found in the file!")
    exit()

print(f"📝 Text to speak:\n{text}\n")


#  Detect Language Automatically

detected_lang = detect(text)
print(f"🌐 Detected language: {detected_lang}")


#  Set Correct Voice

voice_name = voice_mapping.get(detected_lang, "en-US-AriaNeural")
speech_config.speech_synthesis_voice_name = voice_name
print(f"🎤 Using Azure voice: {voice_name}")


#  Audio Configuration
audio_file_path = os.path.join(output_folder, "output.wav")
audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_file_path)
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)


#  Speak the Text
print("\n🔄 Generating speech...")
result = speech_synthesizer.speak_text_async(text).get()


#  Result & Playback

if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"✅ Speech generated successfully and saved to:\n{audio_file_path}")
    try:
        # Play automatically (Windows only)
        os.startfile(audio_file_path)
    except Exception:
        print("🎵 Speech file saved successfully (auto-play not supported on this system).")

elif result.reason == speechsdk.ResultReason.Canceled:
    cancellation = result.cancellation_details
    print(f"❌ Speech synthesis canceled: {cancellation.reason}")
    if cancellation.reason == speechsdk.CancellationReason.Error:
        print(f"Error details: {cancellation.error_details}")
        print("⚠️ Check if your Azure key and region are correct.")
