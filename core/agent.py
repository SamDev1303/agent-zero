#!/usr/bin/env python3
"""
Agent Zero - Core Agent Loop
A baby AI that learns from the real world.
"""
import json
import os
from datetime import datetime
from pathlib import Path

class AgentZero:
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.memory_path = workspace / "learnings"
        self.skills_path = workspace / "skills"
        self.projects_path = workspace / "projects"
        
        # Initialize memory
        self.problems = self._load_json("problems.json", [])
        self.solutions = self._load_json("solutions.json", [])
        self.feedback = self._load_json("feedback.json", [])
        
        # Agent state
        self.iteration = 0
        self.born = datetime.now().isoformat()
    
    def _load_json(self, filename, default):
        path = self.memory_path / filename
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return default
    
    def _save_json(self, filename, data):
        path = self.memory_path / filename
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    
    def perceive(self, sources: list[str]) -> list[dict]:
        """
        Scan sources for problems/pain points.
        Sources: reddit, twitter, hackernews, github
        """
        problems_found = []
        
        for source in sources:
            if source == "reddit":
                problems_found.extend(self._scan_reddit())
            elif source == "twitter":
                problems_found.extend(self._scan_twitter())
            elif source == "hackernews":
                problems_found.extend(self._scan_hackernews())
        
        # Store new problems
        for problem in problems_found:
            if not self._problem_exists(problem):
                problem["discovered_at"] = datetime.now().isoformat()
                problem["iteration"] = self.iteration
                self.problems.append(problem)
        
        self._save_json("problems.json", self.problems)
        return problems_found
    
    def _problem_exists(self, problem: dict) -> bool:
        """Check if we've already seen this problem"""
        for p in self.problems:
            if p.get("description") == problem.get("description"):
                return True
        return False
    
    def _scan_reddit(self) -> list[dict]:
        """Scan Reddit for complaints"""
        # TODO: Implement Reddit API scanning
        # Look for keywords: "annoying", "wish", "hate", "frustrated", "why can't"
        return []
    
    def _scan_twitter(self) -> list[dict]:
        """Scan Twitter for complaints"""
        # TODO: Implement Twitter API scanning
        return []
    
    def _scan_hackernews(self) -> list[dict]:
        """Scan HackerNews for problems"""
        # TODO: Implement HN API scanning
        return []
    
    def analyze(self, problem: dict) -> dict:
        """
        Analyze a problem and determine if it's solvable.
        Returns analysis with: solvable, effort, impact, approach
        """
        analysis = {
            "problem_id": problem.get("id"),
            "solvable": False,
            "effort": "unknown",  # low, medium, high
            "impact": "unknown",  # low, medium, high
            "approach": None,
            "existing_solutions": [],
            "analyzed_at": datetime.now().isoformat()
        }
        
        # TODO: Use LLM to analyze
        # - Is this a real problem?
        # - Can code solve it?
        # - What would the solution look like?
        # - Does something already exist?
        
        return analysis
    
    def propose(self, analysis: dict) -> dict:
        """
        Propose a solution based on analysis.
        """
        if not analysis.get("solvable"):
            return None
        
        proposal = {
            "problem_id": analysis.get("problem_id"),
            "name": None,  # Project name
            "description": None,
            "tech_stack": [],
            "mvp_features": [],
            "estimated_hours": 0,
            "proposed_at": datetime.now().isoformat()
        }
        
        # TODO: Use LLM to generate proposal
        
        return proposal
    
    def build(self, proposal: dict) -> dict:
        """
        Build the proposed solution.
        Returns project metadata.
        """
        project = {
            "proposal_id": proposal.get("problem_id"),
            "name": proposal.get("name"),
            "path": None,
            "status": "building",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "deployed_at": None,
            "files_created": []
        }
        
        # Create project directory
        project_path = self.projects_path / proposal.get("name", "unnamed")
        project_path.mkdir(exist_ok=True)
        project["path"] = str(project_path)
        
        # TODO: Use LLM to generate code
        # - Generate files based on proposal
        # - Test the code
        # - Document it
        
        self.solutions.append(project)
        self._save_json("solutions.json", self.solutions)
        
        return project
    
    def learn(self, project: dict, feedback: dict):
        """
        Learn from feedback on a project.
        """
        learning = {
            "project_name": project.get("name"),
            "feedback": feedback,
            "learned_at": datetime.now().isoformat(),
            "insights": []
        }
        
        # TODO: Analyze what worked and didn't
        # - Did people use it?
        # - What was the feedback?
        # - What would I do differently?
        
        self.feedback.append(learning)
        self._save_json("feedback.json", self.feedback)
    
    def run_cycle(self, sources: list[str] = None):
        """
        Run one complete perception-action cycle.
        """
        sources = sources or ["reddit", "twitter", "hackernews"]
        
        print(f"🧒 Agent Zero - Cycle {self.iteration}")
        print("-" * 40)
        
        # 1. Perceive
        print("👁️  Perceiving...")
        problems = self.perceive(sources)
        print(f"   Found {len(problems)} new problems")
        
        # 2. Analyze top problems
        for problem in problems[:3]:  # Focus on top 3
            print(f"🔍 Analyzing: {problem.get('description', 'Unknown')[:50]}...")
            analysis = self.analyze(problem)
            
            if analysis.get("solvable"):
                # 3. Propose
                print("💡 Proposing solution...")
                proposal = self.propose(analysis)
                
                if proposal:
                    # 4. Build
                    print(f"🔨 Building: {proposal.get('name')}...")
                    project = self.build(proposal)
                    print(f"   Created at: {project.get('path')}")
        
        self.iteration += 1
        print(f"\n✅ Cycle {self.iteration} complete")
    
    def status(self):
        """Print agent status"""
        print(f"""
🧒 Agent Zero Status
====================
Born: {self.born}
Iteration: {self.iteration}
Problems discovered: {len(self.problems)}
Solutions built: {len(self.solutions)}
Feedback entries: {len(self.feedback)}
        """)


if __name__ == "__main__":
    workspace = Path(__file__).parent.parent
    agent = AgentZero(workspace)
    agent.status()
