#!/usr/bin/env python3
"""
Ideenfinder CLI
Main entry point for the agent factory workflow
"""
import asyncio
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from orchestrator import IdeenfinderOrchestrator

app = typer.Typer(help="Ideenfinder - From Idea to Plan using Agent Factory")
console = Console()


def check_setup():
    """Check if setup is complete"""
    if not Path("config.yaml").exists():
        console.print("[red]❌ config.yaml not found![/red]")
        console.print("\n[yellow]Setup required:[/yellow]")
        console.print("  1. Copy [cyan]config.yaml.example[/cyan] to [cyan]config.yaml[/cyan]")
        console.print("  2. Add your Anthropic API key")
        console.print("  3. Run: [cyan]ideenfinder start[/cyan]\n")
        return False

    return True


@app.command()
def start(
    idea: str = typer.Option(
        None,
        "--idea",
        "-i",
        help="Project idea (or will prompt interactively)"
    ),
    output: str = typer.Option(
        None,
        "--output",
        "-o",
        help="Output directory (default: ./outputs/timestamp)"
    )
):
    """Start the ideenfinder workflow"""

    if not check_setup():
        return

    console.print(Panel(
        "[bold cyan]🚀 Ideenfinder - Agent Factory[/bold cyan]\n\n"
        "Transform your idea into a structured project plan using\n"
        "parallel AI agents and context engineering.",
        style="cyan"
    ))

    # Get idea if not provided
    if not idea:
        console.print("\n[bold]Tell me about your project idea:[/bold]")
        console.print("[dim]Be as detailed or brief as you like. The agents will ask clarifying questions if needed.[/dim]\n")
        idea = Prompt.ask("💡 Your idea")

        if not idea.strip():
            console.print("[red]No idea provided. Exiting.[/red]")
            return

    # Confirm
    console.print(f"\n[bold]Your Idea:[/bold] {idea}\n")

    if not Confirm.ask("Proceed with analysis?", default=True):
        console.print("Cancelled.")
        return

    # Run orchestrator
    try:
        orchestrator = IdeenfinderOrchestrator()
        result = asyncio.run(orchestrator.run_ideation(idea, output))

        console.print("\n[bold green]✅ Success![/bold green]")
        console.print(f"Check outputs in: [cyan]{result['output_directory']}[/cyan]\n")

    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        console.print("\n[dim]Tip: Check your config.yaml and API key[/dim]")
        sys.exit(1)


@app.command()
def init():
    """Initialize configuration files"""
    console.print("[bold]Initializing Ideenfinder...[/bold]\n")

    # Check if config exists
    if Path("config.yaml").exists():
        if not Confirm.ask("config.yaml already exists. Overwrite?", default=False):
            console.print("Cancelled.")
            return

    # Copy example files
    if Path("config.yaml.example").exists():
        import shutil
        shutil.copy("config.yaml.example", "config.yaml")
        console.print("✓ Created [cyan]config.yaml[/cyan]")
    else:
        console.print("[red]❌ config.yaml.example not found[/red]")
        return

    if Path(".env.example").exists():
        import shutil
        if not Path(".env").exists():
            shutil.copy(".env.example", ".env")
            console.print("✓ Created [cyan].env[/cyan]")

    console.print("\n[bold green]Setup complete![/bold green]\n")
    console.print("[yellow]Next steps:[/yellow]")
    console.print("  1. Edit [cyan]config.yaml[/cyan] - Add your Anthropic API key")
    console.print("  2. (Optional) Edit [cyan].env[/cyan] - Configure Archon integration")
    console.print("  3. Run: [cyan]python ideenfinder.py start[/cyan]\n")


@app.command()
def version():
    """Show version information"""
    console.print("[bold]Ideenfinder[/bold] v1.0.0")
    console.print("Agent Factory for Project Planning\n")


if __name__ == "__main__":
    app()
