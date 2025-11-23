#!/bin/bash

# Script to push code to GitHub for Streamlit Cloud deployment

echo "========================================"
echo " Fabric Product Classifier - Git Push"
echo "========================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "[1/4] Initializing git repository..."
    git init
    echo "✅ Git initialized"
else
    echo "[1/4] Git repository already exists"
fi

echo ""
echo "[2/4] Adding files to git..."
git add app.py requirements.txt README.md .gitignore .streamlit/
[ -f QUICK_START.md ] && git add QUICK_START.md
[ -f STREAMLIT_CLOUD_SETUP.md ] && git add STREAMLIT_CLOUD_SETUP.md
echo "✅ Files added"

echo ""
echo "[3/4] Checking remote repository..."
if ! git remote -v | grep -q origin; then
    echo "⚠️  No remote repository found!"
    echo ""
    read -p "Enter your GitHub username: " GITHUB_USER
    read -p "Enter repository name (default: fabric-product-classifier): " REPO_NAME
    REPO_NAME=${REPO_NAME:-fabric-product-classifier}
    echo ""
    echo "Adding remote: https://github.com/$GITHUB_USER/$REPO_NAME.git"
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "✅ Remote added"
else
    echo "✅ Remote repository configured"
    git remote -v
fi

echo ""
echo "[4/4] Committing and pushing..."
if git diff --staged --quiet && git diff --quiet; then
    echo "ℹ️  No changes to commit"
else
    git commit -m "Deploy: Fabric Product Classifier to Streamlit Cloud"
    echo "✅ Changes committed"
fi

echo ""
echo "Pushing to GitHub..."
git branch -M main 2>/dev/null
if git push -u origin main; then
    echo ""
    echo "========================================"
    echo " ✅ Successfully pushed to GitHub!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://share.streamlit.io"
    echo "2. Login with GitHub"
    echo "3. Click 'New app'"
    echo "4. Select your repository"
    echo "5. Main file: app.py"
    echo "6. Click 'Deploy'"
    echo ""
else
    echo ""
    echo "⚠️  Push failed! Possible reasons:"
    echo "   - Repository doesn't exist on GitHub yet"
    echo "   - Authentication required"
    echo "   - Network issues"
    echo ""
    echo "Please:"
    echo "1. Create repository on GitHub first: https://github.com/new"
    echo "2. Or check your git credentials"
    echo ""
fi

