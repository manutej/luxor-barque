"""Command-line interface for BARQUE"""

import click
from pathlib import Path
import sys

from ..core.generator import PDFGenerator
from ..core.config import BarqueConfig
from ..core.email import EmailSender, EmailConfig, EmailProvider, EmailMessage


@click.group()
@click.version_option(version="2.0.0", prog_name="barque")
@click.pass_context
def main(ctx):
    """
    BARQUE - Beautiful Automated Report and Query Universal Engine

    Multi-modal document orchestration with dual-theme PDF generation and email delivery.

    \b
    Examples:
      barque init                                  # Initialize BARQUE
      barque generate document.md                  # Generate PDF (both themes)
      barque generate doc.md --theme light         # Generate light theme only
      barque batch docs/ --workers 8               # Process directory with 8 workers
      barque send doc.md --to user@example.com     # Generate PDF and email it
      barque email file.pdf --to user@example.com  # Send existing file via email
                           --subject "Report"
    """
    ctx.ensure_object(dict)


@main.command()
@click.option(
    '--directory',
    type=click.Path(exists=False),
    default='.',
    help='Directory to initialize (default: current directory)'
)
def init(directory):
    """Initialize BARQUE configuration in directory"""
    config_dir = Path(directory) / ".barque"
    config_file = config_dir / "config.yaml"

    if config_file.exists():
        click.secho("⚠️  Configuration already exists!", fg="yellow")
        if not click.confirm("Overwrite existing configuration?"):
            click.echo("Initialization cancelled.")
            return

    # Create configuration directory
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "themes").mkdir(exist_ok=True)

    # Create default configuration
    default_config = BarqueConfig()
    default_config.save(config_file)

    click.secho(f"✓ Created configuration: {config_file}", fg="green")
    click.secho(f"✓ Created themes directory: {config_dir / 'themes'}", fg="green")
    click.secho("\n✅ BARQUE initialized successfully!", fg="green", bold=True)

    # Show next steps
    click.echo("\nNext steps:")
    click.echo("  1. Edit .barque/config.yaml to customize settings")
    click.echo("  2. Run 'barque generate <file.md>' to create PDFs")
    click.echo("  3. Run 'barque batch <directory>' for bulk processing")


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option(
    '--theme',
    type=click.Choice(['light', 'dark', 'both']),
    default='both',
    help='Theme selection (default: both)'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Output directory (default: ./output)'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Custom config file path'
)
def generate(file, theme, output, config):
    """Generate PDF from markdown file"""
    input_file = Path(file)

    click.echo(f"\n📄 Processing: {input_file.name}")

    # Load configuration
    if config:
        barque_config = BarqueConfig.load(Path(config))
    else:
        barque_config = BarqueConfig.load()

    # Override output directory if specified
    if output:
        barque_config.output_dir = Path(output)

    # Create generator
    generator = PDFGenerator(barque_config)

    # Generate PDF
    with click.progressbar(
        length=1,
        label='Generating PDF',
        show_eta=False
    ) as bar:
        result = generator.generate(
            input_file=input_file,
            theme=theme
        )
        bar.update(1)

    # Display results
    if result.success:
        click.secho("\n✓ Generation successful!", fg="green", bold=True)
        for pdf_file in result.files:
            click.echo(f"  📑 {pdf_file}")

        # Show metadata summary
        if result.metadata:
            meta = result.metadata
            click.echo(f"\n📊 Statistics:")
            click.echo(f"  Words: {meta.get('word_count', 0):,}")
            click.echo(f"  Sections: {meta.get('section_count', 0)}")
            if meta.get('has_math'):
                click.echo(f"  Math formulas: Yes 📐")
    else:
        click.secho(f"\n✗ Error: {result.error}", fg="red", bold=True)
        sys.exit(1)


