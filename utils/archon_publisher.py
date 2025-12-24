"""
Intelligent Archon Publisher
Transforms Ideenfinder outputs into complete, structured Archon projects
"""
import json
import re
from pathlib import Path
from typing import Dict, List, Any
import requests


def parse_features_to_tasks(features_plan: str) -> List[Dict[str, Any]]:
    """Parse feature plan text into structured tasks"""
    tasks = []

    # Split by feature headers (### Feature N:)
    feature_pattern = r'### Feature \d+: (.+?)\n- \*\*Priority\*\*: (.+?)\n- \*\*Description\*\*: (.+?)\n- \*\*User Story\*\*: (.+?)\n- \*\*Complexity\*\*: (.+?)\n- \*\*Estimated Hours\*\*: (\d+) hours'

    matches = re.finditer(feature_pattern, features_plan, re.DOTALL)

    for match in matches:
        title, priority, description, user_story, complexity, hours = match.groups()

        # Map priority to status
        status = "todo" if priority.lower() in ["high", "medium"] else "backlog"

        tasks.append({
            "title": title.strip(),
            "description": f"{description.strip()}\n\n**User Story:** {user_story.strip()}",
            "status": status,
            "priority": priority.lower(),
            "tags": [complexity.lower(), "mvp", "ideenfinder"],
            "estimated_hours": int(hours),
            "metadata": {
                "complexity": complexity.lower(),
                "user_story": user_story.strip(),
                "source": "ideenfinder"
            }
        })

    return tasks


