param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ReportPath = ""
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Join-Path $Root $RelativePath
}

function Require-File {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    $path = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required file: $RelativePath" }
    return $path
}

function Require-Text {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string[]]$Patterns)
    $text = Get-Content -LiteralPath (Require-File $RelativePath) -Raw
    foreach ($pattern in $Patterns) {
        if (-not $text.Contains($pattern)) { throw "Missing pattern '$pattern' in $RelativePath" }
    }
}

Require-Text "iac\scripts\invoke-live-larger-cell-capk-oidc-preflight.ps1" @(
    "live_larger_cell_capk_oidc_preflight_blocked",
    "live_larger_cell_capk_oidc_no_aggregate_completion_claim",
    "Get-VMHost",
    "sudo -n k3s kubectl",
    "live-larger-cell-capk-oidc-preflight-lib.ps1",
    "provider_portal_oidc_jwks_runtime",
    "provider_portal_oidc_token_runtime",
    "larger_cell_tenant_cluster_shape"
)
Require-Text "iac\scripts\live-larger-cell-capk-oidc-preflight-lib.ps1" @(
    "StrictHostKeyChecking=yes",
    "valueFrom",
    "Resolve-EnvSetting",
    "resolvedValue"
)
Require-Text "docs\live-larger-cell-capk-oidc-evidence.md" @(
    "Live Larger-Cell CAPK/OIDC Evidence",
    "preflight/resource diagnosis",
    "does not claim aggregate completion",
    "live_larger_cell_capk_oidc_preflight_blocked"
)
Require-Text "docs\test-plan.md" @("Live larger-cell CAPK/OIDC preflight", "invoke-live-larger-cell-capk-oidc-preflight.ps1")
Require-Text "docs\operations-log.md" @("Live larger-cell CAPK/OIDC preflight", "invoke-live-larger-cell-capk-oidc-preflight.ps1")

$scriptText = (Get-Content -LiteralPath (Require-File "iac\scripts\invoke-live-larger-cell-capk-oidc-preflight.ps1") -Raw) + "`n" +
    (Get-Content -LiteralPath (Require-File "iac\scripts\live-larger-cell-capk-oidc-preflight-lib.ps1") -Raw)
foreach ($forbidden in @("New-VM", "Remove-VM", "Set-VM", "kubectl apply", "kubectl delete", "kubectl create", "helm upgrade", "k3s-uninstall", "wsl.exe --shutdown", "ShutdownWslOnTimeout")) {
    if ($scriptText -match [regex]::Escape($forbidden)) { throw "Preflight script contains forbidden mutation token: $forbidden" }
}