@main.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option(
    '--output',
    type=click.Path(),
    help='Output directory (default: ./output)'
)
@click.option(
    '--theme',
    type=click.Choice(['light', 'dark', 'both']),
    default='both',
    help='Theme selection (default: both)'
)
@click.option(
    '--workers',
    type=int,
    default=4,
    help='Number of parallel workers (default: 4)'
)
@click.option(
    '--pattern',
    default='**/*.md',
    help='File pattern to match (default: **/*.md)'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Custom config file path'
)
def batch(directory, output, theme, workers, pattern, config):
    """Process all markdown files in directory"""
    input_dir = Path(directory)

    click.echo(f"\n📚 Batch processing: {input_dir}")
    click.echo(f"   Pattern: {pattern}")
    click.echo(f"   Workers: {workers}")
    click.echo(f"   Theme: {theme}")

    # Load configuration
    if config:
        barque_config = BarqueConfig.load(Path(config))
    else:
        barque_config = BarqueConfig.load()

    # Override settings if specified
    if output:
        barque_config.output_dir = Path(output)
    if workers:
        barque_config.workers = workers

    # Create generator
    generator = PDFGenerator(barque_config)

    # Find markdown files
    md_files = list(input_dir.glob(pattern))
    total_files = len(md_files)

    if total_files == 0:
        click.secho(f"\n⚠️  No markdown files found matching '{pattern}'", fg="yellow")
        return

    click.echo(f"\n🔍 Found {total_files} files to process\n")

    # Process files with progress bar
    success_count = 0
    error_count = 0

    with click.progressbar(
        md_files,
        label='Processing files',
        show_pos=True
    ) as files:
        results = []
        for md_file in files:
            result = generator.generate(
                input_file=md_file,
                theme=theme
            )
            results.append(result)

            if result.success:
                success_count += 1
            else:
                error_count += 1

    # Generate index if enabled
    if barque_config.create_index:
        click.echo("\n📑 Generating index...")
        index_file = generator.generate_index()
        click.secho(f"✓ Index created: {index_file}", fg="green")

    # Display summary
    click.echo("\n" + "=" * 60)
    click.secho("📊 Batch Processing Complete!", fg="green", bold=True)
    click.echo("=" * 60)
    click.echo(f"  Total files: {total_files}")
    click.secho(f"  Successful: {success_count}", fg="green")
    if error_count > 0:
        click.secho(f"  Errors: {error_count}", fg="red")
    click.echo(f"\n📂 Output directory: {barque_config.output_dir}")
    click.echo("=" * 60 + "\n")


@main.command()
@click.option(
    '--all',
    is_flag=True,
    help='Clean output and cache directories'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Output directory to clean (default: ./output)'
)
def clean(all, output):
    """Remove generated output files"""
    import shutil

    output_dir = Path(output) if output else Path("./output")

    if not output_dir.exists():
        click.secho("⚠️  Output directory does not exist", fg="yellow")
        return

    click.echo(f"🧹 Cleaning: {output_dir}")

    if not click.confirm("Are you sure you want to delete generated files?"):
        click.echo("Clean cancelled.")
        return

    # Remove directories
    dirs_to_remove = ['light', 'dark', 'metadata']
    if all:
        dirs_to_remove.extend(['.temp', '.cache'])

    for dir_name in dirs_to_remove:
        dir_path = output_dir / dir_name
        if dir_path.exists():
            shutil.rmtree(dir_path)
            click.secho(f"✓ Removed: {dir_name}/", fg="green")

    # Remove index file
    index_file = output_dir / "INDEX.md"
    if index_file.exists():
        index_file.unlink()
        click.secho(f"✓ Removed: INDEX.md", fg="green")

    click.secho("\n✅ Clean complete!", fg="green", bold=True)


