param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $ReportPath) {
    $ReportPath = Join-Path $Root ".omo\ulw-loop\evidence\actual-capk-oidc-live-cutover-report.json"
}
if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
    throw "Missing G023 report: $ReportPath"
}

$report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
if ($report.finalAggregateClaim -ne $false) { throw "G023 report must not claim aggregate completion." }
if (-not (@($report.markers) -contains "actual_capk_oidc_live_cutover_no_aggregate_completion_claim")) {
    throw "Missing G023 no-aggregate marker."
}

if ($report.status -eq "liveEvidenceReady") {
    if (-not $report.evidenceFile -or -not (Test-Path -LiteralPath $report.evidenceFile -PathType Leaf)) {
        throw "G023 ready report must reference an existing live EvidenceFile."
    }
    $canonicalVerifier = Join-Path $Root "iac\scripts\verify-production-capk-oidc-runtime-cutover-readiness.ps1"
    $canonicalOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $canonicalVerifier -EvidenceFile $report.evidenceFile 2>&1
    if ($LASTEXITCODE -ne 0 -or (($canonicalOutput | Out-String) -notmatch "production_capk_oidc_runtime_live_evidence_ok")) {
        throw "G023 ready report requires canonical live EvidenceFile acceptance."
    }
    Write-Output "actual_capk_oidc_live_cutover_evidence_ready"
    exit 0
}

if ($report.status -ne "blocked") { throw "G023 report must be blocked or liveEvidenceReady." }
if (-not (@($report.markers) -contains "actual_capk_oidc_live_cutover_blocked")) {
    throw "Missing G023 blocked marker."
}

foreach ($required in @(
    "host_memory_for_larger_cell",
    "safe_non_disruptive_remediation",
    "tenant_larger_cell_shape",
    "provider_portal_oidc_runtime"
)) {
    if (-not (@($report.blockers | ForEach-Object { $_.name }) -contains $required)) {
        throw "G023 report missing blocker: $required"
    }
}

if ($report.facts.host.freeMemoryBytes -ge $report.thresholds.minimumFreeMemoryBytes) {
    throw "G023 host memory blocker cannot be present when free memory meets threshold."
}
if ($report.facts.hyperv.requiresManagementVmStopForMemoryRemediation -ne $true) {
    throw "G023 must record that memory remediation requires disruptive management VM changes."
}
if ($report.facts.tenantCluster.controlPlaneReady -ne 1 -or $report.facts.tenantCluster.workerReady -ne 0) {
    throw "G023 tenant shape blocker must record one ready control-plane and zero ready workers."
}
if ($report.facts.providerPortal.authMode -ne "jwt" -or -not $report.facts.providerPortal.hs256SecretPresent) {
    throw "G023 provider portal blocker must record current jwt/HS256 state."
}
if ($report.facts.providerPortal.jwksUri) { throw "G023 provider portal blocker must record absent JWKS URI." }
if ($report.mutationsPerformed.Count -ne 0) { throw "G023 blocked report must not include live mutations." }

Write-Output "actual_capk_oidc_live_cutover_blocked_report_ok"
Write-Output "actual_capk_oidc_live_cutover_no_aggregate_completion_claim"
