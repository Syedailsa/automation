<#
.SYNOPSIS
    Upload NotebookLM Playwright Agent to GitHub
.DESCRIPTION
    This script uploads all project files to https://github.com/Syedailsa/automation
.NOTES
    Run this script on your Windows machine from:
    C:\Users\UNI-TECH\Downloads\p4 files
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken
)

$ErrorActionPreference = "Stop"

$RepoOwner = "Syedailsa"
$RepoName = "automation"
$Branch = "main"
$SourceDir = "$PSScriptRoot\notebooklm-playwright"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  NotebookLM Playwright - GitHub Uploader   " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verify source directory
if (-not (Test-Path $SourceDir)) {
    Write-Host "ERROR: Source directory not found: $SourceDir" -ForegroundColor Red
    exit 1
}

# Get all files to upload
$files = Get-ChildItem -Path $SourceDir -Recurse -File | 
    Where-Object { 
        $_.FullName -notmatch '__pycache__' -and
        $_.FullName -notmatch '\.pytest_cache' -and
        $_.FullName -notmatch 'venv' -and
        $_.FullName -notmatch '\.git\\' -and
        $_.FullName -notmatch 'storage' -and
        $_.Extension -ne '.pyc'
    }

Write-Host "Found $($files.Count) files to upload" -ForegroundColor Green
Write-Host "Repository: https://github.com/$RepoOwner/$RepoName" -ForegroundColor Yellow
Write-Host ""

$successCount = 0
$failCount = 0
$count = 0

foreach ($file in $files) {
    $count++
    $relativePath = $file.FullName.Substring($SourceDir.Length + 1).Replace('\', '/')
    
    Write-Host "[$count/$($files.Count)] $relativePath" -NoNewline
    
    try {
        $content = [System.IO.File]::ReadAllText($file.FullName)
        $contentBytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $contentBase64 = [Convert]::ToBase64String($contentBytes)
        
        $body = @{
            message = "Add $relativePath"
            content = $contentBase64
            branch = $Branch
        } | ConvertTo-Json
        
        $uri = "https://api.github.com/repos/$RepoOwner/$RepoName/contents/$relativePath"
        
        $response = Invoke-RestMethod -Uri $uri -Method Put -Headers @{
            Authorization = "token $GitHubToken"
            Accept = "application/vnd.github.v3+json"
        } -Body $body -ContentType "application/json; charset=utf-8"
        
        Write-Host " [OK]" -ForegroundColor Green
        $successCount++
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        if ($statusCode -eq 422) {
            Write-Host " [EXISTS]" -ForegroundColor Yellow
            $successCount++
        } else {
            Write-Host " [FAILED: $statusCode]" -ForegroundColor Red
            $failCount++
        }
    }
    
    # Rate limiting - small delay between requests
    Start-Sleep -Milliseconds 100
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Upload Complete!" -ForegroundColor Green
Write-Host "  Success: $successCount files" -ForegroundColor Green
Write-Host "  Failed:  $failCount files" -ForegroundColor Red
Write-Host ""
Write-Host "View your repository:" -ForegroundColor Yellow
Write-Host "  https://github.com/$RepoOwner/$RepoName" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
