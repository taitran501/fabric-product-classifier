@echo off
REM Script to push code to GitHub for Streamlit Cloud deployment

echo ========================================
echo  Fabric Product Classifier - Git Push
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo [1/4] Initializing git repository...
    git init
    echo ✅ Git initialized
) else (
    echo [1/4] Git repository already exists
)

echo.
echo [2/4] Adding files to git...
git add app.py requirements.txt README.md .gitignore .streamlit/
if exist QUICK_START.md git add QUICK_START.md
if exist STREAMLIT_CLOUD_SETUP.md git add STREAMLIT_CLOUD_SETUP.md
echo ✅ Files added

echo.
echo [3/4] Checking remote repository...
git remote -v >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No remote repository found!
    echo.
    set /p GITHUB_USER="Enter your GitHub username: "
    set /p REPO_NAME="Enter repository name (default: fabric-product-classifier): "
    if "%REPO_NAME%"=="" set REPO_NAME=fabric-product-classifier
    echo.
    echo Adding remote: https://github.com/%GITHUB_USER%/%REPO_NAME%.git
    git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
    echo ✅ Remote added
) else (
    echo ✅ Remote repository configured
    git remote -v
)

echo.
echo [4/4] Committing and pushing...
git commit -m "Deploy: Fabric Product Classifier to Streamlit Cloud" 2>nul
if errorlevel 1 (
    echo ℹ️  No changes to commit, or already committed
) else (
    echo ✅ Changes committed
)

echo.
echo Pushing to GitHub...
git branch -M main 2>nul
git push -u origin main
if errorlevel 1 (
    echo.
    echo ⚠️  Push failed! Possible reasons:
    echo    - Repository doesn't exist on GitHub yet
    echo    - Authentication required
    echo    - Network issues
    echo.
    echo Please:
    echo 1. Create repository on GitHub first: https://github.com/new
    echo 2. Or check your git credentials
) else (
    echo.
    echo ========================================
    echo  ✅ Successfully pushed to GitHub!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Go to https://share.streamlit.io
    echo 2. Login with GitHub
    echo 3. Click "New app"
    echo 4. Select your repository
    echo 5. Main file: app.py
    echo 6. Click "Deploy"
    echo.
)

pause

