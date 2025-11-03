"""
STT Provider Factory

Factory pattern for creating STT (Speech-to-Text) providers based on configuration.
Enables easy switching between different STT providers without code changes.

Usage:
    from stt.factory import STTProviderFactory

    config = {
        'api_key': 'your_key',
        'model': 'whisper-1',
        ...
    }

    # Create provider from config
    provider = STTProviderFactory.create('openai_whisper', config)

    # Or get list of available providers
    providers = STTProviderFactory.get_available_providers()
"""

from typing import Dict, List
import logging

from .base import STTProvider
from .providers.openai_whisper import OpenAIWhisperProvider
from .providers.mock_stt import MockSTTProvider
from .providers.local_whisper import LocalWhisperProvider
from .providers.pytorch_whisper import PyTorchWhisperProvider

logger = logging.getLogger(__name__)


class STTProviderFactory:
    """Factory for creating STT providers."""

    # Registry of available providers
    _providers = {
        'openai_whisper': OpenAIWhisperProvider,
        'mock_stt': MockSTTProvider,
        'local_whisper': LocalWhisperProvider,
        'pytorch_whisper': PyTorchWhisperProvider,
        # Future providers:
        # 'deepgram': DeepgramProvider,
        # 'vosk': VoskProvider,
    }

    @classmethod
    def create(cls, provider_name: str, config: Dict) -> STTProvider:
        """
        Create an STT provider instance.

        Args:
            provider_name: Name of the provider (e.g., 'openai_whisper')
            config: Configuration dictionary for the provider

        Returns:
            Initialized STTProvider instance

        Raises:
            ValueError: If provider_name is not recognized
        """
        if provider_name not in cls._providers:
            available = ', '.join(cls._providers.keys())
            raise ValueError(
                f"Unknown STT provider: '{provider_name}'. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name]
        logger.info(f"Creating STT provider: {provider_name}")

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
            provider_class: The provider class (must inherit from STTProvider)

        Raises:
            TypeError: If provider_class doesn't inherit from STTProvider
        """
        if not issubclass(provider_class, STTProvider):
            raise TypeError(
                f"Provider class must inherit from STTProvider, "
                f"got {provider_class}"
            )

        cls._providers[name] = provider_class
        logger.info(f"Registered new STT provider: {name}")

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
