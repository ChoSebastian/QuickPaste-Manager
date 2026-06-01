# QuickPaste Manager — Python 탐색 유틸
$ErrorActionPreference = "Stop"

function Find-PythonExecutable {
    $candidates = @(
        "$PSScriptRoot\..\.venv\Scripts\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:ProgramFiles\Python312\python.exe",
        "$env:ProgramFiles\Python313\python.exe"
    )

    foreach ($path in $candidates) {
        $resolved = Resolve-Path -LiteralPath $path -ErrorAction SilentlyContinue
        if ($resolved) {
            return $resolved.Path
        }
    }

    foreach ($name in @("python", "python3", "py")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }

        # WindowsApps 스텁(Store 리다이렉트) 제외
        if ($cmd.Source -like "*WindowsApps*") { continue }

        return $cmd.Source
    }

    return $null
}

function Ensure-Python {
    $python = Find-PythonExecutable
    if ($python) {
        return $python
    }

    Write-Host ""
    Write-Host "Python 3.12+ 을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host ""
    Write-Host "다음 중 하나로 설치하세요:" -ForegroundColor Yellow
    Write-Host "  1) winget install Python.Python.3.12"
    Write-Host "  2) https://www.python.org/downloads/ (설치 시 'Add python.exe to PATH' 체크)"
    Write-Host ""
    Write-Host "설치 후 PowerShell을 새로 열고 다시 실행하세요:" -ForegroundColor Yellow
    Write-Host "  .\scripts\bootstrap.ps1"
    Write-Host ""
    exit 1
}

function Get-VenvPython {
    param([string]$Root)
    Join-Path $Root ".venv\Scripts\python.exe"
}

function Get-VenvPip {
    param([string]$Root)
    Join-Path $Root ".venv\Scripts\pip.exe"
}
