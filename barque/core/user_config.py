"""User-level configuration for BARQUE (API keys, email settings, etc.)"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
import os


@dataclass
class UserConfig:
    """User-level configuration stored in ~/.config/barque/config.yaml"""

    # Email settings
    resend_api_key: Optional[str] = None
    default_from_email: Optional[str] = None
    default_email_signature: Optional[str] = None

    # SMTP settings (alternative to Resend)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # General preferences
    default_theme: str = "both"
    default_output_dir: str = "./output"

    @classmethod
    def get_config_dir(cls) -> Path:
        """Get user config directory following XDG standards"""
        # Use XDG_CONFIG_HOME if set, otherwise ~/.config
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / "barque"
        return Path.home() / ".config" / "barque"

    @classmethod
    def get_config_file(cls) -> Path:
        """Get user config file path"""
        return cls.get_config_dir() / "config.yaml"

    @classmethod
    def load(cls) -> "UserConfig":
        """Load user configuration from standard location"""
        config_file = cls.get_config_file()

        if not config_file.exists():
            # Return default config if file doesn't exist
            return cls()

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            return cls._from_dict(data)
        except Exception as e:
            print(f"Warning: Could not load user config: {e}")
            return cls()

    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "UserConfig":
        """Create config from dictionary"""
        email = data.get("email", {})
        smtp = data.get("smtp", {})
        preferences = data.get("preferences", {})

        return cls(
            # Email
            resend_api_key=email.get("resend_api_key"),
            default_from_email=email.get("default_from_email"),
            default_email_signature=email.get("default_signature"),
            # SMTP
            smtp_host=smtp.get("host"),
            smtp_port=smtp.get("port"),
            smtp_username=smtp.get("username"),
            smtp_password=smtp.get("password"),
            # Preferences
            default_theme=preferences.get("default_theme", "both"),
            default_output_dir=preferences.get("default_output_dir", "./output"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config = {
            "email": {},
            "smtp": {},
            "preferences": {}
        }

        # Email settings
        if self.resend_api_key:
            config["email"]["resend_api_key"] = self.resend_api_key
        if self.default_from_email:
            config["email"]["default_from_email"] = self.default_from_email
        if self.default_email_signature:
            config["email"]["default_signature"] = self.default_email_signature

        # SMTP settings
        if self.smtp_host:
            config["smtp"]["host"] = self.smtp_host
        if self.smtp_port:
            config["smtp"]["port"] = self.smtp_port
        if self.smtp_username:
            config["smtp"]["username"] = self.smtp_username
        if self.smtp_password:
            config["smtp"]["password"] = self.smtp_password

        # Preferences
        config["preferences"]["default_theme"] = self.default_theme
        config["preferences"]["default_output_dir"] = self.default_output_dir

        # Remove empty sections
        return {k: v for k, v in config.items() if v}

    def save(self) -> None:
        """Save user configuration to standard location"""
        config_file = self.get_config_file()
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, sort_keys=False)

    def set(self, key: str, value: Any) -> None:
        """Set a configuration value"""
        # Parse dotted key notation (e.g., "email.resend_api_key")
        parts = key.split(".")

        # Map keys to attributes
        key_mapping = {
            "email.resend_api_key": "resend_api_key",
            "email.from": "default_from_email",
            "email.signature": "default_email_signature",
            "smtp.host": "smtp_host",
            "smtp.port": "smtp_port",
            "smtp.username": "smtp_username",
            "smtp.password": "smtp_password",
            "preferences.theme": "default_theme",
            "preferences.output": "default_output_dir",
        }

        full_key = ".".join(parts)
        if full_key not in key_mapping:
            raise ValueError(f"Unknown config key: {key}")

        attr = key_mapping[full_key]

        # Convert value type if needed
        if attr == "smtp_port" and value is not None:
            value = int(value)

        setattr(self, attr, value)

    def get(self, key: str) -> Any:
        """Get a configuration value"""
        # Map keys to attributes
        key_mapping = {
            "email.resend_api_key": "resend_api_key",
            "email.from": "default_from_email",
            "email.signature": "default_email_signature",
            "smtp.host": "smtp_host",
            "smtp.port": "smtp_port",
            "smtp.username": "smtp_username",
            "smtp.password": "smtp_password",
            "preferences.theme": "default_theme",
            "preferences.output": "default_output_dir",
        }

        if key not in key_mapping:
            raise ValueError(f"Unknown config key: {key}")

        attr = key_mapping[key]
        return getattr(self, attr)

    @staticmethod
    def get_default_config_content() -> str:
        """Get default configuration template with comments"""
        return """# BARQUE User Configuration
# This file stores user-level settings like API keys and email preferences.
# Location: ~/.config/barque/config.yaml

# Email settings for sending PDFs via email
email:
  # Resend API key (get one at https://resend.com)
  resend_api_key: "re_your_api_key_here"

  # Default sender email address
  default_from_email: "your-email@example.com"

  # Optional email signature
  # default_signature: "Sent with ❤️ by BARQUE"

# SMTP settings (alternative to Resend)
# smtp:
#   host: "smtp.gmail.com"
#   port: 587
#   username: "your-email@gmail.com"
#   password: "your-app-password"

# User preferences
preferences:
  # Default theme: "light", "dark", or "both"
  default_theme: "both"

  # Default output directory
  default_output_dir: "./output"
"""
