#!/usr/bin/env python3
"""
Generic script to create Jira epics and user stories from markdown files.

Usage:
    python create_jira_issues.py [options]

Environment Variables:
    JIRA_URL: Jira server URL (default: http://localhost:8080)
    JIRA_PAT: Jira Personal Access Token (required)
    JIRA_PROJECT_KEY: Jira project key (default: MEET1)
    EPICS_DIR: Directory containing epic markdown files (default: ./epics)

Example:
    export JIRA_URL="https://jira.example.com"
    export JIRA_PAT="your-pat-token"
    export JIRA_PROJECT_KEY="MYPROJ"
    python create_jira_issues.py
"""

import os
import re
import json
import sys
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configuration - can be overridden via environment variables or command-line arguments
JIRA_URL = os.getenv("JIRA_URL", "http://localhost:8080")
JIRA_PAT = os.getenv("JIRA_PAT", "")  # Add your Jira personal access token here
PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "MEET1")  # Default to MEET1, override with env var
EPICS_DIR = os.getenv("EPICS_DIR", "./epics")


@dataclass
class Epic:
    """Represents a Jira epic"""
    id: str
    title: str
    priority: str
    description: str
    business_goal: str
    success_criteria: List[str]
    user_stories: List['UserStory'] = None
    jira_key: Optional[str] = None

    def __post_init__(self):
        if self.user_stories is None:
            self.user_stories = []


@dataclass
class UserStory:
    """Represents a Jira user story"""
    id: str
    title: str
    priority: str
    story_points: int
    description: str
    acceptance_criteria: List[str]
    epic_id: str
    jira_key: Optional[str] = None


class JiraIssueCreator:
    def __init__(self, jira_url: str, pat: str, project_key: str):
        self.jira_url = jira_url.rstrip('/')
        self.pat = pat
        self.project_key = project_key
        self.session = requests.Session()
        self._setup_auth()
        self.epic_issue_map = {}  # Maps epic_id to JIRA epic key
        self.created_issues = []

    def _setup_auth(self):
        """Setup auth with PAT token"""
        # For local Jira, use Bearer token format directly
        self.session.headers.update({
            "Authorization": f"Bearer {self.pat}",
            "Content-Type": "application/json"
        })

    def test_connection(self) -> bool:
        """Test connection to Jira"""
        try:
            response = self.session.get(f"{self.jira_url}/rest/api/2/myself")
            if response.status_code == 200:
                print(f"✓ Connected to Jira as: {response.json().get('displayName')}")
                return True
            else:
                print(f"✗ Failed to connect: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def create_epic(self, epic: Epic) -> Optional[str]:
        """Create an epic in Jira"""
        # Map priority
        priority_map = {
            "P0": "Highest",
            "P1": "High",
            "P2": "Medium",
            "P3": "Low"
        }

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Epic"},
                "summary": epic.title,
                "description": f"{epic.description}\n\nBusiness Goal: {epic.business_goal}",
                "customfield_10103": epic.title,  # Epic Name (required in Jira)
                "priority": {"name": priority_map.get(epic.priority, "Medium")},
                "labels": ["epic", epic.id]
            }
        }

        try:
            response = self.session.post(
                f"{self.jira_url}/rest/api/2/issue",
                json=payload
            )
            if response.status_code in [200, 201]:
                issue_key = response.json()['key']
                epic.jira_key = issue_key
                self.epic_issue_map[epic.id] = issue_key
                self.created_issues.append({
                    "type": "Epic",
                    "id": epic.id,
                    "title": epic.title,
                    "jira_key": issue_key
                })
                print(f"  ✓ Created Epic: {issue_key} - {epic.title}")
                return issue_key
            else:
                print(f"  ✗ Failed to create epic: {response.status_code}")
                print(f"    Response: {response.text}")
                return None
        except Exception as e:
            print(f"  ✗ Error creating epic: {e}")
            return None

    def create_user_story(self, story: UserStory, epic_key: str) -> Optional[str]:
        """Create a user story in Jira"""
        priority_map = {
            "P0": "Highest",
            "P1": "High",
            "P2": "Medium",
            "P3": "Low"
        }

        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "issuetype": {"name": "Story"},
                "summary": story.title,
                "description": story.description,
                "priority": {"name": priority_map.get(story.priority, "Medium")},
                "customfield_10101": epic_key,   # Epic Link
                "labels": ["user-story", story.id]
            }
        }

        try:
            response = self.session.post(
                f"{self.jira_url}/rest/api/2/issue",
                json=payload
            )
            if response.status_code in [200, 201]:
                issue_key = response.json()['key']
                story.jira_key = issue_key
                self.created_issues.append({
                    "type": "User Story",
                    "id": story.id,
                    "title": story.title,
                    "jira_key": issue_key,
                    "epic": epic_key,
                    "story_points": story.story_points
                })
                print(f"    ✓ Created Story: {issue_key} - {story.title} ({story.story_points} pts)")
                return issue_key
            else:
                print(f"    ✗ Failed to create story: {response.status_code}")
                print(f"      Response: {response.text}")
                return None
        except Exception as e:
            print(f"    ✗ Error creating story: {e}")
            return None