if ($ReportPath) {
    if (-not (Test-Path -LiteralPath $ReportPath -PathType Leaf)) { throw "Missing report: $ReportPath" }
    $report = Get-Content -LiteralPath $ReportPath -Raw | ConvertFrom-Json
    if ($report.finalAggregateClaim -ne $false) { throw "Preflight report must not claim aggregate completion." }
    if (-not $report.markers) { throw "Preflight report must include markers." }
    if (-not (@($report.markers) -contains "live_larger_cell_capk_oidc_no_aggregate_completion_claim") -and $report.status -eq "blocked") {
        throw "Blocked report must include no aggregate completion marker."
    }
    foreach ($required in @(
        "windows_host_memory",
        "hyperv_management_cell",
        "wsl_bash_kubectl_path",
        "ssh_management_kubectl",
        "management_nodes_ready",
        "cluster_api_capk_providers",
        "larger_cell_tenant_cluster_shape",
        "tenant_kubeconfig_handoff",
        "tenant_control_plane_vmis",
        "provider_portal_oidc_jwks_runtime",
        "provider_portal_oidc_token_runtime"
    )) {
        if (-not (@($report.checks | ForEach-Object { $_.name }) -contains $required)) {
            throw "Report missing required check: $required"
        }
    }
    $memoryCheck = @($report.checks | Where-Object { $_.name -eq "windows_host_memory" } | Select-Object -First 1)
    if ($null -eq $memoryCheck.data.freeMemoryBytes) { throw "Host memory check must include freeMemoryBytes." }
    $wslCheck = @($report.checks | Where-Object { $_.name -eq "wsl_bash_kubectl_path" } | Select-Object -First 1)
    if ($wslCheck.status -eq "blocker" -and -not $wslCheck.data.timedOut) { throw "WSL blocker must include timeout evidence." }
    $handoffCheck = @($report.checks | Where-Object { $_.name -eq "tenant_kubeconfig_handoff" } | Select-Object -First 1)
    if (-not $handoffCheck.data.claims) { throw "Tenant kubeconfig handoff check must include claim facts." }
    $vmiCheck = @($report.checks | Where-Object { $_.name -eq "tenant_control_plane_vmis" } | Select-Object -First 1)
    if ($null -eq $vmiCheck.data.controlPlaneVmis) { throw "Tenant control-plane VMI check must include VMI facts." }
    $portalCheck = @($report.checks | Where-Object { $_.name -eq "provider_portal_oidc_jwks_runtime" } | Select-Object -First 1)
    $portalFacts = @($portalCheck.data.portalIdentity)
    if ($portalCheck.status -eq "pass" -and $portalFacts.Count -eq 0) {
        throw "Provider portal OIDC/JWKS check cannot pass without portalIdentity facts."
    }
    if ($portalFacts.Count -gt 0) {
        $hasEnvShape = @($portalFacts | Where-Object {
            ($_.PSObject.Properties.Name -contains "jwksUriFrom") -and
            ($_.PSObject.Properties.Name -contains "jwksUriResolvedFrom") -and
            ($_.PSObject.Properties.Name -contains "hs256SecretFrom") -and
            ($_.PSObject.Properties.Name -contains "hs256SecretResolvedFrom") -and
            ($_.PSObject.Properties.Name -contains "authModeResolveError")
        }).Count -gt 0
        if (-not $hasEnvShape) { throw "Provider portal runtime facts must include resolved valueFrom-aware env fields." }
        $falseReady = @($portalFacts | Where-Object {
            $_.authMode -eq "oidc-jwks" -and (-not $_.issuer -or -not $_.jwksUri -or -not $_.allowedAlgorithms)
        })
        if ($falseReady.Count -gt 0) { throw "Provider portal cannot be treated as OIDC ready without resolved issuer, jwksUri, and allowedAlgorithms." }
        $readyPortalFacts = @($portalFacts | Where-Object {
            $_.authMode -eq "oidc-jwks" -and
            $_.issuer -and
            $_.jwksUri -and
            $_.allowedAlgorithms -and
            -not $_.hs256SecretPresent -and
            $_.allowedAlgorithms -notmatch "HS256"
        })
        if ($portalCheck.status -eq "pass" -and $readyPortalFacts.Count -eq 0) {
            throw "Provider portal OIDC/JWKS check cannot pass without resolved oidc-jwks facts and no HS256 secret."
        }
        if ($portalCheck.status -eq "blocker" -and $readyPortalFacts.Count -gt 0) {
            throw "Provider portal OIDC/JWKS check is blocker despite ready resolved facts."
        }
    }
    $portalRuntimeCheck = @($report.checks | Where-Object { $_.name -eq "provider_portal_oidc_token_runtime" } | Select-Object -First 1)
    if (@("pass", "blocker") -notcontains $portalRuntimeCheck.status) {
        throw "Provider portal token runtime check must be pass or blocker."
    }
    if (-not $portalRuntimeCheck.data.path) { throw "Provider portal token runtime check must include evidence path." }
    $runtimeEvidencePath = [string]$portalRuntimeCheck.data.path
    if (-not [System.IO.Path]::IsPathRooted($runtimeEvidencePath)) {
        $runtimeEvidencePath = Resolve-RepoPath $runtimeEvidencePath
    }
    if ($portalRuntimeCheck.status -eq "pass" -and -not $portalRuntimeCheck.data.exists) {
        throw "Provider portal token runtime check cannot pass without an existing runtime evidence file."
    }
    if ($portalRuntimeCheck.status -eq "pass" -and -not (Test-Path -LiteralPath $runtimeEvidencePath -PathType Leaf)) {
        throw "Provider portal token runtime check cannot pass without an existing runtime evidence file at data.path."
    }
    if ($portalRuntimeCheck.status -eq "pass" -and -not $portalRuntimeCheck.data.accepted) {
        throw "Provider portal token runtime check cannot pass without accepted runtime evidence."
    }
    if ($portalRuntimeCheck.status -eq "pass" -and -not (@($portalRuntimeCheck.data.markers) -contains "production_capk_oidc_runtime_live_evidence_ok")) {
        throw "Provider portal token runtime check cannot pass without production runtime evidence marker."
    }
    if ($portalRuntimeCheck.status -eq "pass") {
        $canonicalVerifier = Resolve-RepoPath "iac\scripts\verify-production-capk-oidc-runtime-cutover-readiness.ps1"
        $canonicalOutput = & powershell -NoProfile -ExecutionPolicy Bypass -File $canonicalVerifier -EvidenceFile $runtimeEvidencePath 2>&1
        if ($LASTEXITCODE -ne 0 -or (($canonicalOutput | Out-String) -notmatch "production_capk_oidc_runtime_live_evidence_ok")) {
            throw "Provider portal token runtime check cannot pass unless canonical runtime evidence verifier accepts data.path."
        }
    }
    if ($portalRuntimeCheck.status -eq "blocker" -and $portalRuntimeCheck.data.accepted) {
        throw "Provider portal token runtime check is blocker despite accepted runtime evidence."
    }
    Write-Output "live_larger_cell_capk_oidc_preflight_report_ok"
}

Write-Output "live_larger_cell_capk_oidc_preflight_contract_ok"
