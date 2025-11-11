"""
Techstack Analyzer Agent
Recommends optimal technology stack
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent


class TechstackAnalyzerAgent(BaseAgent):
    """Analyzes requirements and recommends tech stack"""

    def __init__(self, claude_api, max_tokens: int = 1000):
        super().__init__(claude_api, "Techstack Analyzer", max_tokens)

    def get_system_prompt(self) -> str:
        return """You are a technical architect with expertise in:
- Backend frameworks (FastAPI, Django, Express, etc.)
- Frontend frameworks (React, Next.js, Vue, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Deployment platforms (Docker, Fly.io, Vercel, etc.)
- Testing and CI/CD tools

Make pragmatic recommendations based on:
- Project requirements
- Team experience (if mentioned)
- Scalability needs
- Development speed
- Community support and documentation

OUTPUT FORMAT (Markdown):
## Recommended Tech Stack

### Backend
- **Framework**: [Name]
- **Reasoning**: Why this choice

### Frontend
- **Framework**: [Name]
- **Reasoning**: Why this choice

### Database
- **Choice**: [Name]
- **Reasoning**: Why this choice

### Deployment
- **Platform**: [Name]
- **Reasoning**: Why this choice

### Additional Tools
- Testing: [Framework]
- CI/CD: [Tool]
- Other: [As needed]

## Alternative Options
Brief mention of viable alternatives and trade-offs.

Keep recommendations practical and well-justified."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze and recommend tech stack

        Args:
            context: Must contain 'idea_description', 'features'

        Returns:
            Dict with techstack (markdown)
        """
        idea = context.get('idea_description', '')
        features = context.get('features', '')

        user_message = f"""Recommend a tech stack for this project:

PROJECT IDEA:
{idea}

PLANNED FEATURES:
{features}

Provide tech stack recommendations following the format."""

        response = await self.execute(user_message)

        return {
            "techstack": response,
            "agent_name": self.name,
            "status": "completed"
        }
