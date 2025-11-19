#!/usr/bin/env python3
"""
Script to create Jira epics and user stories from markdown files.
"""

import os
import re
import json
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Configuration
JIRA_URL = "http://localhost:8080"
JIRA_PAT = ""  # Add your Jira personal access token here
PROJECT_KEY = "AID"  # Change this to your project key

EPICS_DIR = "/Users/alexk/Projects/ MeetupDemo/docs/agile/epics"


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


def load_epics_and_stories() -> List[Epic]:
    """Load all epics and their user stories from markdown files"""
    epics = []

    # Iterate through epic directories
    for epic_dir in sorted(Path(EPICS_DIR).iterdir()):
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

        # Parse user stories for this epic
        for story_file in sorted(epic_dir.glob("US-*.md")):
            story = MarkdownParser.parse_user_story(str(story_file), epic.id)
            if story:
                epic.user_stories.append(story)
                print(f"  - Loaded Story: {story.id} - {story.title}")

        epics.append(epic)

    return epics


def main():
    """Main execution"""
    print("=" * 80)
    print("Jira Issue Creator - Premium Customer Notification System")
    print("=" * 80)
    print()

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
    epics = load_epics_and_stories()
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
    report_file = "/Users/alexk/Projects/ MeetupDemo/scripts/jira_creation_report.json"
    with open(report_file, 'w') as f:
        json.dump(creator.created_issues, f, indent=2)
    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
