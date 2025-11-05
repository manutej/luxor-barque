"""Email delivery engine for BARQUE using Charm Pop"""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass

from .user_config import UserConfig


# Re-export for backward compatibility
EmailProvider = EmailProvider


# Legacy EmailConfig wrapper for backward compatibility
@dataclass
class EmailConfig:
    """
    Email configuration (backward compatible wrapper)

    This class maintains backward compatibility with the original API
    while delegating to the new configuration system.
    """
    provider: EmailProvider = EmailProvider.RESEND
    from_email: Optional[str] = None
    signature: Optional[str] = None

    # SMTP specific
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

    # Resend specific
    resend_api_key: Optional[str] = None

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> 'EmailConfig':
        """
        Load configuration from file with environment variable overrides

        Args:
            config_path: Optional path to config file

        Returns:
            EmailConfig instance
        """
        # Use new config loader
        config_data = EmailConfigLoader.load(config_path)

        # Convert to legacy format
        return cls(
            provider=config_data.provider,
            from_email=config_data.defaults.from_email,
            signature=config_data.defaults.signature,
            smtp_host=config_data.smtp.host,
            smtp_port=config_data.smtp.port,
            smtp_username=config_data.smtp.username,
            smtp_password=config_data.smtp.password,
            resend_api_key=config_data.resend.api_key
        )


@dataclass
class EmailMessage:
    """Email message structure"""
    to: List[str]
    subject: str
    body: str
    attachments: List[Path] = None
    from_email: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


@dataclass
class EmailResult:
    """Result of email delivery"""
    success: bool
    message: str
    recipients: List[str]
    error: Optional[str] = None


class EmailSender:
    """Email delivery orchestrator using Charm Pop"""

    def __init__(self, config: Optional[EmailConfig] = None):
        # Load user config from ~/.config/barque/config.yaml
        user_config = UserConfig.load()

        # Start with provided config or create default
        self.config = config or EmailConfig()

        # Merge user config into email config (user config takes precedence if values not set)
        if not self.config.from_email and user_config.default_from_email:
            self.config.from_email = user_config.default_from_email

        if not self.config.signature and user_config.default_email_signature:
            self.config.signature = user_config.default_email_signature

        if not self.config.resend_api_key and user_config.resend_api_key:
            self.config.resend_api_key = user_config.resend_api_key

        # SMTP settings from user config
        if not self.config.smtp_host and user_config.smtp_host:
            self.config.smtp_host = user_config.smtp_host
        if not self.config.smtp_port and user_config.smtp_port:
            self.config.smtp_port = user_config.smtp_port
        if not self.config.smtp_username and user_config.smtp_username:
            self.config.smtp_username = user_config.smtp_username
        if not self.config.smtp_password and user_config.smtp_password:
            self.config.smtp_password = user_config.smtp_password

        self._verify_pop_installed()

    def _verify_pop_installed(self) -> None:
        """Verify that Pop CLI is installed"""
        if not shutil.which("pop"):
            raise RuntimeError(
                "Charm Pop CLI not found. Install it with: brew install pop"
            )

    def send(self, message: EmailMessage) -> EmailResult:
        """
        Send email using Pop CLI

        Args:
            message: EmailMessage to send

        Returns:
            EmailResult with delivery status
        """
        try:
            # Build Pop command
            cmd = self._build_pop_command(message)

            # Execute Pop with message body as stdin
            result = subprocess.run(
                cmd,
                input=message.body,
                capture_output=True,
                text=True,
                check=True,
                env=self._get_env_vars()
            )

            return EmailResult(
                success=True,
                message="Email sent successfully",
                recipients=message.to
            )

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            return EmailResult(
                success=False,
                message="Failed to send email",
                recipients=message.to,
                error=error_msg
            )

        except Exception as e:
            return EmailResult(
                success=False,
                message="Unexpected error sending email",
                recipients=message.to,
                error=str(e)
            )

    def send_pdf_report(
        self,
        to: List[str],
        subject: str,
        pdf_files: List[Path],
        body_template: Optional[str] = None,
        from_email: Optional[str] = None
    ) -> EmailResult:
        """
        Convenience method to send PDF report

        Args:
            to: List of recipient email addresses
            subject: Email subject
            pdf_files: List of PDF files to attach
            body_template: Optional custom body text
            from_email: Optional sender email (overrides config)

        Returns:
            EmailResult with delivery status
        """
        # Build default body if not provided
        if body_template is None:
            pdf_names = [f.name for f in pdf_files]
            body = f"""# PDF Report Generated by BARQUE

Please find attached the following PDF documents:

{chr(10).join(f'- {name}' for name in pdf_names)}

Generated with ❤️ by BARQUE v2.0.0
"""
        else:
            body = body_template

        message = EmailMessage(
            to=to,
            subject=subject,
            body=body,
            attachments=pdf_files,
            from_email=from_email or self.config.from_email
        )

        return self.send(message)

    def _build_pop_command(self, message: EmailMessage) -> List[str]:
        """Build Pop CLI command"""
        cmd = ["pop"]

        # From address
        from_email = message.from_email or self.config.from_email
        if from_email:
            cmd.extend(["--from", from_email])

        # To addresses (multiple recipients)
        for recipient in message.to:
            cmd.extend(["--to", recipient])

        # CC addresses
        if message.cc:
            for cc_addr in message.cc:
                cmd.extend(["--cc", cc_addr])

        # BCC addresses
        if message.bcc:
            for bcc_addr in message.bcc:
                cmd.extend(["--bcc", bcc_addr])

        # Subject
        cmd.extend(["--subject", message.subject])

        # Attachments
        for attachment in message.attachments:
            if attachment.exists():
                cmd.extend(["--attach", str(attachment)])

        return cmd

    def _get_env_vars(self) -> Dict[str, str]:
        """Get environment variables for Pop"""
        import os
        env = os.environ.copy()

        # Resend API key
        if self.config.provider == EmailProvider.RESEND and self.config.resend_api_key:
            env["RESEND_API_KEY"] = self.config.resend_api_key

        # SMTP configuration
        if self.config.provider == EmailProvider.SMTP:
            if self.config.smtp_host:
                env["POP_SMTP_HOST"] = self.config.smtp_host
            if self.config.smtp_port:
                env["POP_SMTP_PORT"] = str(self.config.smtp_port)
            if self.config.smtp_username:
                env["POP_SMTP_USERNAME"] = self.config.smtp_username
            if self.config.smtp_password:
                env["POP_SMTP_PASSWORD"] = self.config.smtp_password

        # From email
        if self.config.from_email:
            env["POP_FROM"] = self.config.from_email

        # Signature
        if self.config.signature:
            env["POP_SIGNATURE"] = self.config.signature

        return env

    @staticmethod
    def check_pop_available() -> bool:
        """Check if Pop CLI is available"""
        return shutil.which("pop") is not None

    @staticmethod
    def get_installation_instructions() -> str:
        """Get installation instructions for Pop"""
        return """
Charm Pop is not installed. Install it with:

macOS/Linux:
  brew install pop

Go:
  go install github.com/charmbracelet/pop@latest

For other installation methods, visit:
  https://github.com/charmbracelet/pop
"""
