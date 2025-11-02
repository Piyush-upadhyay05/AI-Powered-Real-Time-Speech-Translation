import streamlit as st
import azure.cognitiveservices.speech as speechsdk
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip, AudioFileClip
import time
import os
import base64

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

language_options = {
    "en": "English", "hi": "Hindi", "fr": "French", "de": "German",
    "es": "Spanish", "it": "Italian", "ja": "Japanese", "ko": "Korean",
    "ru": "Russian", "pt-PT": "Portuguese (Portugal)", "pt-BR": "Portuguese (Brazil)",
    "zh-CN": "Chinese (Simplified)", "zh-TW": "Chinese (Traditional)",
    "ar": "Arabic", "tr": "Turkish", "th": "Thai", "nl": "Dutch",
    "sv": "Swedish", "pl": "Polish", "ta": "Tamil"
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
st.markdown("<p style='text-align:center; color:#ddd;'>Upload a video, choose your language, and watch it dubbed live!</p>", unsafe_allow_html=True)

# ------------------- INPUT AREA -------------------
with st.container():
    st.markdown("<div class='upload-container'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("🎥 Upload your video file", type=["mp4", "mkv", "mov"])
    st.markdown("</div>", unsafe_allow_html=True)

target_lang = st.selectbox("🌍 Choose Target Language", list(language_options.keys()), index=1)

# ------------------- PROCESSING -------------------
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

            # 1️⃣ Speech Recognition
            audio_input = speechsdk.AudioConfig(filename=audio_path)
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)
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
                translated_text = GoogleTranslator(source='auto', target=target_lang).translate(original_text)

                # 📝 Display recognized and translated text
                st.markdown("### 🗣️ Recognized Original Speech:")
                st.markdown(f"<div class='box'>{original_text}</div>", unsafe_allow_html=True)

                st.markdown(f"### 🌐 Translated Text ({language_options[target_lang]}):")
                st.markdown(f"<div class='box'>{translated_text}</div>", unsafe_allow_html=True)

                # 2️⃣ Speech synthesis (Dubbed Audio)
                dubbed_audio_path = "dubbed_output.wav"
                voice = voice_mapping.get(target_lang, "en-US-AriaNeural")
                speech_config.speech_synthesis_voice_name = voice
                audio_output = speechsdk.audio.AudioOutputConfig(filename=dubbed_audio_path)
                synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
                synthesizer.speak_text_async(translated_text).get()

                # 3️⃣ Combine dubbed audio with video
                dubbed_audio = AudioFileClip(dubbed_audio_path)
                final_video = video_clip.set_audio(dubbed_audio)
                output_video_path = "dubbed_video.mp4"
                final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

                # 4️⃣ Show dubbed video (auto fullscreen + autoplay)
                st.success("🎉 Translation & dubbing complete! Playing dubbed video below ⬇️")
                time.sleep(1)
                st.markdown("### 🎧 Dubbed Video Output:")

                with open(output_video_path, "rb") as video_file:
                    video_bytes = video_file.read()
                    video_b64 = base64.b64encode(video_bytes).decode()

                # --- ✅ AUTO FULLSCREEN SCRIPT ---
                video_html = f"""
                    <video id="dubbedVideo" width="700" controls autoplay style="border-radius: 12px;">
                        <source src="data:video/mp4;base64,{video_b64}" type="video/mp4">
                        Your browser does not support the video tag.
                    </video>
                    <script>
                        const video = document.getElementById('dubbedVideo');
                        function openFullscreen() {{
                            if (video.requestFullscreen) {{
                                video.requestFullscreen();
                            }} else if (video.webkitEnterFullscreen) {{
                                video.webkitEnterFullscreen();  // iPhone/iPad
                            }} else if (video.webkitRequestFullscreen) {{
                                video.webkitRequestFullscreen();
                            }} else if (video.msRequestFullscreen) {{
                                video.msRequestFullscreen();
                            }}
                        }}
                        video.addEventListener('canplay', () => {{
                            setTimeout(() => {{
                                video.play();
                                openFullscreen();
                            }}, 1000);
                        }});
                    </script>
                """
                st.markdown(video_html, unsafe_allow_html=True)
                st.balloons()

# ------------------- FOOTER -------------------
st.markdown("<hr><p style='text-align:center; color:#aaa;'>Built with ❤️ using Streamlit + Azure Speech + Deep Translator</p>", unsafe_allow_html=True)
