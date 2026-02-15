#!/usr/bin/env python3
"""
Agent Zero - Perception Module
Scans the web for problems people are complaining about.
"""
import requests
import json
import re
from datetime import datetime
from typing import List, Dict

# Pain point keywords
PAIN_KEYWORDS = [
    "annoying", "frustrated", "hate", "wish", "tired of",
    "why can't", "broken", "sucks", "waste of time", "manually",
    "tedious", "painful", "nightmare", "impossible", "ridiculous",
    "need a tool", "looking for", "anyone know", "help me"
]

class ProblemScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AgentZero/1.0 (Problem Discovery Bot)"
        })
    
    def scan_reddit(self, subreddits: List[str] = None) -> List[Dict]:
        """
        Scan Reddit for complaints and pain points.
        Uses Reddit JSON API (no auth required for public data).
        """
        subreddits = subreddits or [
            "webdev", "programming", "startups", "SaaS",
            "Entrepreneur", "smallbusiness", "automation"
        ]
        
        problems = []
        
        for sub in subreddits:
            try:
                # Get recent posts
                url = f"https://www.reddit.com/r/{sub}/new.json?limit=50"
                resp = self.session.get(url, timeout=10)
                
                if resp.status_code != 200:
                    continue
                
                data = resp.json()
                posts = data.get("data", {}).get("children", [])
                
                for post in posts:
                    post_data = post.get("data", {})
                    title = post_data.get("title", "")
                    selftext = post_data.get("selftext", "")
                    content = f"{title} {selftext}".lower()
                    
                    # Check for pain keywords
                    if self._has_pain_keywords(content):
                        problems.append({
                            "source": "reddit",
                            "subreddit": sub,
                            "title": title,
                            "description": selftext[:500] if selftext else title,
                            "url": f"https://reddit.com{post_data.get('permalink', '')}",
                            "upvotes": post_data.get("ups", 0),
                            "comments": post_data.get("num_comments", 0),
                            "discovered_at": datetime.now().isoformat()
                        })
            
            except Exception as e:
                print(f"Error scanning r/{sub}: {e}")
        
        return problems
    
    def scan_hackernews(self, story_type: str = "new") -> List[Dict]:
        """
        Scan HackerNews for problems.
        Look at Ask HN, Show HN comments, and discussions.
        """
        problems = []
        
        try:
            # Get story IDs
            url = f"https://hacker-news.firebaseio.com/v0/{story_type}stories.json"
            resp = self.session.get(url, timeout=10)
            story_ids = resp.json()[:30]  # Top 30
            
            for story_id in story_ids:
                try:
                    item_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                    item = self.session.get(item_url, timeout=5).json()
                    
                    if not item:
                        continue
                    
                    title = item.get("title", "")
                    text = item.get("text", "")
                    content = f"{title} {text}".lower()
                    
                    # Look for Ask HN or pain keywords
                    if "ask hn" in title.lower() or self._has_pain_keywords(content):
                        problems.append({
                            "source": "hackernews",
                            "title": title,
                            "description": text[:500] if text else title,
                            "url": f"https://news.ycombinator.com/item?id={story_id}",
                            "score": item.get("score", 0),
                            "comments": item.get("descendants", 0),
                            "discovered_at": datetime.now().isoformat()
                        })
                
                except Exception:
                    continue
        
        except Exception as e:
            print(f"Error scanning HackerNews: {e}")
        
        return problems
    
    def scan_twitter_search(self, query: str = None) -> List[Dict]:
        """
        Search Twitter for complaints.
        Note: Requires API credentials - implement with tweepy if needed.
        """
        # TODO: Implement with X API
        # Search for: "I wish", "why can't", "so annoying", etc.
        return []
    
    def scan_github_issues(self, repos: List[str] = None) -> List[Dict]:
        """
        Scan popular GitHub repos for common issues.
        """
        repos = repos or [
            "vercel/next.js",
            "facebook/react",
            "vitejs/vite"
        ]
        
        problems = []
        
        for repo in repos:
            try:
                url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=30"
                resp = self.session.get(url, timeout=10)
                
                if resp.status_code != 200:
                    continue
                
                issues = resp.json()
                
                for issue in issues:
                    title = issue.get("title", "")
                    body = issue.get("body", "") or ""
                    content = f"{title} {body}".lower()
                    
                    # Look for bug reports or feature requests with pain
                    if self._has_pain_keywords(content):
                        problems.append({
                            "source": "github",
                            "repo": repo,
                            "title": title,
                            "description": body[:500],
                            "url": issue.get("html_url"),
                            "reactions": issue.get("reactions", {}).get("total_count", 0),
                            "comments": issue.get("comments", 0),
                            "discovered_at": datetime.now().isoformat()
                        })
            
            except Exception as e:
                print(f"Error scanning {repo}: {e}")
        
        return problems
    
    def _has_pain_keywords(self, text: str) -> bool:
        """Check if text contains pain point keywords"""
        text_lower = text.lower()
        return any(kw in text_lower for kw in PAIN_KEYWORDS)
    
    def rank_problems(self, problems: List[Dict]) -> List[Dict]:
        """
        Rank problems by potential value.
        Higher score = more people affected + higher engagement.
        """
        for problem in problems:
            score = 0
            
            # Engagement signals
            score += problem.get("upvotes", 0) * 2
            score += problem.get("score", 0) * 2
            score += problem.get("comments", 0) * 3
            score += problem.get("reactions", 0) * 5
            
            # Source weight
            if problem.get("source") == "hackernews":
                score *= 1.5  # HN audience is more technical
            
            problem["rank_score"] = score
        
        return sorted(problems, key=lambda x: x.get("rank_score", 0), reverse=True)


if __name__ == "__main__":
    scanner = ProblemScanner()
    
    print("🔍 Scanning Reddit...")
    reddit_problems = scanner.scan_reddit(["webdev", "programming"])
    print(f"   Found {len(reddit_problems)} problems")
    
    print("🔍 Scanning HackerNews...")
    hn_problems = scanner.scan_hackernews()
    print(f"   Found {len(hn_problems)} problems")
    
    # Combine and rank
    all_problems = reddit_problems + hn_problems
    ranked = scanner.rank_problems(all_problems)
    
    print("\n📊 Top 5 Problems:")
    for i, p in enumerate(ranked[:5], 1):
        print(f"{i}. [{p['source']}] {p['title'][:60]}...")
        print(f"   Score: {p.get('rank_score', 0)} | URL: {p.get('url', 'N/A')}")
