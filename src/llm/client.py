from openai import OpenAI
from src.config import Config
import base64

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=Config.LLM_API_KEY,
            base_url=Config.LLM_BASE_URL
        )

    def chat_completion(self, messages, stream=False):
        response = self.client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            stream=stream
        )
        return response

    def analyze_image(self, prompt, image_bytes):
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        return self.chat_completion(messages)

    def transcribe_audio(self, audio_file_path):
        # Using OpenAI Whisper-style endpoint if supported by LLM7.io
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
                return transcript.text
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
