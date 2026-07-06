@echo off
echo ============================================
echo   NotebookLM Playwright - GitHub Uploader
echo ============================================
echo.
echo To upload files to GitHub, you need a Personal Access Token.
echo.
echo Steps:
echo 1. Go to: https://github.com/settings/tokens
echo 2. Click "Generate new token (classic)"
echo 3. Select "repo" scope
echo 4. Copy the token
echo.
echo Then run this command:
echo.
echo   powershell -ExecutionPolicy Bypass -File upload_to_github.ps1 -GitHubToken YOUR_TOKEN_HERE
echo.
echo Or use Git commands below:
echo.
echo   cd "%~dp0notebooklm-playwright"
echo   git init
echo   git branch -m main
echo   git remote add origin https://github.com/Syedailsa/automation.git
echo   git add .
echo   git commit -m "feat: NotebookLM Playwright Agent"
echo   git push -u origin main
echo.
pause
