param([switch]$VerifyOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
if ($pythonCommand) {
    $portPython = $pythonCommand.Source
} else {
    $portPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
}
if (-not (Test-Path -LiteralPath $portPython)) {
    throw 'Python 3.9+ is required. Install Python and rerun this script.'
}
Push-Location -LiteralPath $projectRoot
try {
    if (-not $VerifyOnly) {
        & $portPython -u porting/ios/prepare_resources.py
        if ($LASTEXITCODE -ne 0) { throw 'Resource preparation failed.' }
    }
    & $portPython -m unittest discover -s porting/ios/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Resource verification failed.' }
} finally {
    Pop-Location
}
