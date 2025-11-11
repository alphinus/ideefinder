"""
Base Agent Class
All specialized agents inherit from this
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.claude_api import ClaudeAPI


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(
        self,
        claude_api: ClaudeAPI,
        name: str,
        max_tokens: Optional[int] = None
    ):
        self.claude = claude_api
        self.name = name
        self.max_tokens = max_tokens or 3000

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with given context

        Args:
            context: Input data for the agent

        Returns:
            Agent's output as dict
        """
        pass

    def _create_user_message(self, context: Dict[str, Any]) -> str:
        """Helper to format context into user message"""
        # Default implementation - can be overridden
        parts = []
        for key, value in context.items():
            parts.append(f"{key.upper()}:\n{value}\n")
        return "\n".join(parts)

    async def execute(self, user_message: str) -> str:
        """Execute agent with custom message"""
        system_prompt = self.get_system_prompt()
        response = self.claude.send_message(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=self.max_tokens
        )
        return response
