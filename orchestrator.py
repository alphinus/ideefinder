"""
Ideenfinder Orchestrator
Coordinates all agents through the 5-phase workflow
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from utils.claude_api import get_claude_api
from utils.parallel_executor import run_agents_parallel
from utils.archon_integration import ArchonIntegration
from agents.research_agent import ResearchAgent
from agents.feature_planner import FeaturePlannerAgent
from agents.techstack_analyzer import TechstackAnalyzerAgent
from agents.reusability_scout import ReusabilityScoutAgent
from agents.validator_agent import ValidatorAgent


class IdeenfinderOrchestrator:
    """Main orchestrator for the ideenfinder workflow"""

    def __init__(self, config_path: str = "config.yaml"):
        self.console = Console()
        self.config_path = config_path
        self.claude_api = get_claude_api(config_path)

        # Initialize agents
        self.research_agent = ResearchAgent(self.claude_api)
        self.feature_planner = FeaturePlannerAgent(self.claude_api)
        self.techstack_analyzer = TechstackAnalyzerAgent(self.claude_api)
        self.reusability_scout = ReusabilityScoutAgent(self.claude_api)
        self.validator = ValidatorAgent(self.claude_api)

        # Initialize Archon integration
        self.archon = ArchonIntegration(config_path)

        # Storage for results
        self.context = {}

    async def run_ideation(
        self,
        idea_input: str,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete ideation workflow

        Args:
            idea_input: User's project idea description
            output_dir: Where to save outputs (default: ./outputs/[timestamp])

        Returns:
            Complete project specification
        """
        self.console.print("\n[bold cyan]🚀 Ideenfinder - Agent Factory Workflow[/bold cyan]\n")

        # Setup output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"./outputs/{timestamp}"

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.context['output_dir'] = output_dir

        # Phase 0: Process idea input
        self.console.print(Panel("[bold]Phase 0: Processing Idea Input[/bold]", style="cyan"))
        self.context['idea_description'] = idea_input
        self.console.print(f"✓ Idea captured: {idea_input[:100]}...\n")

        # Phase 1: Research
        self.console.print(Panel("[bold]Phase 1: Market Research[/bold]", style="cyan"))
        research_result = await self._run_phase_1()
        self.console.print("✓ Research completed\n")

        # Phase 2: Parallel Planning
        self.console.print(Panel("[bold]Phase 2: Parallel Planning (3 agents)[/bold]", style="cyan"))
        planning_results = await self._run_phase_2()
        self.console.print("✓ Planning completed\n")

        # Phase 3: Consolidation
        self.console.print(Panel("[bold]Phase 3: Generating Specification[/bold]", style="cyan"))
        spec = self._generate_specification()
        self.console.print("✓ Specification generated\n")

        # Phase 4: Validation
        self.console.print(Panel("[bold]Phase 4: Validation[/bold]", style="cyan"))
        validation_result = await self._run_phase_4()
        self.console.print("✓ Validation completed\n")

        # Phase 5: Output Generation
        self.console.print(Panel("[bold]Phase 5: Generating Outputs[/bold]", style="cyan"))
        outputs = self._generate_outputs(spec, output_dir)
        self.console.print("✓ Outputs generated\n")

        # Phase 5.5: Auto-Import to Archon (if enabled)
        project_id = None
        if self.archon.enabled:
            self.console.print(Panel("[bold]Auto-Import to Archon[/bold]", style="cyan"))
            project_id = await self.archon.auto_import_project(spec)
            if project_id:
                self.console.print(f"✨ Project auto-imported to Archon: [cyan]{project_id}[/cyan]")
                archon_url = self.archon.api_url.replace('/api/projects', '')
                self.console.print(f"🔗 Open: [link={archon_url}/projects/{project_id}]{archon_url}/projects/{project_id}[/link]\n")
            else:
                self.console.print("⚠️  Auto-import failed - check logs above\n")

        self._display_summary(outputs, output_dir, project_id)

        return {
            "specification": spec,
            "outputs": outputs,
            "output_directory": output_dir,
            "archon_project_id": project_id
        }

    async def _run_phase_1(self) -> Dict[str, Any]:
        """Phase 1: Research Agent"""
        with self.console.status("[bold green]Running Research Agent...") as status:
            result = await self.research_agent.run(self.context)
            self.context.update(result)
            return result

    async def _run_phase_2(self) -> Dict[str, Any]:
        """Phase 2: Parallel Planning Agents"""
        # Define agents to run in parallel
        agents = [
            ("Feature Planner", lambda: self.feature_planner.run(self.context)),
            ("Techstack Analyzer", lambda: self.techstack_analyzer.run(self.context)),
            ("Reusability Scout", lambda: self.reusability_scout.run(self.context))
        ]

        # Run in parallel with progress
        results = await run_agents_parallel(agents, show_progress=True)

        # Update context with all results
        for agent_name, result in results.items():
            self.context.update(result)

        return results

    async def _run_phase_4(self) -> Dict[str, Any]:
        """Phase 4: Validator"""
        with self.console.status("[bold green]Running Validator...") as status:
            result = await self.validator.run(self.context)
            self.context.update(result)
            return result

    def _generate_specification(self) -> Dict[str, Any]:
        """Phase 3: Generate consolidated specification"""
        spec = {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "project": {
                "title": self._extract_title(),
                "description": self.context['idea_description'],
                "type": "web-app",  # Could be enhanced
            },
            "research": {
                "report": self.context.get('research_report', '')
            },
            "features": {
                "plan": self.context.get('features', '')
            },
            "techstack": {
                "recommendations": self.context.get('techstack', '')
            },
            "reusability": {
                "assets": self.context.get('reusable_assets', ''),
                "similar_projects": self.context.get('similar_projects', [])
            },
            "validation": {
                "report": self.context.get('validation_report', '')
            }
        }

        self.context['specification'] = spec
        return spec

    def _generate_outputs(self, spec: Dict[str, Any], output_dir: str) -> Dict[str, str]:
        """Phase 5: Generate output files"""
        outputs = {}

        # 1. Full JSON specification
        json_path = f"{output_dir}/project-spec.json"
        with open(json_path, 'w') as f:
            json.dump(spec, f, indent=2)
        outputs['json'] = json_path

        # 2. Markdown report
        md_path = f"{output_dir}/project-spec.md"
        markdown_content = self._generate_markdown(spec)
        with open(md_path, 'w') as f:
            f.write(markdown_content)
        outputs['markdown'] = md_path

        # 3. Archon import format (simplified for now)
        archon_path = f"{output_dir}/archon-import.json"
        archon_data = self._generate_archon_import(spec)
        with open(archon_path, 'w') as f:
            json.dump(archon_data, f, indent=2)
        outputs['archon'] = archon_path

        return outputs

    def _generate_markdown(self, spec: Dict[str, Any]) -> str:
        """Generate human-readable markdown report"""
        md = f"""# {spec['project']['title']}

**Generated**: {spec['generated_at']}

## Project Overview

{spec['project']['description']}

---

## Market Research

{spec['research']['report']}

---

## Features

{spec['features']['plan']}

---

## Technology Stack

{spec['techstack']['recommendations']}

---

## Reusable Assets

{spec['reusability']['assets']}

---

## Validation Report

{spec['validation']['report']}

---

## Next Steps

1. **Review this specification** - Ensure it matches your vision
2. **Import to Archon** - Use `archon-import.json` for project setup
3. **Start Development** - Use Claude Code to implement features
4. **Iterate** - Adjust based on learnings

---

*Generated by Ideenfinder Agent Factory*
"""
        return md

    def _generate_archon_import(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Archon-compatible import format"""
        # Simplified version - can be enhanced
        return {
            "version": "1.0",
            "project": {
                "title": spec['project']['title'],
                "description": spec['project']['description'],
            },
            "documents": [
                {
                    "title": "Project Specification",
                    "document_type": "spec",
                    "content": {
                        "research": spec['research']['report'],
                        "features": spec['features']['plan'],
                        "techstack": spec['techstack']['recommendations']
                    }
                }
            ],
            "note": "Import this into Archon to create project and tasks"
        }

    def _extract_title(self) -> str:
        """Extract or generate project title from idea"""
        idea = self.context['idea_description']
        # Simple extraction - first sentence or first 50 chars
        if '.' in idea:
            title = idea.split('.')[0]
        else:
            title = idea[:50]
        return title.strip()

    def _display_summary(self, outputs: Dict[str, str], output_dir: str, project_id: Optional[str] = None):
        """Display completion summary"""
        self.console.print("\n[bold green]✨ Project Specification Complete![/bold green]\n")

        self.console.print("[bold]Generated Files:[/bold]")
        for format_type, path in outputs.items():
            self.console.print(f"  • {format_type}: [cyan]{path}[/cyan]")

        self.console.print(f"\n[bold]Output Directory:[/bold] [cyan]{output_dir}[/cyan]")

        if project_id:
            archon_url = self.archon.api_url.replace('/api/projects', '')
            self.console.print(f"\n[bold green]✅ Archon Project:[/bold green] [link={archon_url}/projects/{project_id}]{archon_url}/projects/{project_id}[/link]")

        self.console.print("\n[bold yellow]Next Steps:[/bold yellow]")
        self.console.print("  1. Review: [cyan]less project-spec.md[/cyan]")
        if project_id:
            self.console.print(f"  2. Open Archon project and start working on tasks")
        else:
            self.console.print("  2. Import to Archon: Use [cyan]archon-import.json[/cyan]")
        self.console.print("  3. Start coding with Claude Code!\n")
