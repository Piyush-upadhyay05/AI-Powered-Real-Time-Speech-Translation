import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip
import time
import os
import base64
from dotenv import load_dotenv

# ------------------- LOAD ENV -------------------
load_dotenv()
speech_key = os.getenv("Speech_key")
service_region = os.getenv("Speech_region")

speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

# ------------------- LANGUAGES -------------------
language_options = {
    "English": "en", "Hindi": "hi", "French": "fr", "German": "de",
    "Spanish": "es", "Italian": "it", "Japanese": "ja", "Korean": "ko",
    "Russian": "ru", "Portuguese (Portugal)": "pt-PT", "Portuguese (Brazil)": "pt-BR",
    "Chinese (Simplified)": "zh-CN", "Chinese (Traditional)": "zh-TW",
    "Arabic": "ar", "Turkish": "tr", "Thai": "th", "Dutch": "nl",
    "Swedish": "sv", "Polish": "pl", "Tamil": "ta"
}

voice_mapping = {
    "en": "en-US-AriaNeural", "hi": "hi-IN-SwaraNeural", "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural", "es": "es-ES-ElviraNeural", "it": "it-IT-ElsaNeural",
    "ja": "ja-JP-NanamiNeural", "ko": "ko-KR-SunHiNeural", "ru": "ru-RU-DariyaNeural",
    "pt-PT": "pt-PT-FernandaNeural", "pt-BR": "pt-BR-FranciscaNeural",
    "zh-CN": "zh-CN-XiaoxiaoNeural", "zh-TW": "zh-TW-HsiaoChenNeural",
    "ar": "ar-EG-SalmaNeural", "tr": "tr-TR-EmelNeural", "th": "th-TH-PremwadeeNeural",
    "nl": "nl-NL-ColetteNeural", "sv": "sv-SE-HilleviNeural", "pl": "pl-PL-ZofiaNeural",
    "ta": "ta-IN-PallaviNeural"
}

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="🎬 AI OTT Translator", page_icon="🎧", layout="centered")

