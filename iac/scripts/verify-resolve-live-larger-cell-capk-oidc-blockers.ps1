param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"

if (-not $ReportPath) {
    $ReportPath = Join-Path $Root ".omo\ulw-loop\evidence\resolve-live-larger-cell-capk-oidc-blockers-report.json"
}
if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) {
    throw "Missing G022 report: $ReportPath"
}

$report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
if ($report.status -ne "blocked") { throw "G022 report must remain blocked unless accepted live evidence exists." }
if ($report.finalAggregateClaim -ne $false) { throw "G022 report must not claim aggregate completion." }
if (-not (@($report.markers) -contains "resolve_live_larger_cell_capk_oidc_blocked")) { throw "Missing G022 blocked marker." }
if (-not (@($report.markers) -contains "resolve_live_larger_cell_capk_oidc_no_aggregate_completion_claim")) { throw "Missing G022 no-aggregate marker." }

foreach ($required in @(
    "windows_host_memory",
    "larger_cell_tenant_cluster_shape",
    "tenant_control_plane_vmis",
    "provider_portal_oidc_jwks_runtime",
    "provider_portal_oidc_token_runtime"
)) {
    if (-not (@($report.blockers | ForEach-Object { $_.name }) -contains $required)) {
        throw "G022 report missing blocker: $required"
    }
}

$tenant = $report.facts.tenantCluster
if ($tenant.controlPlaneDesired -ne 1 -or $tenant.controlPlaneCurrent -ne 1 -or $tenant.controlPlaneReady -ne 1) {
    throw "G022 tenant cluster facts must record CP desired/current/ready = 1/1/1."
}
if ($tenant.workerDesired -ne 0 -or $tenant.workerCurrent -ne 0 -or $tenant.workerReady -ne 0) {
    throw "G022 tenant cluster facts must record worker desired/current/ready = 0/0/0."
}
if ($report.facts.tenantControlPlaneVmis.running -ne 1) {
    throw "G022 report must record one running tenant control-plane VMI."
}

$portal = $report.facts.providerPortal
if ($portal.authMode -ne "jwt") { throw "G022 portal auth mode must reflect current jwt blocker." }
if (-not $portal.hs256SecretPresent) { throw "G022 portal must record current HS256 secret blocker." }
if ($portal.jwksUri) { throw "G022 portal JWKS URI must be absent in current blocker report." }
if ($portal.allowedAlgorithms) { throw "G022 portal allowed algorithms must be absent in current blocker report." }

if ($report.facts.host.freeMemoryBytes -ge $report.thresholds.minimumFreeMemoryBytes) {
    throw "G022 host memory blocker cannot be present when free memory meets threshold."
}

Write-Output "resolve_live_larger_cell_capk_oidc_blockers_report_ok"
Write-Output "resolve_live_larger_cell_capk_oidc_no_aggregate_completion_claim"
