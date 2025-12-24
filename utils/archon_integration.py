"""
Archon Integration - Auto-Import Projects
"""
import aiohttp
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class ArchonIntegration:
    """Client for Archon API integration"""

    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.api_url = self.config['archon']['api_url']
        self.api_key = self.config['archon'].get('api_key')
        self.enabled = self.config['archon'].get('enabled', True)

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    async def auto_import_project(self, spec: Dict[str, Any]) -> Optional[str]:
        """
        Import generated project specification into Archon

        Args:
            spec: Project specification from Ideenfinder

        Returns:
            project_id if successful, None otherwise
        """
        if not self.enabled:
            return None

        try:
            # Extract project data
            project_data = {
                "title": spec['project']['title'],
                "description": spec['project']['description'],
                "status": "active"
            }

            # Create project
            project_id = await self._create_project(project_data)

            if project_id:
                # Create specification document
                await self._create_spec_document(project_id, spec)

                # Extract and create tasks from features
                await self._create_tasks_from_features(project_id, spec)

            return project_id

        except Exception as e:
            print(f"⚠️  Auto-import failed: {e}")
            print("📝 You can manually import using archon-import.json")
            return None

    async def _create_project(self, project_data: Dict[str, Any]) -> Optional[str]:
        """Create project in Archon"""
        # Fix API URL - remove /api/projects if present, we'll add it
        base_url = self.api_url.replace('/api/projects', '')
        url = f"{base_url}/api/projects"

        headers = {}
        if self.api_key:
            headers['apikey'] = self.api_key
            headers['Authorization'] = f'Bearer {self.api_key}'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=project_data, headers=headers) as response:
                if response.status == 201:
                    data = await response.json()
                    return data.get('id')
                else:
                    error_text = await response.text()
                    print(f"Failed to create project: {response.status} - {error_text}")
                    return None

    async def _create_spec_document(self, project_id: str, spec: Dict[str, Any]) -> None:
        """Create specification document in Archon"""
        base_url = self.api_url.replace('/api/projects', '')
        url = f"{base_url}/api/projects/{project_id}/docs"

        # Convert spec to markdown
        content = self._spec_to_markdown(spec)

        document_data = {
            "title": "Project Specification",
            "content": content,
            "document_type": "spec"
        }

        headers = {}
        if self.api_key:
            headers['apikey'] = self.api_key
            headers['Authorization'] = f'Bearer {self.api_key}'

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=document_data, headers=headers) as response:
                if response.status != 201:
                    error_text = await response.text()
                    print(f"Failed to create document: {response.status} - {error_text}")

    async def _create_tasks_from_features(self, project_id: str, spec: Dict[str, Any]) -> None:
        """Extract tasks from features and create them in Archon"""
        base_url = self.api_url.replace('/api/projects', '')
        url = f"{base_url}/api/projects/{project_id}/tasks"

        features_text = spec.get('features', {}).get('plan', '')

        # Simple feature extraction (can be enhanced)
        tasks = self._extract_tasks(features_text, spec['project']['title'])

        headers = {}
        if self.api_key:
            headers['apikey'] = self.api_key
            headers['Authorization'] = f'Bearer {self.api_key}'

        async with aiohttp.ClientSession() as session:
            for task in tasks:
                task_data = {
                    "title": task['title'],
                    "description": task['description'],
                    "status": "todo"
                }

                async with session.post(url, json=task_data, headers=headers) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        print(f"Failed to create task '{task['title']}': {response.status}")

    def _spec_to_markdown(self, spec: Dict[str, Any]) -> str:
        """Convert specification to markdown format"""
        md = f"# {spec['project']['title']}\n\n"
        md += f"**Generated:** {spec['generated_at']}\n\n"
        md += f"## Description\n{spec['project']['description']}\n\n"

        # Research
        if 'research' in spec:
            md += f"## Market Research\n{spec['research'].get('report', '')}\n\n"

        # Features
        if 'features' in spec:
            md += f"## Features\n{spec['features'].get('plan', '')}\n\n"

        # Tech Stack
        if 'techstack' in spec:
            md += f"## Tech Stack\n{spec['techstack'].get('recommendations', '')}\n\n"

        # Reusability
        if 'reusability' in spec:
            md += f"## Reusable Assets\n{spec['reusability'].get('assets', '')}\n\n"

        # Validation
        if 'validation' in spec:
            md += f"## Validation\n{spec['validation'].get('report', '')}\n\n"

        return md

    def _extract_tasks(self, features_text: str, project_title: str) -> list:
        """Extract tasks from features text"""
        tasks = []

        # Simple extraction: Look for numbered lists or bullet points
        lines = features_text.split('\n')
        current_task = None

        for line in lines:
            line = line.strip()

            # Check for task indicators (numbered or bulleted lists)
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Extract title (remove numbering/bullets)
                title = line.lstrip('0123456789.-* ').strip()

                if title and len(title) > 3:  # Avoid empty or too short titles
                    if current_task:
                        tasks.append(current_task)

                    current_task = {
                        "title": title[:100],  # Limit length
                        "description": ""
                    }
            elif current_task and line:
                # Add to description
                current_task['description'] += line + '\n'

        # Add last task
        if current_task:
            tasks.append(current_task)

        # If no tasks extracted, create default one
        if not tasks:
            tasks.append({
                "title": f"Implement {project_title}",
                "description": "Implement the project according to the specification"
            })

        return tasks[:10]  # Limit to 10 tasks
