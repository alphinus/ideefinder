"""
Research Agent
Analyzes market, competitors, and opportunities
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Conducts market research and competitor analysis"""

    def __init__(self, claude_api, max_tokens: int = 3000):
        super().__init__(claude_api, "Research Agent", max_tokens)

    def get_system_prompt(self) -> str:
        return """You are a market research specialist with expertise in:
- Market analysis and opportunity identification
- Competitor research and gap analysis
- Technology trends and adoption patterns
- User needs and pain points analysis

Your task is to analyze a project idea and provide comprehensive market insights.

Keep your analysis focused, data-driven (when possible), and actionable.
Aim for 500-800 words total.

OUTPUT FORMAT (Markdown):
## Market Analysis
- Market size and growth potential
- Target audience characteristics
- Key trends relevant to this idea

## Competitor Analysis
- 3-5 key competitors or similar solutions
- What they do well
- Where they fall short (gaps/opportunities)

## Market Opportunity
- Unique positioning for this project
- Potential differentiation points
- Risk factors to consider

Be realistic but optimistic. Focus on actionable insights."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run market research analysis

        Args:
            context: Must contain 'idea_description', optionally 'target_audience'

        Returns:
            Dict with research_report (markdown string)
        """
        idea = context.get('idea_description', '')
        target_audience = context.get('target_audience', 'general users')

        user_message = f"""Analyze this project idea:

PROJECT IDEA:
{idea}

TARGET AUDIENCE:
{target_audience}

Provide comprehensive market research following the format specified."""

        response = await self.execute(user_message)

        return {
            "research_report": response,
            "agent_name": self.name,
            "status": "completed"
        }