st.markdown("""
<style>
body {
    background: linear-gradient(120deg, #0f0c29, #302b63, #24243e);
    color: white;
    font-family: 'Poppins', sans-serif;
}
h1 {
    text-align: center;
    color: #FF4B2B;
    font-size: 3rem;
    text-shadow: 0px 0px 20px #FF416C;
}
.upload-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.stButton>button {
    background: linear-gradient(45deg, #FF416C, #FF4B2B);
    border: none;
    color: white;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 30px;
    transition: 0.4s;
}
.stButton>button:hover {
    transform: scale(1.08);
    box-shadow: 0 0 20px #FF4B2B;
}
.box {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 10px;
    margin-top: 10px;
    color: #f2f2f2;
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎬 AI OTT Speech & Video Translator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#ddd;'>Upload video, audio, or speak — auto-detects English or Hindi and translates beautifully!</p>", unsafe_allow_html=True)

# ------------------- INPUT MODE -------------------
input_mode = st.radio("🎙️ Select Input Mode", ["🎥 Upload Video", "🎵 Upload Audio", "🎙️ Speak from Microphone"])

lang_full_names = list(language_options.keys())
default_index = lang_full_names.index("Hindi") if "Hindi" in lang_full_names else 0
selected_lang_name = st.selectbox("🌍 Choose Target Language", lang_full_names, index=default_index)
target_lang = language_options[selected_lang_name]

# ------------------- VIDEO TRANSLATION -------------------
if input_mode == "🎥 Upload Video":
    uploaded_file = st.file_uploader("🎥 Upload your video file", type=["mp4", "mkv", "mov"])
    if uploaded_file:
        file_ext = uploaded_file.name.split(".")[-1]
        input_video_path = f"uploaded_input.{file_ext}"
        with open(input_video_path, "wb") as f:
            f.write(uploaded_file.read())
        st.video(input_video_path)

        if st.button("🚀 Translate & Dub Video"):
            with st.spinner("🎧 Translating and dubbing your video... Please wait ⏳"):
                video_clip = VideoFileClip(input_video_path)
                audio_path = "extracted_audio.wav"
                video_clip.audio.write_audiofile(audio_path, verbose=False, logger=None)

                auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-IN", "hi-IN"])
                audio_input = speechsdk.AudioConfig(filename=audio_path)
                recognizer = speechsdk.SpeechRecognizer(
                    speech_config=speech_config,
                    audio_config=audio_input,
                    auto_detect_source_language_config=auto_detect_config
                )

                full_text = []
                def recognized_handler(evt):
                    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                        full_text.append(evt.result.text)

                recognizer.recognized.connect(recognized_handler)
                recognizer.start_continuous_recognition()
                time.sleep(video_clip.duration + 3)
                recognizer.stop_continuous_recognition()

                original_text = " ".join(full_text)
                if not original_text:
                    st.error("⚠️ Could not recognize any speech. Try a clearer video.")
                else:
                    st.success("✅ Speech recognized successfully!")
                    st.markdown(f"### 🗣️ Recognized Original Speech:\n<div class='box'>{original_text}</div>", unsafe_allow_html=True)
                    translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)
                    st.markdown(f"### 🌐 Translated Text ({selected_lang_name}):\n<div class='box'>{translated_text}</div>", unsafe_allow_html=True)

                    dubbed_audio_path = "dubbed_output.wav"
                    voice = voice_mapping.get(target_lang, "en-US-AriaNeural")
                    speech_config.speech_synthesis_voice_name = voice
                    audio_output = speechsdk.audio.AudioOutputConfig(filename=dubbed_audio_path)
                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
                    synthesizer.speak_text_async(translated_text).get()

                    dubbed_audio = AudioFileClip(dubbed_audio_path)
                    final_video = video_clip.set_audio(dubbed_audio)
                    output_video_path = "dubbed_video.mp4"
                    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

                    st.success("🎉 Translation & dubbing complete! Playing dubbed video below ⬇️")
                    with open(output_video_path, "rb") as video_file:
                        video_bytes = video_file.read()
                        video_b64 = base64.b64encode(video_bytes).decode()
                    st.markdown(f"""
                        <video width="700" controls autoplay style="border-radius: 12px;">
                            <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                        </video>
                    """, unsafe_allow_html=True)
                    st.balloons()

# ------------------- AUDIO TRANSLATION -------------------
elif input_mode == "🎵 Upload Audio":
    uploaded_audio = st.file_uploader("🎵 Upload your audio file", type=["wav", "mp3", "m4a"])
    if uploaded_audio:
        file_ext = uploaded_audio.name.split(".")[-1]
        raw_audio_path = f"temp_audio.{file_ext}"
        with open(raw_audio_path, "wb") as f:
            f.write(uploaded_audio.read())

        # Convert any format (mp3/m4a) → wav automatically
        audio_clip = AudioFileClip(raw_audio_path)
        input_audio_path = "converted_audio.wav"
        audio_clip.write_audiofile(input_audio_path, verbose=False, logger=None)
        audio_clip.close()

        st.audio(input_audio_path)

        if st.button("🚀 Translate & Dub Audio"):
            with st.spinner("🎧 Translating your audio... Please wait ⏳"):
                auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-IN", "hi-IN"])
                audio_input = speechsdk.AudioConfig(filename=input_audio_path)
                recognizer = speechsdk.SpeechRecognizer(
                    speech_config=speech_config,
                    audio_config=audio_input,
                    auto_detect_source_language_config=auto_detect_config
                )

                result = recognizer.recognize_once_async().get()
                if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    original_text = result.text
                    st.success("✅ Speech recognized successfully!")
                    st.markdown(f"### 🗣️ Recognized Original Speech:\n<div class='box'>{original_text}</div>", unsafe_allow_html=True)

                    translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)
                    st.markdown(f"### 🌐 Translated Text ({selected_lang_name}):\n<div class='box'>{translated_text}</div>", unsafe_allow_html=True)

                    dubbed_audio_path = "audio_dubbed_output.wav"
                    voice = voice_mapping.get(target_lang, "en-US-AriaNeural")
                    speech_config.speech_synthesis_voice_name = voice
                    audio_output = speechsdk.audio.AudioOutputConfig(filename=dubbed_audio_path)
                    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
                    synthesizer.speak_text_async(translated_text).get()

                    st.audio(dubbed_audio_path)
                    st.success("🎉 Audio translation & dubbing complete!")
                    st.balloons()
                else:
                    st.error("⚠️ Could not recognize any speech. Please try another audio file.")

# ------------------- MICROPHONE TRANSLATION -------------------
elif input_mode == "🎙️ Speak from Microphone":
    st.markdown("🎤 Click below and speak in **English or Hindi**.")
    if st.button("🎧 Start Recording"):
        with st.spinner("🎙️ Listening... Please speak now!"):
            audio_config = speechsdk.AudioConfig(use_default_microphone=True)
            auto_detect_config = speechsdk.languageconfig.AutoDetectSourceLanguageConfig(languages=["en-IN", "hi-IN"])
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config,
                auto_detect_source_language_config=auto_detect_config
            )

            result = recognizer.recognize_once_async().get()
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                original_text = result.text
                st.success("✅ Speech recognized successfully!")
                st.markdown(f"### 🗣️ You said:\n<div class='box'>{original_text}</div>", unsafe_allow_html=True)

                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)
                st.markdown(f"### 🌐 Translated Text ({selected_lang_name}):\n<div class='box'>{translated_text}</div>", unsafe_allow_html=True)

                dubbed_audio_path = "mic_output.wav"
                voice = voice_mapping.get(target_lang, "en-US-AriaNeural")
                speech_config.speech_synthesis_voice_name = voice
                audio_output = speechsdk.audio.AudioOutputConfig(filename=dubbed_audio_path)
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
                synthesizer.speak_text_async(translated_text).get()

                st.audio(dubbed_audio_path)
                st.success("🎉 Dubbing complete! 🎧")
                st.balloons()
            else:
                st.error("⚠️ No speech detected. Please try again.")

# ------------------- FOOTER -------------------
st.markdown("<hr><p style='text-align:center; color:#aaa;'>Built with ❤️ using Streamlit + Azure Speech + Deep Translator</p>", unsafe_allow_html=True)
