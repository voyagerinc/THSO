#!/bin/bash

# GitHub Setup Script for Excel Template Exporter
# This script helps you set up Git and GitHub integration for the first time

echo "================================================"
echo "GitHub Setup for Excel Template Exporter"
echo "================================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed!"
    echo "Please install git first:"
    echo "  Ubuntu/Debian: sudo apt-get install git"
    echo "  macOS: brew install git"
    echo "  Windows: Download from https://git-scm.com/"
    exit 1
fi

echo "✅ Git is installed: $(git --version)"
echo ""

# Check if already a git repository
if [ -d ".git" ]; then
    echo "✅ This directory is already a git repository"
    echo ""
    
    # Show current remote
    if git remote -v | grep -q "origin"; then
        echo "Current remote repository:"
        git remote -v
    else
        echo "⚠️ No remote repository configured"
        echo ""
        read -p "Enter your GitHub repository URL: " repo_url
        git remote add origin "$repo_url"
        echo "✅ Remote added successfully"
    fi
else
    echo "📁 Initializing new git repository..."
    git init
    echo "✅ Git repository initialized"
    echo ""
    
    # Configure user (if not already set)
    if ! git config user.name &> /dev/null; then
        read -p "Enter your name: " user_name
        git config user.name "$user_name"
    fi
    
    if ! git config user.email &> /dev/null; then
        read -p "Enter your email: " user_email
        git config user.email "$user_email"
    fi
    
    echo ""
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
    echo "✅ Remote repository configured"
    
    # Create .gitignore
    echo "Creating .gitignore file..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# Data files (optional - comment out if you want to track these)
# *.xlsx
# *.xls
# *.csv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
EOF
    echo "✅ .gitignore created"
    
    # Initial commit
    echo ""
    read -p "Create initial commit? (y/n): " create_commit
    if [ "$create_commit" = "y" ] || [ "$create_commit" = "Y" ]; then
        git add .
        git commit -m "Initial commit: Excel Template Exporter with GitHub Sync"
        echo "✅ Initial commit created"
        
        echo ""
        read -p "Push to GitHub? (y/n): " do_push
        if [ "$do_push" = "y" ] || [ "$do_push" = "Y" ]; then
            echo "Pushing to GitHub..."
            git push -u origin main || git push -u origin master
            echo "✅ Pushed to GitHub"
        fi
    fi
fi

echo ""
echo "================================================"
echo "Setup Complete! 🎉"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Open your Streamlit app"
echo "2. Log in with your credentials"
echo "3. Use the GitHub Sync controls in the upper left corner"
echo ""
echo "To upload files to GitHub and sync:"
echo "  git add <files>"
echo "  git commit -m 'Your message'"
echo "  git push"
echo "  Then click 'Pull & Restart' in the app"
echo ""
