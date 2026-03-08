#!/usr/bin/env python3
"""
Simple GitHub Deployment Script
Quick deployment with minimal configuration
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if git is initialized
    if not Path('.git').exists():
        print("❌ Git repository not initialized. Run: git init")
        return False
    
    # Check if GitHub CLI is installed
    success, _ = run_command("gh --version")
    if not success:
        print("❌ GitHub CLI not found. Install from: https://cli.github.com/")
        return False
    
    # Check if authenticated with GitHub
    success, output = run_command("gh auth status")
    if not success or "not logged in" in output.lower():
        print("❌ Not authenticated with GitHub. Run: gh auth login")
        return False
    
    print("✅ All prerequisites met")
    return True

def deploy_to_github():
    """Deploy to GitHub with simple steps"""
    print("🚀 Starting GitHub deployment...")
    
    # Get repo name from environment or default
    repo_name = os.environ.get('GITHUB_REPO_NAME', 'devops-observability-stack')
    
    # Check if repo exists
    success, _ = run_command(f"gh repo view {repo_name}")
    if success:
        print(f"✅ Repository {repo_name} already exists")
        # Just push current changes
        success, output = run_command("git push origin main")
        if success:
            print("✅ Changes pushed to GitHub")
        else:
            print(f"❌ Push failed: {output}")
            return False
    else:
        # Create new repository
        print(f"📝 Creating repository {repo_name}...")
        cmd = f"gh repo create {repo_name} --public --source=. --remote=origin --push"
        success, output = run_command(cmd)
        if not success:
            print(f"❌ Repository creation failed: {output}")
            return False
        print("✅ Repository created and pushed")
    
    # Get repository URL
    success, output = run_command(f"gh repo view {repo_name} --json url")
    if success:
        import json
        repo_data = json.loads(output)
        repo_url = repo_data['url']
        print(f"\n🎉 Deployment successful!")
        print(f"📍 Repository: {repo_url}")
        print(f"🐳 Docker setup: docker-compose up -d")
        print(f"📊 Monitoring: http://localhost:8000")
        print(f"📈 Grafana: http://localhost:3000")
    
    return True

def main():
    """Main deployment function"""
    print("=" * 50)
    print("🚀 SIMPLE GITHUB DEPLOYMENT")
    print("=" * 50)
    
    if not check_prerequisites():
        sys.exit(1)
    
    # Check for uncommitted changes
    success, output = run_command("git status --porcelain")
    if output:
        print("⚠️  You have uncommitted changes:")
        print(output)
        response = input("Commit and continue? (y/N): ")
        if response.lower() == 'y':
            run_command("git add .")
            run_command('git commit -m "Auto-commit before deployment"')
        else:
            print("❌ Please commit changes first")
            sys.exit(1)
    
    if deploy_to_github():
        print("\n✅ Ready to go!")
    else:
        print("\n❌ Deployment failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
