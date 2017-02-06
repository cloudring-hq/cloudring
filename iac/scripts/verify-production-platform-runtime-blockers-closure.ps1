param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Join-Path $Root $RelativePath
}

function Require-File {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing required file: $RelativePath"
    }
    return $path
}

function Require-Text {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string[]]$Patterns)
    $text = Get-Content -LiteralPath (Require-File $RelativePath) -Raw
    foreach ($pattern in $Patterns) {
        if (-not $text.Contains($pattern)) {
            throw "Missing pattern '$pattern' in $RelativePath"
        }
    }
}

function Require-NoRegexTree {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string]$Pattern, [Parameter(Mandatory = $true)][string]$Message)
    $path = Resolve-RepoPath $RelativePath
    $files = if (Test-Path -LiteralPath $path -PathType Leaf) { @(Get-Item -LiteralPath $path) } else { @(Get-ChildItem -LiteralPath $path -Recurse -File) }
    foreach ($file in $files) {
        if ((Get-Content -LiteralPath $file.FullName -Raw) -match $Pattern) {
            throw "$Message Offending file: $($file.FullName)"
        }
    }
}

function Invoke-RepoVerifier {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Require-File $RelativePath
    $output = & powershell -NoProfile -ExecutionPolicy Bypass -File $path -Root $Root
    if ($LASTEXITCODE -ne 0) {
        throw "Verifier failed: $RelativePath"
    }
    return @($output)
}

$admission = Invoke-RepoVerifier "iac\scripts\verify-production-scheduler-runtime-admission-seam.ps1"
foreach ($marker in @(
    "provider_scheduler_fixture_parse_ok",
    "production_scheduler_runtime_admission_seam_ok",
    "production_scheduler_runtime_fail_closed_ok",
    "production_scheduler_runtime_no_cluster_access_ok",
    "lab_overlay_no_scheduler_runtime_reference_ok"
)) {
    if ($marker -notin $admission) { throw "Scheduler admission verifier missing marker: $marker" }
}

$quotaReplay = Invoke-RepoVerifier "iac\scripts\verify-production-scheduler-quota-replay-seam.ps1"
foreach ($marker in @(
    "provider_scheduler_quota_replay_fixture_parse_ok",
    "production_scheduler_quota_replay_seam_ok",
    "production_scheduler_quota_replay_fail_closed_ok",
    "production_scheduler_quota_replay_no_cluster_access_ok",
    "lab_overlay_no_scheduler_quota_replay_reference_ok"
)) {
    if ($marker -notin $quotaReplay) { throw "Scheduler quota replay verifier missing marker: $marker" }
}

foreach ($verifier in @(
    "iac\scripts\verify-production-scheduler-replay-operations.ps1",
    "iac\scripts\verify-production-scheduler-workqueue-runtime.ps1",
    "iac\scripts\verify-production-scheduler-observability-slo.ps1",
    "iac\scripts\verify-production-scheduler-runtime-cutover.ps1",
    "iac\scripts\verify-production-scheduler-blueprint.ps1"
)) {
    Invoke-RepoVerifier $verifier | Out-Null
}

Require-Text "docs\platform-runtime-blockers-closure.md" @(
    "Production scheduler runtime replacement",
    "Scheduler-grade transactional quota admission",
    "Full Cluster API + CAPK tenant cluster lifecycle",
    "external OIDC/JWKS provider"
)
Require-Text "docs\provider-roadmap.md" @(
    "verify-production-platform-runtime-blockers-closure.ps1",
    "production scheduler runtime replacement",
    "scheduler-grade transactional quota admission",
    "full Cluster API + CAPK tenant cluster lifecycle",
    "external OIDC/JWKS runtime remains"
)
Require-Text "docs\test-plan.md" @("Production platform runtime blockers closure", "verify-production-platform-runtime-blockers-closure.ps1")
Require-Text "docs\operations-log.md" @("Production platform runtime blockers closure", "verify-production-platform-runtime-blockers-closure.ps1")

Require-File "iac\kubernetes\production-identity\oidc-contract.yaml" | Out-Null
Require-File "gitops\platform-production-identity\kustomization.yaml" | Out-Null
Require-Text "docs\production-identity.md" @("external OIDC", "JWKS", "HS256")
Require-Text "docs\tenant-kubernetes-clusters.md" @("CAPK", "scale", "kubeconfig")

$runtimePattern = "verify-production-platform-runtime-blockers-closure|platform-runtime-blockers-closure|provider-scheduler-quota-replay-canary|provider-scheduler-runtime-canary|platform-production-identity"
Require-NoRegexTree "gitops\platform" $runtimePattern "Shared lab platform overlay must not apply aggregate runtime-blocker closure resources."
Require-NoRegexTree "gitops\cells\lab-hyperv" $runtimePattern "Hyper-V lab overlay must not apply aggregate runtime-blocker closure resources."

$scriptText = Get-Content -LiteralPath (Require-File "iac\scripts\verify-production-platform-runtime-blockers-closure.ps1") -Raw
$forbidden = @(
    ("Invoke-" + "WebRequest"),
    ("Invoke-" + "RestMethod"),
    ("Start-" + "Process"),
    ("New-" + "VM"),
    ("Set-" + "VM"),
    ("Remove-" + "VM"),
    ("do" + "cker"),
    ("pod" + "man")
)
foreach ($pattern in $forbidden) {
    if ($scriptText -match $pattern) {
        throw "Aggregate closure verifier contains forbidden live mutation token: $pattern"
    }
}

Write-Output "production_platform_runtime_blockers_closure_ok"
Write-Output "production_platform_runtime_blockers_fail_closed_ok"
Write-Output "production_platform_runtime_blockers_no_cluster_access_ok"
Write-Output "lab_overlay_no_platform_runtime_blockers_reference_ok"
Write-Output "production_platform_runtime_blockers_gap_accounting_ok"
