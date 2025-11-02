"""
OpenAI Whisper API STT Provider
VCA 1.0 - Phase 1
"""

import io
from openai import AsyncOpenAI
from ..base import STTProvider, TranscriptionResult


class OpenAIWhisperProvider(STTProvider):
    """OpenAI Whisper API speech-to-text provider"""

    def __init__(self, config: dict):
        super().__init__(config)

        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get('model', 'whisper-1')
        self.language = config.get('language', 'en')
        self.temperature = config.get('temperature', 0.0)
        self.response_format = config.get('response_format', 'text')

    async def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        """
        Transcribe audio using OpenAI Whisper API.

        Args:
            audio_bytes: Raw audio bytes (PCM16, 16kHz recommended)

        Returns:
            TranscriptionResult with transcribed text

        Raises:
            Exception: If API call fails
        """
        # Create file-like object from bytes
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"  # Whisper needs a filename

        # Call OpenAI Whisper API
        response = await self.client.audio.transcriptions.create(
            model=self.model,
            file=audio_file,
            language=self.language,
            temperature=self.temperature,
            response_format=self.response_format
        )

        # Extract text from response
        if isinstance(response, str):
            text = response
        else:
            text = response.text

        return TranscriptionResult(
            text=text.strip(),
            language=self.language
        )

    def __repr__(self) -> str:
        return f"OpenAIWhisperProvider(model='{self.model}', language='{self.language}')"
