@echo off
setlocal
title AURELIUS APEX v9.0 - PUSH TO GITHUB
echo ================================================================================
echo AURELIUS APEX (AQ-OS v9.0) — GITHUB REPOSITORY PUSHER
echo ================================================================================
echo Current Branch: main
echo Ready to link and push to your new GitHub repository.
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/repo-name.git): "

if "%REPO_URL%"=="" (
    echo Error: No repository URL provided.
    pause
    exit /b 1
)

"c:\Users\Nitin Sharma\mingit\cmd\git.exe" remote remove origin 2>nul
"c:\Users\Nitin Sharma\mingit\cmd\git.exe" remote add origin %REPO_URL%
echo.
echo Pushing main branch to origin...
"c:\Users\Nitin Sharma\mingit\cmd\git.exe" push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ================================================================================
    echo SUCCESS: AURELIUS APEX v9.0 has been pushed to GitHub!
    echo ================================================================================
) else (
    echo.
    echo PUSH FAILED. Check your repository URL or credentials.
)
pause
