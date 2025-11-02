"""
OpenAI TTS API Provider
VCA 1.0 - Phase 1
"""

from openai import AsyncOpenAI
from ..base import TTSProvider, TTSResult


class OpenAITTSProvider(TTSProvider):
    """OpenAI TTS API text-to-speech provider"""

    def __init__(self, config: dict):
        super().__init__(config)

        api_key = config.get('api_key')
        if not api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = config.get('model', 'tts-1')
        self.voice = config.get('voice', 'nova')
        self.speed = config.get('speed', 1.0)

    async def synthesize(self, text: str) -> TTSResult:
        """
        Synthesize speech using OpenAI TTS API.

        Args:
            text: Text to convert to speech

        Returns:
            TTSResult with MP3 audio bytes

        Raises:
            Exception: If API call fails
        """
        # Call OpenAI TTS API
        response = await self.client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
            speed=self.speed,
            response_format="mp3"
        )

        # Read audio bytes from response
        audio_bytes = response.content

        return TTSResult(
            audio_bytes=audio_bytes,
            format='mp3',
            sample_rate=24000  # OpenAI TTS default
        )

    def __repr__(self) -> str:
        return f"OpenAITTSProvider(model='{self.model}', voice='{self.voice}')"