def create_structured_documents(project_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create structured documents from project specification"""
    documents = []

    # 1. Market Research Document
    if "research" in project_spec and project_spec["research"].get("report"):
        documents.append({
            "title": "Market Research & Analysis",
            "document_type": "research",
            "content": {"markdown": project_spec["research"]["report"]},
            "tags": ["research", "market-analysis", "ideenfinder"],
            "metadata": {
                "generated_by": "ideenfinder",
                "section": "research"
            }
        })

    # 2. Features & MVP Plan Document
    if "features" in project_spec and project_spec["features"].get("plan"):
        documents.append({
            "title": "MVP Features & Roadmap",
            "document_type": "spec",
            "content": {"markdown": project_spec["features"]["plan"]},
            "tags": ["features", "mvp", "roadmap", "ideenfinder"],
            "metadata": {
                "generated_by": "ideenfinder",
                "section": "features"
            }
        })

    # 3. Tech Stack Document
    if "techstack" in project_spec and project_spec["techstack"].get("recommendations"):
        documents.append({
            "title": "Technology Stack Recommendations",
            "document_type": "spec",
            "content": {"markdown": project_spec["techstack"]["recommendations"]},
            "tags": ["techstack", "architecture", "ideenfinder"],
            "metadata": {
                "generated_by": "ideenfinder",
                "section": "techstack"
            }
        })

    # 4. Reusability Assets Document
    if "reusability" in project_spec and project_spec["reusability"].get("assets"):
        documents.append({
            "title": "Reusable Components & Assets",
            "document_type": "guide",
            "content": {"markdown": project_spec["reusability"]["assets"]},
            "tags": ["reusability", "components", "ideenfinder"],
            "metadata": {
                "generated_by": "ideenfinder",
                "section": "reusability"
            }
        })

    # 5. Validation Report (if exists)
    if "validation" in project_spec and project_spec["validation"].get("report"):
        documents.append({
            "title": "Validation & Risk Assessment",
            "document_type": "spec",
            "content": {"markdown": project_spec["validation"]["report"]},
            "tags": ["validation", "risks", "ideenfinder"],
            "metadata": {
                "generated_by": "ideenfinder",
                "section": "validation"
            }
        })

    return documents


def extract_project_metadata(project_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Extract metadata from project specification"""
    metadata = {
        "generated_by": "ideenfinder",
        "version": project_spec.get("version", "1.0"),
        "generated_at": project_spec.get("generated_at", ""),
        "project_type": project_spec.get("project", {}).get("type", "web-app")
    }

    # Extract features summary
    if "features" in project_spec:
        features_plan = project_spec["features"].get("plan", "")
        feature_count = len(re.findall(r'### Feature \d+:', features_plan))
        metadata["mvp_features_count"] = feature_count

    return metadata


def publish_to_archon(
    project_spec_path: Path,
    archon_url: str,
    archon_api_key: str = None
) -> Dict[str, Any]:
    """
    Publish a complete Ideenfinder project to Archon

    Args:
        project_spec_path: Path to project-spec.json
        archon_url: Archon API URL
        archon_api_key: Optional API key

    Returns:
        Response from Archon API
    """

    # 1. Load project specification
    with open(project_spec_path, 'r', encoding='utf-8') as f:
        project_spec = json.load(f)

    # 2. Extract project info
    project_info = project_spec.get("project", {})
    title = project_info.get("title", "Untitled Project")
    description = project_info.get("description", "")
    project_type = project_info.get("type", "web-app")

    # 3. Create structured documents
    documents = create_structured_documents(project_spec)

    # 4. Add markdown files from same directory
    source_directory = project_spec_path.parent
    for md_file in source_directory.glob("*.md"):
        if md_file.stem not in ["README", "LICENSE"]:  # Skip common files
            documents.append({
                "title": md_file.stem.replace('_', ' ').replace('-', ' ').title(),
                "document_type": "note",
                "content": {"markdown": md_file.read_text(encoding="utf-8")},
                "tags": ["ideenfinder-generated", "markdown"]
            })

    # 5. Parse features into tasks
    tasks = []
    if "features" in project_spec and project_spec["features"].get("plan"):
        tasks = parse_features_to_tasks(project_spec["features"]["plan"])

    # 6. Extract metadata
    metadata = extract_project_metadata(project_spec)

    # 7. Build project payload (without documents - they're created separately)
    payload = {
        "title": title,
        "description": description
    }

    # 8. Send project to Archon
    headers = {"Content-Type": "application/json"}
    if archon_api_key:
        headers["Authorization"] = f"Bearer {archon_api_key}"

    response = requests.post(archon_url, headers=headers, json=payload)
    response.raise_for_status()

    project_response = response.json()
    project_id = extract_project_id(project_response)

    # 9. Create documents for the project
    if documents and project_id != "unknown":
        base_url = archon_url.rsplit('/', 1)[0]  # Remove '/projects'
        docs_url = f"{base_url}/projects/{project_id}/docs"

        created_docs = []
        for doc_data in documents:
            doc_payload = {
                "document_type": doc_data.get("document_type", "note"),
                "title": doc_data["title"],
                "content": doc_data.get("content", {}),
                "tags": doc_data.get("tags", []),
                "author": "Ideenfinder"
            }

            try:
                doc_response = requests.post(docs_url, headers=headers, json=doc_payload)
                doc_response.raise_for_status()
                created_docs.append(doc_response.json())
            except Exception as e:
                print(f"Warning: Failed to create document '{doc_data['title']}': {str(e)}")

        project_response["documents_created"] = len(created_docs)
        project_response["documents"] = created_docs

    # 10. Create tasks if we have any
    if tasks and project_id != "unknown":
        base_url = archon_url.rsplit('/', 1)[0]  # Remove '/projects'
        tasks_url = f"{base_url}/tasks"

        created_tasks = []
        for task_data in tasks:
            # Add project_id to task
            task_payload = {
                "project_id": project_id,
                "title": task_data["title"],
                "description": task_data["description"],
                "status": task_data["status"],
                "priority": task_data["priority"],
                "assignee": "User",
                "task_order": 0
            }

            try:
                task_response = requests.post(tasks_url, headers=headers, json=task_payload)
                task_response.raise_for_status()
                created_tasks.append(task_response.json())
            except Exception as e:
                # Log error but continue with other tasks
                print(f"Warning: Failed to create task '{task_data['title']}': {str(e)}")

        # Add tasks to response
        project_response["tasks_created"] = len(created_tasks)
        project_response["tasks"] = created_tasks

    return project_response


def extract_project_id(response: Dict[str, Any]) -> str:
    """Extract project ID from Archon response"""
    if "project_id" in response:
        return response["project_id"]
    elif "project" in response and "id" in response["project"]:
        return response["project"]["id"]
    elif "id" in response:
        return response["id"]
    else:
        return "unknown"
