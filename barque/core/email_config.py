"""Email configuration management for BARQUE"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class EmailProvider(Enum):
    """Email delivery provider"""
    RESEND = "resend"
    SMTP = "smtp"


@dataclass
class ResendConfig:
    """Resend API configuration"""
    api_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResendConfig':
        return cls(api_key=data.get('api_key'))


@dataclass
class SMTPConfig:
    """SMTP configuration"""
    host: Optional[str] = None
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SMTPConfig':
        return cls(
            host=data.get('host'),
            port=data.get('port', 587),
            username=data.get('username'),
            password=data.get('password'),
            use_tls=data.get('use_tls', True)
        )


@dataclass
class DefaultsConfig:
    """Default email settings"""
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    signature: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DefaultsConfig':
        return cls(
            from_email=data.get('from_email'),
            from_name=data.get('from_name'),
            signature=data.get('signature')
        )


@dataclass
class DeliveryConfig:
    """Email delivery configuration"""
    max_retries: int = 3
    retry_delay_seconds: int = 5
    retry_exponential_backoff: bool = True
    rate_limit: int = 60
    max_attachment_size_mb: int = 25
    max_attachments: int = 10

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeliveryConfig':
        return cls(
            max_retries=data.get('max_retries', 3),
            retry_delay_seconds=data.get('retry_delay_seconds', 5),
            retry_exponential_backoff=data.get('retry_exponential_backoff', True),
            rate_limit=data.get('rate_limit', 60),
            max_attachment_size_mb=data.get('max_attachment_size_mb', 25),
            max_attachments=data.get('max_attachments', 10)
        )


@dataclass
class EmailConfigData:
    """Complete email configuration"""
    provider: EmailProvider = EmailProvider.RESEND
    resend: ResendConfig = field(default_factory=ResendConfig)
    smtp: SMTPConfig = field(default_factory=SMTPConfig)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EmailConfigData':
        """Create config from dictionary"""
        provider_str = data.get('provider', 'resend')
        provider = EmailProvider.RESEND if provider_str == 'resend' else EmailProvider.SMTP

        return cls(
            provider=provider,
            resend=ResendConfig.from_dict(data.get('resend', {})),
            smtp=SMTPConfig.from_dict(data.get('smtp', {})),
            defaults=DefaultsConfig.from_dict(data.get('defaults', {})),
            delivery=DeliveryConfig.from_dict(data.get('delivery', {}))
        )


class EmailConfigLoader:
    """Load email configuration from multiple sources with precedence"""

    CONFIG_SEARCH_PATHS = [
        Path.cwd() / ".barque" / "email.yaml",
        Path.home() / ".config" / "barque" / "email.yaml",
        Path.home() / ".barque" / "email.yaml"
    ]

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> EmailConfigData:
        """
        Load email configuration with precedence:
        1. Specified config file
        2. Environment variables
        3. Local config file (.barque/email.yaml)
        4. Global config file (~/.config/barque/email.yaml)
        5. Defaults

        Args:
            config_path: Optional path to config file

        Returns:
            EmailConfigData with merged configuration
        """
        # Start with defaults
        config = EmailConfigData()

        # Load from config file if it exists
        file_config = cls._load_from_file(config_path)
        if file_config:
            config = cls._merge_configs(config, file_config)

        # Override with environment variables (highest priority)
        env_config = cls._load_from_env()
        config = cls._merge_configs(config, env_config)

        return config

    @classmethod
    def _load_from_file(cls, config_path: Optional[Path] = None) -> Optional[EmailConfigData]:
        """Load configuration from YAML file"""
        # Use specified path or search for config
        paths_to_try = [config_path] if config_path else cls.CONFIG_SEARCH_PATHS

        for path in paths_to_try:
            if path and path.exists():
                try:
                    with open(path, 'r') as f:
                        data = yaml.safe_load(f)
                        if data:
                            return EmailConfigData.from_dict(data)
                except Exception as e:
                    print(f"Warning: Failed to load config from {path}: {e}")

        return None

    @classmethod
    def _load_from_env(cls) -> EmailConfigData:
        """Load configuration from environment variables"""
        # Determine provider from env
        provider = EmailProvider.RESEND

        # Check for SMTP env vars
        if any(os.getenv(key) for key in ['POP_SMTP_HOST', 'POP_SMTP_USERNAME']):
            provider = EmailProvider.SMTP

        # Resend config
        resend = ResendConfig(
            api_key=os.getenv('RESEND_API_KEY')
        )

        # SMTP config
        smtp = SMTPConfig(
            host=os.getenv('POP_SMTP_HOST'),
            port=int(os.getenv('POP_SMTP_PORT', '587')),
            username=os.getenv('POP_SMTP_USERNAME'),
            password=os.getenv('POP_SMTP_PASSWORD'),
            use_tls=os.getenv('POP_SMTP_USE_TLS', 'true').lower() == 'true'
        )

        # Defaults config
        defaults = DefaultsConfig(
            from_email=os.getenv('POP_FROM'),
            signature=os.getenv('POP_SIGNATURE')
        )

        return EmailConfigData(
            provider=provider,
            resend=resend,
            smtp=smtp,
            defaults=defaults
        )

    @classmethod
    def _merge_configs(cls, base: EmailConfigData, override: EmailConfigData) -> EmailConfigData:
        """Merge two configs, with override taking precedence"""
        # Merge Resend config
        resend = ResendConfig(
            api_key=override.resend.api_key or base.resend.api_key
        )

        # Merge SMTP config
        smtp = SMTPConfig(
            host=override.smtp.host or base.smtp.host,
            port=override.smtp.port if override.smtp.port != 587 else base.smtp.port,
            username=override.smtp.username or base.smtp.username,
            password=override.smtp.password or base.smtp.password,
            use_tls=override.smtp.use_tls if not base.smtp.use_tls else base.smtp.use_tls
        )

        # Merge defaults
        defaults = DefaultsConfig(
            from_email=override.defaults.from_email or base.defaults.from_email,
            from_name=override.defaults.from_name or base.defaults.from_name,
            signature=override.defaults.signature or base.defaults.signature
        )

        # Merge delivery (override wins completely)
        delivery = override.delivery if override.delivery.max_retries != 3 else base.delivery

        return EmailConfigData(
            provider=override.provider,
            resend=resend,
            smtp=smtp,
            defaults=defaults,
            delivery=delivery
        )

    @classmethod
    def save_example(cls, output_path: Path) -> None:
        """Save example configuration file"""
        example = {
            'provider': 'resend',
            'resend': {
                'api_key': ''
            },
            'smtp': {
                'host': 'smtp.gmail.com',
                'port': 587,
                'username': '',
                'password': '',
                'use_tls': True
            },
            'defaults': {
                'from_email': '',
                'from_name': '',
                'signature': '---\nSent with BARQUE v2.0.0'
            },
            'delivery': {
                'max_retries': 3,
                'retry_delay_seconds': 5,
                'retry_exponential_backoff': True,
                'rate_limit': 60,
                'max_attachment_size_mb': 25,
                'max_attachments': 10
            }
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(example, f, default_flow_style=False, sort_keys=False)


# Backward compatibility wrapper
class EmailConfig:
    """Legacy EmailConfig for backward compatibility"""

    def __init__(self, config_data: Optional[EmailConfigData] = None):
        if config_data is None:
            config_data = EmailConfigLoader.load()

        self.provider = config_data.provider
        self.from_email = config_data.defaults.from_email
        self.signature = config_data.defaults.signature

        # SMTP specific
        self.smtp_host = config_data.smtp.host
        self.smtp_port = config_data.smtp.port
        self.smtp_username = config_data.smtp.username
        self.smtp_password = config_data.smtp.password

        # Resend specific
        self.resend_api_key = config_data.resend.api_key

        # Store full config
        self._config_data = config_data

    @property
    def delivery_config(self) -> DeliveryConfig:
        """Get delivery configuration"""
        return self._config_data.delivery
