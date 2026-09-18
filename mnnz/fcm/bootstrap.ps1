param(
    [string]$Venv = ".venv-mnnz-fcm",
    [string]$Python = "3.13"
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repo

uv venv $Venv --python $Python
$pythonExe = Join-Path $repo "$Venv\Scripts\python.exe"

uv pip install --python $pythonExe -e ".[litellm]" "chromadb>=1.1.1" "transformers<5"

& $pythonExe -c "import parlant, transformers, chromadb; print('PARLANT_IMPORT_OK'); print('transformers='+transformers.__version__); print('chromadb='+chromadb.__version__)"
