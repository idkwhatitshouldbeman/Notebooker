@echo off
echo 🚀 Starting Notebooker Deployment...
echo ==================================================

REM Add all changes
echo 🔄 Adding all changes...
git add .
if %errorlevel% neq 0 (
    echo ❌ Failed to add changes
    pause
    exit /b 1
)
echo ✅ Changes added successfully

REM Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo ℹ️  No changes to commit. Repository is up to date.
    pause
    exit /b 0
)

REM Commit changes
echo 🔄 Committing changes...
for /f "tokens=1-6 delims=: " %%a in ("%time%") do set timestamp=%%a:%%b:%%c
git commit -m "Update Notebooker - %date% %timestamp%"
if %errorlevel% neq 0 (
    echo ❌ Failed to commit changes
    pause
    exit /b 1
)
echo ✅ Changes committed successfully

REM Push to GitHub
echo 🔄 Pushing to GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to push to GitHub
    pause
    exit /b 1
)
echo ✅ Pushed to GitHub successfully

echo ==================================================
echo 🎉 Deployment completed successfully!
echo 📁 Repository: https://github.com/idkwhatitshouldbeman/Notebooker.git
echo 🌐 Local server: http://localhost:5000
pause
