import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
import os
import time

# ----------------------------- #
# 🔹 Azure Speech Configuration
# ----------------------------- #
speech_key = "Speech_key"
service_region = "Speech_region"

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# ----------------------------- #
# 🔹 File Paths
# ----------------------------- #
output_audio_folder = r"D:\Project Title AI-Powered Real-Time Speech Translation\venv\Data\tts_output"
os.makedirs(output_audio_folder, exist_ok=True)

# ----------------------------- #
# 🔹 Supported Languages
# ----------------------------- #
language_options = {
    "en": "English",
    "hi": "Hindi",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "pt-PT": "Portuguese (Portugal)",
    "pt-BR": "Portuguese (Brazil)",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "ar": "Arabic",
    "tr": "Turkish",
    "th": "Thai",
    "nl": "Dutch",
    "sv": "Swedish",
    "pl": "Polish",
    "ta": "Tamil"
}

# ----------------------------- #
# 🔹 Voice Mapping for Azure TTS
# ----------------------------- #
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

# ----------------------------- #
# 🔹 Ask user for target language
# ----------------------------- #
print("🌍 Available languages for translation and speech output:")
for code, name in language_options.items():
    print(f"{code} → {name}")

target_lang = input("\nEnter the language code you want to translate to: ").strip()

if target_lang not in language_options:
    print("❌ Invalid language code! Exiting.")
    exit()

voice_name = voice_mapping.get(target_lang, "en-US-AriaNeural")
speech_config.speech_synthesis_voice_name = voice_name
print(f"\n🎯 Target language: {language_options[target_lang]} ({target_lang})")
print(f"🎤 Using Azure voice: {voice_name}")

# ----------------------------- #
# 🔹 Speech Recognizer Setup
# ----------------------------- #
# Auto language detection between English & Hindi (you can add more)
auto_detect_language = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
    languages=["en-IN", "hi-IN"]
)
audio_input = speechsdk.audio.AudioConfig(use_default_microphone=True)

speech_recognizer = speechsdk.SpeechRecognizer(
    speech_config=speech_config,
    auto_detect_source_language_config=auto_detect_language,
    audio_config=audio_input
)

# ----------------------------- #
# 🔹 Speech Synthesizer Setup
# ----------------------------- #
def speak_text(text, count):
    audio_path = os.path.join(output_audio_folder, f"translated_{count}.wav")
    audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    result = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"🔊 Played translated text: {text}")
        os.startfile(audio_path)
    elif result.reason == speechsdk.ResultReason.Canceled:
        print("❌ Speech synthesis canceled.")

# ----------------------------- #
# 🔹 Real-Time Recognition + Translation
# ----------------------------- #
print("\n🎙️ Speak now! Your speech will be translated and spoken in real-time.")
print("Press Ctrl+C to stop.\n")

count = 1

def recognized_handler(evt):
    global count
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        recognized_text = evt.result.text.strip()
        if recognized_text:
            print(f"\n🗣️ You said: {recognized_text}")
            try:
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(recognized_text)
                print(f"🌐 Translated ({language_options[target_lang]}): {translated_text}")
                speak_text(translated_text, count)
                count += 1
            except Exception as e:
                print(f"⚠️ Translation error: {e}")

speech_recognizer.recognized.connect(recognized_handler)

speech_recognizer.start_continuous_recognition()

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n🛑 Stopped by user.")
finally:
    speech_recognizer.stop_continuous_recognition()
    print("✅ Translation session ended.")
