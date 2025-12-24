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
import yaml
import requests
import json

# Load environment variables from .env file
load_dotenv()

from orchestrator import IdeenfinderOrchestrator
from utils.archon_publisher import publish_to_archon as intelligent_publish, extract_project_id

app = typer.Typer(help="Ideenfinder - From Idea to Plan using Agent Factory")
console = Console()


def load_config():
    """Loads configuration from config.yaml."""
    try:
        with open("config.yaml", "r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        console.print("[red]❌ config.yaml not found![/red]")
        console.print("Run [cyan]ideenfinder init[/cyan] to create it.")
        return None

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
        console.print(f"[yellow]Next step:[/yellow] Publish the project to Archon using the 'publish' command.")
        console.print(f"  [cyan]ideenfinder publish {result['output_directory']}/final_project_plan.json[/cyan]")


    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        console.print("\n[dim]Tip: Check your config.yaml and API key[/dim]")
        sys.exit(1)


def publish_to_archon(plan_file: Path):
    """Reads a project plan and all associated markdown files, then sends them to the Archon API."""
    console.print(f"🚀 Publishing project '[cyan]{plan_file}[/cyan]' to Archon with full intelligence...")

    # 1. Load configuration
    config = load_config()
    if not config:
        return

    archon_config = config.get("archon")
    if not archon_config or not archon_config.get("api_url") or not archon_config.get("api_key"):
        console.print("[red]Error: Archon configuration (api_url, api_key) not found in config.yaml.[/red]")
        return

    api_url = archon_config["api_url"]
    api_key = archon_config["api_key"]

    # 2. Check if plan_file is archon-import.json or project-spec.json
    if not plan_file.exists():
        console.print(f"[red]Error: Project plan file '{plan_file}' not found.[/red]")
        return

    # If archon-import.json is provided, look for project-spec.json in same directory
    project_spec_path = plan_file
    if plan_file.name == "archon-import.json":
        project_spec_path = plan_file.parent / "project-spec.json"
        if not project_spec_path.exists():
            console.print(f"[yellow]Warning: project-spec.json not found. Using archon-import.json only (limited data).[/yellow]")
            project_spec_path = plan_file

    # 3. Use intelligent publisher
    try:
        console.print(f"[dim]Using intelligent publisher with project spec: {project_spec_path.name}[/dim]")
        response_data = intelligent_publish(
            project_spec_path=project_spec_path,
            archon_url=api_url,
            archon_api_key=api_key
        )

        project_id = extract_project_id(response_data)
        tasks_created = response_data.get("tasks_created", 0)
        docs_created = response_data.get("documents_created", 0)

        console.print(f"\n[bold green]✅ Success![/bold green]")
        console.print(f"   Project created in Archon with ID: [cyan]{project_id}[/cyan]")
        if docs_created > 0:
            console.print(f"   [green]✓ {docs_created} documents created[/green]")
        if tasks_created > 0:
            console.print(f"   [green]✓ {tasks_created} tasks created from MVP features[/green]")

    except requests.exceptions.HTTPError as e:
        console.print(f"\n[bold red]❌ API Error: {e.response.status_code} {e.response.reason}[/bold red]")
        console.print(f"   [dim]URL: {e.request.url}[/dim]")
        console.print(f"   [dim]Response: {e.response.text}[/dim]")
    except requests.exceptions.RequestException as e:
        console.print(f"\n[bold red]❌ Connection Error:[/bold red] {e}")
    except Exception as e:
        console.print(f"\n[bold red]❌ An unexpected error occurred:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")


@app.command()
def publish(
    plan_file: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the JSON project plan file to publish."
    )
):
    """Publish a generated project plan to Archon."""
    publish_to_archon(plan_file)


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
    console.print("  1. Edit [cyan]config.yaml[/cyan] - Add your Anthropic and Archon credentials")
    console.print("  2. (Optional) Edit [cyan].env[/cyan] - Configure other integrations")
    console.print("  3. Run: [cyan]ideenfinder start[/cyan]\n")


@app.command()
def version():
    """Show version information"""
    console.print("[bold]Ideenfinder[/bold] v1.1.0 (with Archon integration)")
    console.print("Agent Factory for Project Planning\n")


if __name__ == "__main__":
    app()