class MarkdownParser:
    """Parse epic and user story markdown files"""

    @staticmethod
    def extract_field(content: str, field_name: str) -> Optional[str]:
        """Extract field value from markdown"""
        pattern = rf"\*\*{field_name}:\*\*\s*(.+?)(?=\n\*\*|\n---|\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    @staticmethod
    def extract_list_items(content: str, section_header: str) -> List[str]:
        """Extract list items from markdown section"""
        pattern = rf"## {section_header}.*?\n((?:- .*\n?)+)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            items = re.findall(r"- \[[ x]\]\s*(.+)", match.group(1))
            return items if items else []
        return []

    @staticmethod
    def parse_epic(file_path: str) -> Optional[Epic]:
        """Parse an epic markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract epic ID from filename or content
        epic_id = MarkdownParser.extract_field(content, "Epic ID")
        if not epic_id:
            return None

        title_match = re.search(r"# Epic: (.+)", content)
        title = title_match.group(1) if title_match else "Unknown"

        priority = MarkdownParser.extract_field(content, "Priority") or "P1"
        description = MarkdownParser.extract_field(content, "Business Goal") or ""
        business_goal = description

        success_criteria = MarkdownParser.extract_list_items(content, "Success Criteria")

        return Epic(
            id=epic_id,
            title=title,
            priority=priority,
            description=title,
            business_goal=business_goal,
            success_criteria=success_criteria
        )

    @staticmethod
    def parse_user_story(file_path: str, epic_id: str) -> Optional[UserStory]:
        """Parse a user story markdown file"""
        with open(file_path, 'r') as f:
            content = f.read()

        # Extract story ID
        story_id = MarkdownParser.extract_field(content, "Story ID")
        if not story_id:
            return None

        title_match = re.search(r"# User Story: (.+)", content)
        title = title_match.group(1) if title_match else "Unknown"

        priority = MarkdownParser.extract_field(content, "Priority") or "P1"
        
        points_str = MarkdownParser.extract_field(content, "Story Points")
        story_points = int(points_str) if points_str and points_str.isdigit() else 5

        # Build description from user story section
        user_story_match = re.search(r"## User Story\n\n(.+?)\n---", content, re.DOTALL)
        description = user_story_match.group(1).strip() if user_story_match else title

        acceptance_criteria = MarkdownParser.extract_list_items(content, "Acceptance Criteria")

        return UserStory(
            id=story_id,
            title=title,
            priority=priority,
            story_points=story_points,
            description=description,
            acceptance_criteria=acceptance_criteria,
            epic_id=epic_id
        )


def load_epics_and_stories(epics_dir: str = EPICS_DIR) -> List[Epic]:
    """Load all epics and their user stories from markdown files
    
    Args:
        epics_dir: Directory containing epic subdirectories
        
    Returns:
        List of Epic objects with their user stories
    """
    epics = []
    
    epics_path = Path(epics_dir)
    if not epics_path.exists():
        print(f"Error: Epics directory not found: {epics_dir}")
        return epics

    # Iterate through epic directories
    for epic_dir in sorted(epics_path.iterdir()):
        if not epic_dir.is_dir():
            continue

        epic_file = epic_dir / "epic.md"
        if not epic_file.exists():
            continue

        # Parse epic
        epic = MarkdownParser.parse_epic(str(epic_file))
        if not epic:
            continue

        print(f"Loaded Epic: {epic.id} - {epic.title}")

        # Parse user stories for this epic - support both MEET1-X-Y and US-X-Y naming patterns
        story_patterns = ["MEET1-*.md", "US-*.md"]
        for pattern in story_patterns:
            for story_file in sorted(epic_dir.glob(pattern)):
                # Skip epic.md files
                if story_file.name == "epic.md":
                    continue
                story = MarkdownParser.parse_user_story(str(story_file), epic.id)
                if story and not any(s.id == story.id for s in epic.user_stories):
                    epic.user_stories.append(story)
                    print(f"  - Loaded Story: {story.id} - {story.title}")

        epics.append(epic)

    return epics


def main():
    """Main execution"""
    print("=" * 80)
    print("Generic Jira Issue Creator - Epics & User Stories")
    print("=" * 80)
    print()

    # Display configuration
    print("Configuration:")
    print(f"  JIRA_URL: {JIRA_URL}")
    print(f"  JIRA_PROJECT_KEY: {PROJECT_KEY}")
    print(f"  EPICS_DIR: {EPICS_DIR}")
    print(f"  JIRA_PAT: {'***' if JIRA_PAT else 'NOT SET (required)'}")
    print()

    # Validate configuration
    if not JIRA_PAT:
        print("Error: JIRA_PAT environment variable is not set.")
        print("Please set your Jira Personal Access Token:")
        print("  export JIRA_PAT='your-token-here'")
        return

    # Initialize creator
    creator = JiraIssueCreator(JIRA_URL, JIRA_PAT, PROJECT_KEY)

    # Test connection
    print("Testing Jira connection...")
    if not creator.test_connection():
        print("Failed to connect to Jira. Exiting.")
        return
    print()

    # Load epics and stories
    print("Loading epics and user stories from markdown files...")
    epics = load_epics_and_stories(EPICS_DIR)
    if not epics:
        print("No epics found. Exiting.")
        return
    print(f"Loaded {len(epics)} epics with {sum(len(e.user_stories) for e in epics)} user stories")
    print()

    # Create issues
    print("Creating Jira issues...")
    print("-" * 80)

    for epic in epics:
        print(f"\nCreating Epic: {epic.id}")
        epic_key = creator.create_epic(epic)

        if epic_key:
            for story in epic.user_stories:
                creator.create_user_story(story, epic_key)

    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total issues created: {len(creator.created_issues)}")
    print()

    # Group by type
    epics_created = [i for i in creator.created_issues if i['type'] == 'Epic']
    stories_created = [i for i in creator.created_issues if i['type'] == 'User Story']

    print(f"Epics: {len(epics_created)}")
    for epic in epics_created:
        print(f"  - {epic['jira_key']}: {epic['title']}")

    print(f"\nUser Stories: {len(stories_created)}")
    for story in stories_created:
        print(f"  - {story['jira_key']}: {story['title']} ({story['story_points']} pts) [Epic: {story['epic']}]")

    # Save report
    report_dir = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(report_dir, f"jira_creation_report_{PROJECT_KEY}.json")
    with open(report_file, 'w') as f:
        json.dump(creator.created_issues, f, indent=2)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generic Jira Issue Creator - Creates epics and user stories from markdown files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  JIRA_URL: Jira server URL (default: http://localhost:8080)
  JIRA_PAT: Jira Personal Access Token (REQUIRED)
  JIRA_PROJECT_KEY: Jira project key (default: MEET1)
  EPICS_DIR: Directory containing epic markdown files

Example:
  export JIRA_URL="https://jira.company.com"
  export JIRA_PAT="your-pat-token"
  export JIRA_PROJECT_KEY="PROJ"
  python create_jira_issues.py
        """
    )
    parser.add_argument(
        "--url",
        dest="jira_url",
        help="Override JIRA_URL environment variable"
    )
    parser.add_argument(
        "--pat",
        dest="jira_pat",
        help="Override JIRA_PAT environment variable"
    )
    parser.add_argument(
        "--project",
        dest="project_key",
        help="Override JIRA_PROJECT_KEY environment variable"
    )
    parser.add_argument(
        "--epics-dir",
        dest="epics_dir",
        help="Override EPICS_DIR environment variable"
    )
    
    args = parser.parse_args()
    
    # Override globals with command-line args if provided
    if args.jira_url:
        JIRA_URL = args.jira_url
    if args.jira_pat:
        JIRA_PAT = args.jira_pat
    if args.project_key:
        PROJECT_KEY = args.project_key
    if args.epics_dir:
        EPICS_DIR = args.epics_dir
    
    main()