@main.command()
@click.option(
    '--show',
    is_flag=True,
    help='Show current configuration'
)
@click.option(
    '--validate',
    is_flag=True,
    help='Validate configuration'
)
@click.option(
    '--config',
    type=click.Path(exists=True),
    help='Custom config file path'
)
def config_cmd(show, validate, config):
    """Manage BARQUE configuration"""
    # Load configuration
    if config:
        barque_config = BarqueConfig.load(Path(config))
        config_file = Path(config)
    else:
        config_file = BarqueConfig._find_config()
        barque_config = BarqueConfig.load(config_file)

    if show:
        click.echo("\n📋 Current Configuration")
        click.echo("=" * 60)

        if config_file:
            click.echo(f"Config file: {config_file}")
        else:
            click.echo("Config file: <using defaults>")

        click.echo(f"\nProject: {barque_config.project_name}")
        click.echo(f"Output: {barque_config.output_dir}")
        click.echo(f"Workers: {barque_config.workers}")
        click.echo(f"Math support: {'✓' if barque_config.math_enabled else '✗'}")

        click.echo("\nLight theme:")
        for key, value in barque_config.light_theme.items():
            click.echo(f"  {key}: {value}")

        click.echo("\nDark theme:")
        for key, value in barque_config.dark_theme.items():
            click.echo(f"  {key}: {value}")

        click.echo("=" * 60 + "\n")

    if validate:
        is_valid, errors = barque_config.validate()

        if is_valid:
            click.secho("✓ Configuration is valid!", fg="green", bold=True)
        else:
            click.secho("✗ Configuration has errors:", fg="red", bold=True)
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)


# Alias for config command
main.add_command(config_cmd, name='config')


@main.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--to',
    multiple=True,
    required=True,
    help='Recipient email address (can specify multiple times)'
)
@click.option(
    '--subject',
    required=True,
    help='Email subject line'
)
@click.option(
    '--from',
    'from_email',
    help='Sender email address'
)
@click.option(
    '--body',
    help='Email body text (markdown supported)'
)
@click.option(
    '--cc',
    multiple=True,
    help='CC email address (can specify multiple times)'
)
@click.option(
    '--bcc',
    multiple=True,
    help='BCC email address (can specify multiple times)'
)
@click.option(
    '--provider',
    type=click.Choice(['resend', 'smtp']),
    default='resend',
    help='Email provider (default: resend)'
)
@click.option(
    '--smtp-host',
    help='SMTP server hostname'
)
@click.option(
    '--smtp-port',
    type=int,
    default=587,
    help='SMTP server port (default: 587)'
)
@click.option(
    '--smtp-username',
    help='SMTP username'
)
@click.option(
    '--smtp-password',
    help='SMTP password'
)
@click.option(
    '--resend-api-key',
    help='Resend API key (or set RESEND_API_KEY env var)'
)
def email(files, to, subject, from_email, body, cc, bcc, provider,
          smtp_host, smtp_port, smtp_username, smtp_password, resend_api_key):
    """Send files via email using Charm Pop"""

    # Check if Pop is installed
    if not EmailSender.check_pop_available():
        click.secho("\n✗ Charm Pop is not installed!", fg="red", bold=True)
        click.echo(EmailSender.get_installation_instructions())
        sys.exit(1)

    # Convert file paths to Path objects
    file_paths = [Path(f) for f in files]

    # Verify files exist
    for file_path in file_paths:
        if not file_path.exists():
            click.secho(f"\n✗ File not found: {file_path}", fg="red", bold=True)
            sys.exit(1)

    click.echo(f"\n📧 Preparing email...")
    click.echo(f"   To: {', '.join(to)}")
    click.echo(f"   Subject: {subject}")
    click.echo(f"   Attachments: {len(file_paths)}")

    for file_path in file_paths:
        click.echo(f"     - {file_path.name} ({file_path.stat().st_size / 1024:.1f} KB)")

    # Build email configuration
    email_config = EmailConfig(
        provider=EmailProvider.RESEND if provider == 'resend' else EmailProvider.SMTP,
        from_email=from_email,
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        resend_api_key=resend_api_key
    )

    # Create default body if not provided
    if body is None:
        file_names = [f.name for f in file_paths]
        body = f"""# Files from BARQUE

Please find attached the following files:

{chr(10).join(f'- {name}' for name in file_names)}

---
*Sent with ❤️ by BARQUE v2.0.0*
"""

    # Create email message
    message = EmailMessage(
        to=list(to),
        subject=subject,
        body=body,
        attachments=file_paths,
        from_email=from_email,
        cc=list(cc) if cc else None,
        bcc=list(bcc) if bcc else None
    )

    # Send email
    try:
        sender = EmailSender(email_config)

        with click.progressbar(
            length=1,
            label='Sending email',
            show_eta=False
        ) as bar:
            result = sender.send(message)
            bar.update(1)

        # Display results
        if result.success:
            click.secho("\n✓ Email sent successfully!", fg="green", bold=True)
            click.echo(f"   Sent to: {', '.join(result.recipients)}")
        else:
            click.secho(f"\n✗ Failed to send email", fg="red", bold=True)
            if result.error:
                click.echo(f"   Error: {result.error}")
            sys.exit(1)

    except Exception as e:
        click.secho(f"\n✗ Error: {str(e)}", fg="red", bold=True)
        sys.exit(1)


