"""Unified configuration manager for BARQUE email workflows"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import os

from .user_config import UserConfig
from .config import BarqueConfig


@dataclass
class UnifiedEmailConfig:
    """
    Unified email configuration that merges all sources in priority order:
    1. Environment variables (highest priority)
    2. Explicit CLI arguments
    3. User config (~/.config/barque/config.yaml)
    4. Smart defaults (lowest priority)

    This eliminates configuration fragmentation and provides single source of truth.
    """

    # Email delivery
    to: Optional[List[str]] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    from_email: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None

    # Provider settings
    provider: str = "resend"
    resend_api_key: Optional[str] = None

    # SMTP settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # PDF generation
    theme: str = "both"
    output_dir: Path = Path("./output")

    # Behavior flags
    auto_send: bool = False
    keep_pdfs: bool = True
    quiet: bool = False

    @classmethod
    def from_cli_args(
        cls,
        to: Optional[List[str]] = None,
        from_email: Optional[str] = None,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        theme: str = "both",
        output: Optional[Path] = None,
        provider: str = "resend",
        resend_api_key: Optional[str] = None,
        smtp_host: Optional[str] = None,
        smtp_port: int = 587,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        auto_send: bool = False,
        keep_pdfs: bool = True,
        quiet: bool = False,
    ) -> "UnifiedEmailConfig":
        """
        Create unified config from CLI arguments.
        Automatically merges with user config and environment variables.
        """
        # Load user config
        user_config = UserConfig.load()

        # Build config with priority: CLI > UserConfig > Env > Defaults
        return cls(
            # Recipients (CLI only, no defaults)
            to=to,
            cc=cc,
            bcc=bcc,

            # Sender (CLI > UserConfig > Env)
            from_email=from_email or user_config.default_from_email or os.getenv("BARQUE_FROM_EMAIL"),

            # Subject and body (CLI only)
            subject=subject,
            body=body,

            # Provider (CLI > UserConfig > Env)
            provider=provider,
            resend_api_key=resend_api_key or user_config.resend_api_key or os.getenv("RESEND_API_KEY"),

            # SMTP (CLI > UserConfig > Env)
            smtp_host=smtp_host or user_config.smtp_host or os.getenv("SMTP_HOST"),
            smtp_port=smtp_port or user_config.smtp_port or int(os.getenv("SMTP_PORT", "587")),
            smtp_username=smtp_username or user_config.smtp_username or os.getenv("SMTP_USERNAME"),
            smtp_password=smtp_password or user_config.smtp_password or os.getenv("SMTP_PASSWORD"),

            # PDF generation (CLI > UserConfig)
            theme=theme or user_config.default_theme,
            output_dir=Path(output) if output else Path(user_config.default_output_dir),

            # Behavior flags
            auto_send=auto_send,
            keep_pdfs=keep_pdfs,
            quiet=quiet,
        )

    @classmethod
    def from_env_file(cls, env_file: Path) -> "UnifiedEmailConfig":
        """Load configuration from .env file for scripting"""
        config = cls()

        if not env_file.exists():
            return config

        # Parse simple KEY=VALUE format
        env_vars = {}
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip().strip('"\'')

        # Apply to config
        if 'BARQUE_TO' in env_vars:
            config.to = [email.strip() for email in env_vars['BARQUE_TO'].split(',')]
        if 'BARQUE_FROM' in env_vars:
            config.from_email = env_vars['BARQUE_FROM']
        if 'BARQUE_SUBJECT' in env_vars:
            config.subject = env_vars['BARQUE_SUBJECT']
        if 'RESEND_API_KEY' in env_vars:
            config.resend_api_key = env_vars['RESEND_API_KEY']
        if 'BARQUE_THEME' in env_vars:
            config.theme = env_vars['BARQUE_THEME']

        return config

    def validate(self) -> tuple[bool, List[str]]:
        """Validate configuration for email sending"""
        errors = []

        # Must have recipients
        if not self.to or len(self.to) == 0:
            errors.append("No recipients specified (--to required)")

        # Must have sender
        if not self.from_email:
            errors.append("No sender email specified (set in user config or use --from)")

        # Provider-specific validation
        if self.provider == "resend":
            if not self.resend_api_key:
                errors.append("Resend API key not configured (set RESEND_API_KEY or use user-config)")
        elif self.provider == "smtp":
            if not self.smtp_host:
                errors.append("SMTP host not configured")
            if not self.smtp_username:
                errors.append("SMTP username not configured")
            if not self.smtp_password:
                errors.append("SMTP password not configured")

        return (len(errors) == 0, errors)

    def get_smart_subject(self, input_file: Path) -> str:
        """Generate smart subject line if not provided"""
        if self.subject:
            return self.subject

        # Try to extract title from markdown
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('# '):
                        return line[2:].strip()
        except Exception:
            pass

        # Fallback to filename
        return f"PDF Report: {input_file.stem}"

    def get_smart_body(self, pdf_files: List[Path]) -> str:
        """Generate smart email body if not provided"""
        if self.body:
            return self.body

        file_list = '\n'.join(f'- {f.name}' for f in pdf_files)

        return f"""# PDF Report Generated by BARQUE

Please find attached the following PDF documents:

{file_list}

---
*Generated with ❤️ by BARQUE v2.0.0*
*Visit: https://github.com/yourusername/barque*
"""

    def to_email_config_dict(self) -> Dict[str, Any]:
        """Convert to dict for EmailSender"""
        from .email import EmailProvider

        return {
            'provider': EmailProvider.RESEND if self.provider == 'resend' else EmailProvider.SMTP,
            'from_email': self.from_email,
            'resend_api_key': self.resend_api_key,
            'smtp_host': self.smtp_host,
            'smtp_port': self.smtp_port,
            'smtp_username': self.smtp_username,
            'smtp_password': self.smtp_password,
        }

    def to_barque_config(self) -> BarqueConfig:
        """Convert to BarqueConfig for PDF generation"""
        config = BarqueConfig.load()
        config.output_dir = self.output_dir
        return config
