from deep_translator import GoogleTranslator

# File paths
input_file = r"D:\Project Title AI-Powered Real-Time Speech Translation\venv\Data\text.txt"
output_file = r"D:\Project Title AI-Powered Real-Time Speech Translation\venv\Data\translated.txt"

# Azure-supported languages (for both Translation + Text-to-Speech)
language_options = {
    "English": "English",
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

# Ask user for language choice
print("🌍 Available languages (Azure TTS compatible):")
for code, name in language_options.items():
    print(f"{code} → {name}")

user_choice = input("\nEnter the language code you want to translate to: ").strip()

if user_choice not in language_options:
    print("❌ Invalid language code. Please try again.")
    exit()

# Translate and output only translated text
with open(input_file, "r", encoding="utf-8") as infile, open(output_file, "w", encoding="utf-8") as outfile:
    for line in infile:
        text = line.strip()
        if not text:
            continue

        try:
            translated_text = GoogleTranslator(source='auto', target=user_choice).translate(text)
            print(translated_text)  # only translated text
            outfile.write(translated_text + "\n")
        except Exception as e:
            outfile.write("Translation Error\n")