@main.command()
@click.argument('file', type=click.Path(exists=True))
@click.option(
    '--to',
    multiple=True,
    required=True,
    help='Recipient email address (can specify multiple times)'
)
@click.option(
    '--subject',
    help='Email subject (default: auto-generated from filename)'
)
@click.option(
    '--from',
    'from_email',
    help='Sender email address'
)
@click.option(
    '--theme',
    type=click.Choice(['light', 'dark', 'both']),
    default='both',
    help='Theme selection (default: both)'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Output directory (default: ./output)'
)
@click.option(
    '--provider',
    type=click.Choice(['resend', 'smtp']),
    default='resend',
    help='Email provider (default: resend)'
)
@click.option(
    '--body',
    help='Custom email body text'
)
def send(file, to, subject, from_email, theme, output, provider, body):
    """Generate PDF and send via email (convenience command)"""

    input_file = Path(file)

    # Check if Pop is installed
    if not EmailSender.check_pop_available():
        click.secho("\n✗ Charm Pop is not installed!", fg="red", bold=True)
        click.echo(EmailSender.get_installation_instructions())
        sys.exit(1)

    click.echo(f"\n📄 Processing: {input_file.name}")

    # Load configuration
    barque_config = BarqueConfig.load()

    # Override output directory if specified
    if output:
        barque_config.output_dir = Path(output)

    # Create generator
    generator = PDFGenerator(barque_config)

    # Generate PDF
    with click.progressbar(
        length=1,
        label='Generating PDF',
        show_eta=False
    ) as bar:
        result = generator.generate(
            input_file=input_file,
            theme=theme
        )
        bar.update(1)

    # Check generation success
    if not result.success:
        click.secho(f"\n✗ PDF generation failed: {result.error}", fg="red", bold=True)
        sys.exit(1)

    click.secho("\n✓ PDF generation successful!", fg="green")
    for pdf_file in result.files:
        click.echo(f"  📑 {pdf_file}")

    # Prepare email
    pdf_paths = [Path(f) for f in result.files]

    # Generate default subject if not provided
    if subject is None:
        subject = f"PDF Report: {result.metadata.get('title', input_file.stem)}"

    # Build email configuration
    email_config = EmailConfig(
        provider=EmailProvider.RESEND if provider == 'resend' else EmailProvider.SMTP,
        from_email=from_email
    )

    # Send email
    click.echo(f"\n📧 Sending email to {', '.join(to)}...")

    try:
        sender = EmailSender(email_config)

        email_result = sender.send_pdf_report(
            to=list(to),
            subject=subject,
            pdf_files=pdf_paths,
            body_template=body,
            from_email=from_email
        )

        # Display results
        if email_result.success:
            click.secho("\n✓ Email sent successfully!", fg="green", bold=True)
            click.echo(f"   Sent to: {', '.join(email_result.recipients)}")
        else:
            click.secho(f"\n✗ Failed to send email", fg="red", bold=True)
            if email_result.error:
                click.echo(f"   Error: {email_result.error}")
            sys.exit(1)

    except Exception as e:
        click.secho(f"\n✗ Error: {str(e)}", fg="red", bold=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
