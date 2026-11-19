# Runs every Day 12 step that needs Azure: judge on local, cloud test set, judge on cloud,
# cloud security probes, then compare.py. Loads keys from the Day 8 .env into this process only.
#   cd "Day 11\local-rag";  powershell -ExecutionPolicy Bypass -File .\run_azure_steps.ps1
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"

Get-Content "..\..\Day 08\.env" | ForEach-Object {
    if ($_ -match '^\s*(?:export\s+|\$env:)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
        [Environment]::SetEnvironmentVariable($Matches[1], $Matches[2].Trim('"', "'"), "Process")
    }
}
# My Day 8 .env only has OPENAI_API_KEY; the endpoint is the one from the Day 8 notebook
if (-not $env:AZURE_OPENAI_API_KEY) { $env:AZURE_OPENAI_API_KEY = $env:OPENAI_API_KEY }
if (-not $env:AZURE_OPENAI_ENDPOINT) { $env:AZURE_OPENAI_ENDPOINT = "https://ds-ai-internship.openai.azure.com/openai/v1/" }
if (-not $env:AZURE_OPENAI_API_KEY -or -not $env:AZURE_OPENAI_ENDPOINT) { throw "AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT missing in Day 08\.env" }
if (-not $env:AZURE_OPENAI_ENDPOINT.EndsWith("/openai/v1/")) { throw "AZURE_OPENAI_ENDPOINT must end with /openai/v1/" }
$env:JUDGE_BASE_URL = $env:AZURE_OPENAI_ENDPOINT

function Invoke-Step($what, [scriptblock]$cmd) {
    Write-Host "`n=== $what ===" -ForegroundColor Green
    & $cmd
    if ($LASTEXITCODE -ne 0) { throw "$what failed (exit $LASTEXITCODE)" }
}

# 1. Judge on the local outputs (no LLM_* set, nothing local is re-generated)
# Steps whose output file already exists are skipped, so a re-run continues where it stopped.
# Delete the file to redo that step.
if (-not (Test-Path eval_results_local.json)) {
    Invoke-Step "Exercise 3: eval local" { uv run python eval_pipeline.py local }
}

# 2. Cloud generator, same local embeddings and retrieval
$env:LLM_BASE_URL = $env:AZURE_OPENAI_ENDPOINT
$env:LLM_API_KEY = $env:AZURE_OPENAI_API_KEY
$env:LLM_MODEL = "gpt-5.6-luna"
$env:TOKEN_LIMIT_PARAM = "max_completion_tokens"
if (-not (Test-Path pipeline_outputs_cloud.json)) {
    Invoke-Step "Exercise 4: cloud test set" { uv run python pipeline.py --test-set pipeline_outputs_cloud.json }
}
if (-not (Test-Path eval_results_cloud.json)) {
    Invoke-Step "Exercise 4: eval cloud" { uv run python eval_pipeline.py cloud }
}
if (-not (Test-Path security_results_cloud.json)) {
    Invoke-Step "Exercise 5: security cloud" { uv run python security_probe.py cloud }
}
Remove-Item Env:LLM_BASE_URL, Env:LLM_API_KEY, Env:LLM_MODEL, Env:TOKEN_LIMIT_PARAM

# 3. Analysis, outputs saved so the report can cite them
Invoke-Step "compare.py" { uv run python compare.py | Out-File -Encoding utf8 compare_output.md }
Invoke-Step "check local" { uv run python check_eval.py local | Out-File -Encoding utf8 check_local.txt }
Invoke-Step "check cloud" { uv run python check_eval.py cloud | Out-File -Encoding utf8 check_cloud.txt }
Get-Content compare_output.md

# 4. Copy the hand-in files into the Day 12 folder
$dest = "..\..\Day 12\day12_capstone"
Copy-Item eval_pipeline.py, security_probe.py, compare.py, check_eval.py, retrieval_metrics.py, `
    pipeline_outputs_local.json, pipeline_outputs_cloud.json, eval_results_local.json, eval_results_cloud.json, `
    security_results_local.json, security_results_cloud.json, compare_output.md, check_local.txt, check_cloud.txt, `
    retrieval_metrics_local.txt $dest
Write-Host "`nCopied results to $dest. Fill in verdict/note in BOTH security_results files there." -ForegroundColor Green
