"""
TTS Provider Factory

Factory pattern for creating TTS (Text-to-Speech) providers based on configuration.
Enables easy switching between different TTS providers without code changes.

Usage:
    from tts.factory import TTSProviderFactory

    config = {
        'api_key': 'your_key',
        'model': 'tts-1',
        'voice': 'nova',
        ...
    }

    # Create provider from config
    provider = TTSProviderFactory.create('openai_tts', config)

    # Or get list of available providers
    providers = TTSProviderFactory.get_available_providers()
"""

from typing import Dict, List
import logging

from .base import TTSProvider
from .providers.openai_tts import OpenAITTSProvider
from .providers.mock_tts import MockTTSProvider

logger = logging.getLogger(__name__)


class TTSProviderFactory:
    """Factory for creating TTS providers."""

    # Registry of available providers
    _providers = {
        'openai_tts': OpenAITTSProvider,
        'mock_tts': MockTTSProvider,
        # Future providers will be added here:
        # 'piper': PiperTTSProvider,
        # 'elevenlabs': ElevenLabsTTSProvider,
    }

    @classmethod
    def create(cls, provider_name: str, config: Dict) -> TTSProvider:
        """
        Create a TTS provider instance.

        Args:
            provider_name: Name of the provider (e.g., 'openai_tts')
            config: Configuration dictionary for the provider

        Returns:
            Initialized TTSProvider instance

        Raises:
            ValueError: If provider_name is not recognized
        """
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unknown TTS provider: '{provider_name}'. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name]
        logger.info(f"Creating TTS provider: {provider_name}")

        try:
            provider = provider_class(config)
            logger.info(f"Successfully initialized: {provider}")
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize {provider_name}: {e}", exc_info=True)
            raise

    @classmethod
    def get_available_providers(cls) -> List[str]:
        """
        Get list of available provider names.

        Returns:
            List of provider names that can be created
        """
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """
        Register a new provider class.

        This allows plugins or extensions to register custom providers.

        Args:
            name: Name to register the provider under
            provider_class: The provider class (must inherit from TTSProvider)

        Raises:
            TypeError: If provider_class doesn't inherit from TTSProvider
        """
        if not issubclass(provider_class, TTSProvider):
            raise TypeError(
                f"Provider class must inherit from TTSProvider, "
                f"got {provider_class}"
            )

        cls._providers[name] = provider_class
        logger.info(f"Registered new TTS provider: {name}")

    @classmethod
    def is_provider_available(cls, provider_name: str) -> bool:
        """
        Check if a provider is available.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is available, False otherwise
        """
        return provider_name in cls._providers
