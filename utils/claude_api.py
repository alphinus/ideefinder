"""
LLM API wrapper for Ideenfinder
Supports Anthropic Claude and OpenAI Chat Completions
"""
import os
from typing import Optional, Dict, Any, List

import yaml
from anthropic import Anthropic


class ClaudeAPI:
    """Wrapper for LLM providers with conversation management"""

    def __init__(self, api_key: Optional[str] = None, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.provider = self.config.get("llm_provider", "anthropic").lower()

        if self.provider == "openai":
            self._init_openai_client()
        else:
            # Default to Anthropic/Claude for backward compatibility
            self._init_claude_client(api_key)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, "r") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def _init_claude_client(self, api_key: Optional[str]) -> None:
        claude_config = self.config.get("claude", {})
        self.api_key = api_key or claude_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set ANTHROPIC_API_KEY or claude.api_key.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = claude_config.get("model", "claude-sonnet-4")
        self.max_tokens = claude_config.get("max_tokens", 4096)
        self.temperature = claude_config.get("temperature", 0.7)

    def _init_openai_client(self) -> None:
        openai_config = self.config.get("openai", {})
        self.api_key = openai_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY or openai.api_key.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package not installed. Run `pip install openai` to use the OpenAI provider."
            ) from exc

        self.client = OpenAI(api_key=self.api_key)
        self.model = openai_config.get("model", "gpt-4o")
        self.max_tokens = openai_config.get("max_tokens", 4096)
        self.temperature = openai_config.get("temperature", 0.7)

    def send_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Send a single message to the configured provider and get response

        Args:
            system_prompt: System instructions for the model
            user_message: User's message/query
            max_tokens: Override default max tokens
            temperature: Override default temperature

        Returns:
            Provider response text
        """
        if self.provider == "openai":
            return self._send_openai(system_prompt, [{"role": "user", "content": user_message}], max_tokens, temperature)
        return self._send_claude(system_prompt, user_message, max_tokens, temperature)

    def send_with_context(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Send message with conversation history

        Args:
            system_prompt: System instructions
            messages: List of {"role": "user"/"assistant", "content": "..."}
            max_tokens: Override default

        Returns:
            Provider response text
        """
        if self.provider == "openai":
            return self._send_openai(system_prompt, messages, max_tokens, None)
        return self._send_claude(system_prompt, messages, max_tokens, None, use_context=True)

    def _send_claude(
        self,
        system_prompt: str,
        content: Any,
        max_tokens: Optional[int],
        temperature: Optional[float],
        use_context: bool = False,
    ) -> str:
        try:
            messages = content if use_context else [{"role": "user", "content": content}]
            temp = self.temperature if temperature is None else temperature
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temp,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Claude API Error: {str(e)}")

    def _send_openai(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int],
        temperature: Optional[float],
    ) -> str:
        try:
            openai_messages = [{"role": "system", "content": system_prompt}] + messages
            temp = self.temperature if temperature is None else temperature
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temp,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"OpenAI API Error: {str(e)}")


# Global instance (can be imported)
_claude_instance = None

def get_claude_api(config_path: str = "config.yaml") -> ClaudeAPI:
    """Get or create global Claude API instance"""
    global _claude_instance
    if _claude_instance is None:
        _claude_instance = ClaudeAPI(config_path=config_path)
    return _claude_instance
