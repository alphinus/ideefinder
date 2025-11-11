"""
Feature Planner Agent
Creates MVP feature list with priorities
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent


class FeaturePlannerAgent(BaseAgent):
    """Plans features for MVP with clear priorities"""

    def __init__(self, claude_api, max_tokens: int = 1500):
        super().__init__(claude_api, "Feature Planner", max_tokens)

    def get_system_prompt(self) -> str:
        return """You are a product planning specialist focused on MVP development.

Your expertise:
- Feature prioritization using MoSCoW method
- Scope management and MVP thinking
- User story creation
- Complexity estimation

IMPORTANT: Keep MVPs simple! Aim for 3-5 core features maximum.

OUTPUT FORMAT (Markdown):
## MVP Features

### Feature 1: [Name]
- **Priority**: High/Medium/Low
- **Description**: What it does
- **User Story**: As a [user], I want [action] so that [benefit]
- **Complexity**: Low/Medium/High
- **Estimated Hours**: X hours

[Repeat for each feature]

## Feature Roadmap (Post-MVP)
- Future enhancements to consider
- Feature dependencies

Keep it focused on what's truly essential for launch."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create feature plan

        Args:
            context: Must contain 'idea_description', 'research_report'

        Returns:
            Dict with features (markdown)
        """
        idea = context.get('idea_description', '')
        research = context.get('research_report', '')

        user_message = f"""Create an MVP feature plan for this project:

PROJECT IDEA:
{idea}

MARKET RESEARCH:
{research}

Create a focused MVP feature list following the format."""

        response = await self.execute(user_message)

        return {
            "features": response,
            "agent_name": self.name,
            "status": "completed"
        }
