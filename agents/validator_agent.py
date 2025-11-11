"""
Validator Agent
Validates project specification for completeness and realism
"""
from typing import Dict, Any
from agents.base_agent import BaseAgent


class ValidatorAgent(BaseAgent):
    """Validates project specs and provides quality assessment"""

    def __init__(self, claude_api, max_tokens: int = 1500):
        super().__init__(claude_api, "Validator", max_tokens)

    def get_system_prompt(self) -> str:
        return """You are a project validation specialist.

Your task: Review a project specification and assess its quality, completeness, and realism.

Evaluate:
- Feature scope (too ambitious? too narrow?)
- Tech stack choices (appropriate? well-justified?)
- Timeline estimates (realistic?)
- Missing critical elements
- Risk factors

OUTPUT FORMAT (Markdown):
## Validation Report

### Overall Assessment
- **Confidence Score**: X/10
- **Risk Level**: Low/Medium/High
- **Completeness**: X%

### Strengths ✅
- What's well-defined
- Good decisions made

### Concerns ⚠️
- Potential issues
- Missing information
- Unrealistic expectations

### Recommendations
- What to add/change
- Risk mitigation strategies
- Timeline adjustments (if needed)

### Missing Elements
- Critical gaps in specification
- Additional considerations needed

Be constructive but honest. Flag real issues."""

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate project specification

        Args:
            context: Complete project context (all previous outputs)

        Returns:
            Dict with validation_report (markdown)
        """
        spec_summary = f"""
IDEA: {context.get('idea_description', '')}

RESEARCH: {context.get('research_report', '')[:500]}...

FEATURES: {context.get('features', '')[:500]}...

TECHSTACK: {context.get('techstack', '')[:500]}...

REUSABILITY: {context.get('reusable_assets', '')[:500]}...
"""

        user_message = f"""Validate this project specification:

{spec_summary}

Provide a thorough validation report following the format."""

        response = await self.execute(user_message)

        return {
            "validation_report": response,
            "agent_name": self.name,
            "status": "completed"
        }
