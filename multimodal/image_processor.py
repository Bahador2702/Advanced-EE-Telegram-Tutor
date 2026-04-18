import os
import logging
from PIL import Image
import pytesseract
from faster_whisper import WhisperModel
import aiofiles

logger = logging.getLogger(__name__)

class MultimodalProcessor:
    def __init__(self):
        # OCR Path
        # pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        
        # Whisper Model
        self.whisper = None # Lazy load

    def _ensure_whisper(self):
        if self.whisper is None:
            self.whisper = WhisperModel("base", device="cpu", compute_type="int8")
        return self.whisper

    async def process_image(self, file_path: str) -> str:
        try:
            img = Image.open(file_path)
            # Simple OCR for text extraction from images
            # In production, use vision LLM primarily
            text = pytesseract.image_to_string(img, lang='fas+eng')
            return text
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return ""

    async def transcribe_voice(self, file_path: str) -> str:
        try:
            model = self._ensure_whisper()
            segments, info = model.transcribe(file_path, beam_size=5)
            text = "".join([s.text for s in segments])
            return text
        except Exception as e:
            logger.error(f"Error transcribing voice: {e}")
            return ""
