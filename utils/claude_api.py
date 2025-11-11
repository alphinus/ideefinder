"""
Claude API Wrapper für Ideenfinder
Handles all interactions with Claude API
"""
import os
from anthropic import Anthropic
from typing import Optional, Dict, Any
import yaml


class ClaudeAPI:
    """Wrapper for Claude API with conversation management"""

    def __init__(self, api_key: Optional[str] = None, config_path: str = "config.yaml"):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Set it in .env or pass to constructor.")

        self.client = Anthropic(api_key=self.api_key)

        # Load config
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.model = config['claude']['model']
                self.max_tokens = config['claude']['max_tokens']
                self.temperature = config['claude']['temperature']
        except FileNotFoundError:
            # Defaults if config not found
            self.model = "claude-sonnet-4"
            self.max_tokens = 4096
            self.temperature = 0.7

    def send_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Send a single message to Claude and get response

        Args:
            system_prompt: System instructions for Claude
            user_message: User's message/query
            max_tokens: Override default max tokens
            temperature: Override default temperature

        Returns:
            Claude's response text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Claude API Error: {str(e)}")

    def send_with_context(
        self,
        system_prompt: str,
        messages: list[Dict[str, str]],
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send message with conversation history

        Args:
            system_prompt: System instructions
            messages: List of {"role": "user"/"assistant", "content": "..."}
            max_tokens: Override default

        Returns:
            Claude's response text
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Claude API Error: {str(e)}")


# Global instance (can be imported)
_claude_instance = None

def get_claude_api(config_path: str = "config.yaml") -> ClaudeAPI:
    """Get or create global Claude API instance"""
    global _claude_instance
    if _claude_instance is None:
        _claude_instance = ClaudeAPI(config_path=config_path)
    return _claude_instance
