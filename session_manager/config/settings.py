"""
Configuration loader for Session Manager
VCA 1.0 - Phase 1
"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv


class Settings:
    """Load and manage configuration from config.yaml and .env"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

        # Load environment variables
        env_path = Path(".env")
        if env_path.exists():
            load_dotenv(env_path)

        # Load YAML configuration
        self._load_config()

        # Inject environment variables
        self._inject_env_vars()

    def _load_config(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)

    def _inject_env_vars(self):
        """Inject environment variables into configuration"""
        # OpenAI API key
        if 'openai' not in self.config:
            self.config['openai'] = {}

        self.config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')

        # Home Assistant token (not used in revised architecture, but keep for compatibility)
        if 'homeassistant' in self.config:
            self.config['homeassistant']['access_token'] = os.getenv('HA_ACCESS_TOKEN')

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated path.

        Args:
            key_path: Dot-separated path (e.g., 'openai.stt.model')
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            >>> settings.get('openai.stt.model')
            'whisper-1'
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access: settings['openai']"""
        return self.config[key]

    def __repr__(self) -> str:
        return f"Settings(config_path='{self.config_path}')"


# Global settings instance
settings = None


def get_settings(config_path: str = "config.yaml") -> Settings:
    """Get or create global settings instance"""
    global settings
    if settings is None:
        settings = Settings(config_path)
    return settings
