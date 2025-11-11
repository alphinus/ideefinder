"""
Archon RAG Integration
Queries Archon's knowledge base for similar projects and reusable components
"""
import httpx
from typing import Optional, List, Dict, Any
import yaml


class ArchonRAG:
    """Interface to Archon's RAG system"""

    def __init__(self, api_url: Optional[str] = None, config_path: str = "config.yaml"):
        # Load config
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                self.api_url = api_url or config['archon']['api_url']
                self.enabled = config['archon']['enabled']
        except (FileNotFoundError, KeyError):
            self.api_url = "http://localhost:8000"
            self.enabled = False

        self.client = httpx.Client(timeout=30.0)

    def is_enabled(self) -> bool:
        """Check if Archon integration is enabled"""
        return self.enabled

    def search_similar_projects(
        self,
        query: str,
        match_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for similar projects in Archon

        Args:
            query: Search query (e.g., "trading bot", "diet tracking app")
            match_count: Number of results to return

        Returns:
            List of similar projects with metadata
        """
        if not self.enabled:
            return []

        try:
            # This is a mock implementation
            # In reality, you'd call Archon's API endpoint
            # For now, return empty list (can be enhanced later)
            return []

        except Exception as e:
            print(f"Warning: Archon RAG query failed: {e}")
            return []

    def find_reusable_components(
        self,
        project_type: str,
        features: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find reusable components from past projects

        Args:
            project_type: Type of project (web-app, cli-tool, etc.)
            features: List of features needed

        Returns:
            List of reusable components with paths and adaptation notes
        """
        if not self.enabled:
            return []

        try:
            # Mock implementation
            # Would query Archon's knowledge base for code snippets
            return []

        except Exception as e:
            print(f"Warning: Component search failed: {e}")
            return []

    def get_lessons_learned(
        self,
        project_type: str
    ) -> Dict[str, Any]:
        """
        Get lessons learned from similar past projects

        Args:
            project_type: Type of project

        Returns:
            Dict with successes, pitfalls, and recommendations
        """
        if not self.enabled:
            return {
                "successes": [],
                "pitfalls": [],
                "recommendations": []
            }

        try:
            # Mock implementation
            return {
                "successes": [],
                "pitfalls": [],
                "recommendations": []
            }

        except Exception as e:
            print(f"Warning: Lessons learned query failed: {e}")
            return {"successes": [], "pitfalls": [], "recommendations": []}


# Global instance
_archon_instance = None

def get_archon_rag(config_path: str = "config.yaml") -> ArchonRAG:
    """Get or create global Archon RAG instance"""
    global _archon_instance
    if _archon_instance is None:
        _archon_instance = ArchonRAG(config_path=config_path)
    return _archon_instance
