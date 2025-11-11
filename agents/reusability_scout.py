"""
Reusability Scout Agent
Identifies reusable components from past projects
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent
from utils.archon_rag import get_archon_rag


class ReusabilityScoutAgent(BaseAgent):
    """Finds reusable components and patterns"""

    def __init__(self, claude_api, max_tokens: int = 800):
        super().__init__(claude_api, "Reusability Scout", max_tokens)
        self.archon_rag = get_archon_rag()

    def get_system_prompt(self) -> str:
        return """You are a code reusability specialist.

Your task: Identify opportunities to reuse code, components, and patterns from past projects.

Consider:
- UI components (buttons, forms, dashboards)
- Backend modules (auth, API clients, data models)
- Common patterns (authentication flows, data fetching)
- Configuration templates (Docker, CI/CD)
- Testing utilities

OUTPUT FORMAT (Markdown):
## Reusable Assets

### From Project: [Project Name]
- **Component**: [Component name/path]
- **What it does**: Brief description
- **Reusability**: High/Medium/Low
- **Adaptation needed**: What changes are required
- **Estimated time savings**: X hours

[Repeat for each reusable asset]

## Recommendations
- Which components to reuse as-is
- Which need significant adaptation
- New patterns to establish

Focus on realistic reusability - not everything is worth reusing."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find reusable components

        Args:
            context: Must contain 'idea_description', 'features'

        Returns:
            Dict with reusable_assets (markdown)
        """
        idea = context.get('idea_description', '')
        features = context.get('features', '')

        # Try to query Archon RAG if enabled
        similar_projects = []
        if self.archon_rag.is_enabled():
            similar_projects = self.archon_rag.search_similar_projects(idea)

        archon_context = ""
        if similar_projects:
            archon_context = "\n\nSIMILAR PROJECTS IN ARCHON:\n"
            for proj in similar_projects:
                archon_context += f"- {proj.get('title')}: {proj.get('description')}\n"
        else:
            archon_context = "\n\nNOTE: No Archon integration available or no similar projects found."

        user_message = f"""Identify reusable components for this project:

PROJECT IDEA:
{idea}

PLANNED FEATURES:
{features}
{archon_context}

Identify reusable assets following the format.
Be realistic about what can be reused."""

        response = await self.execute(user_message)

        return {
            "reusable_assets": response,
            "agent_name": self.name,
            "similar_projects": similar_projects,
            "status": "completed"
        }
