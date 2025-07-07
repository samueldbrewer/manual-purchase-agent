#!/bin/bash
echo "🚀 Quick GitHub Deploy for Railway"
echo "================================="
echo ""
echo "This script will push your code to GitHub for Railway deployment"
echo ""

# Check if git remote exists
if git remote get-url origin &>/dev/null; then
    echo "✅ Git remote 'origin' already exists"
    git remote get-url origin
else
    echo "📝 Setting up GitHub repository..."
    echo "1. Go to https://github.com/new"
    echo "2. Create a new repository named: manual-purchase-agent"
    echo "3. Don't initialize with README, .gitignore, or license"
    echo ""
    read -p "Enter your GitHub username: " github_username
    echo ""
    
    # Add remote
    git remote add origin "https://github.com/${github_username}/manual-purchase-agent.git"
    echo "✅ Added git remote"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo ""
echo "🎯 Now in Railway:"
echo "1. Click 'Connect Repo'"
echo "2. Select your GitHub account"
echo "3. Choose 'manual-purchase-agent' repository"
echo "4. Railway will auto-deploy!"
echo ""
echo "📝 Don't forget to set environment variables in Railway dashboard!"