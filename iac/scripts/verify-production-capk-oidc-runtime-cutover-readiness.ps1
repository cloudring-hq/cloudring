param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$EvidenceFile = ""
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

function Read-Text {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Get-Content -LiteralPath (Require-File $RelativePath) -Raw
}

function Require-Text {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string[]]$Patterns)
    $text = Read-Text $RelativePath
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

function Require-Status {
    param($Object, [Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Expected)
    $cursor = $Object
    foreach ($part in $Path.Split(".")) {
        if ($null -eq $cursor -or -not ($cursor.PSObject.Properties.Name -contains $part)) {
            throw "Missing live evidence path: $Path"
        }
        $cursor = $cursor.$part
    }
    if ($cursor -ne $Expected) {
        throw "Unexpected live evidence status at ${Path}: expected $Expected got $cursor"
    }
}

function Test-LiveEvidence {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "Missing live evidence file: $Path"
    }
    $evidence = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    if (-not $evidence.cellProfile.name) { throw "Live evidence requires cellProfile.name." }
    if ($evidence.cellProfile.managementNodesReady -lt 3) { throw "Live evidence requires at least three Ready management nodes." }
    if (-not $evidence.tenantCluster.claim) { throw "Live evidence requires tenantCluster.claim." }
    if ($evidence.tenantCluster.controlPlaneReplicas -lt 3) { throw "Live evidence requires at least three tenant control-plane replicas." }
    $workerPools = @($evidence.tenantCluster.workerPools)
    if ($workerPools.Count -lt 1) { throw "Live evidence requires at least one tenant worker pool." }
    foreach ($pool in $workerPools) {
        if (-not $pool.name) { throw "Live evidence workerPools entries require names." }
        if ([int]$pool.replicas -lt 1) { throw "Live evidence requires every tenant worker pool to have at least one replica." }
    }
    foreach ($path in @(
        "tenantCluster.scaleProof.status",
        "tenantCluster.upgradeProof.status",
        "tenantCluster.kubeconfigHandoff.status",
        "tenantCluster.antiAffinity.status",
        "tenantCluster.restartReplacement.status",
        "tenantCluster.providerRoutedEndpoint.status"
    )) { Require-Status $evidence $path "passed" }
    Require-Status $evidence "tenantCluster.crossTenantKubeconfig.status" "denied"
    if ([string]$evidence.tenantCluster.providerRoutedEndpoint.endpoint -notmatch "^https://") { throw "Live evidence providerRoutedEndpoint.endpoint must be an HTTPS routed endpoint." }
    if ([string]$evidence.tenantCluster.providerRoutedEndpoint.endpoint -match "REPLACE_WITH_|stale|lab|localhost|127\.0\.0\.1") { throw "Live evidence providerRoutedEndpoint.endpoint must not be stale, lab-local, or placeholder." }
    if ($evidence.identity.mode -ne "oidc-jwks") { throw "Live evidence identity.mode must be oidc-jwks." }
    if ([string]$evidence.identity.issuer -match "REPLACE_WITH_|HS256|lab") { throw "Live evidence issuer must be an external non-placeholder issuer." }
    if ([string]$evidence.identity.jwksUri -match "REPLACE_WITH_") { throw "Live evidence jwksUri must be populated." }
    if ("HS256" -in @($evidence.identity.allowedAlgorithms)) { throw "Live evidence must not allow HS256." }
    if (-not (("RS256" -in @($evidence.identity.allowedAlgorithms)) -or ("ES256" -in @($evidence.identity.allowedAlgorithms)))) { throw "Live evidence must allow RS256 or ES256." }
    if (-not $evidence.identity.groupsClaim -or -not $evidence.identity.namespacesClaim) { throw "Live evidence must include groups and namespaces claims." }
    if ($evidence.identity.labHs256EnvPresent -ne $false) { throw "Live evidence must prove lab HS256 env is absent." }
    Require-Status $evidence "identity.validTenantToken.status" "allowed"
    Require-Status $evidence "identity.crossTenantToken.status" "denied"
    Require-Status $evidence "identity.invalidSignature.status" "denied"
    Require-Status $evidence "identity.expiredToken.status" "denied"
    Write-Output "production_capk_oidc_runtime_cutover_live_evidence_ok"
}

function Test-LiveEvidenceRejects {
    param([Parameter(Mandatory = $true)][string]$Name, [Parameter(Mandatory = $true)]$Evidence)
    $tempPath = Join-Path ([System.IO.Path]::GetTempPath()) ("capk-oidc-negative-" + [System.Guid]::NewGuid().ToString("N") + ".json")
    try {
        $json = $Evidence | ConvertTo-Json -Depth 20
        [System.IO.File]::WriteAllText($tempPath, $json, (New-Object System.Text.UTF8Encoding($false)))
        try {
            Test-LiveEvidence $tempPath | Out-Null
        } catch {
            Write-Output "negative_capk_oidc_${Name}_probe_ok"
            return
        }
        throw "Negative live evidence probe unexpectedly passed: $Name"
    } finally {
        Remove-Item -LiteralPath $tempPath -Force -ErrorAction SilentlyContinue
    }
}

function Test-FailClosedLiveEvidence {
    $badEvidence = [ordered]@{
        cellProfile = [ordered]@{ managementNodesReady = 3 }
        tenantCluster = [ordered]@{
            controlPlaneReplicas = 3
            workerPools = @(
                [ordered]@{ name = "zero"; replicas = 0 },
                [ordered]@{ name = "one"; replicas = 1 }
            )
            scaleProof = [ordered]@{ status = "passed" }
            upgradeProof = [ordered]@{ status = "passed" }
            kubeconfigHandoff = [ordered]@{ status = "passed" }
            antiAffinity = [ordered]@{ status = "passed" }
            restartReplacement = [ordered]@{ status = "passed" }
            providerRoutedEndpoint = [ordered]@{ status = "passed"; endpoint = "https://tenant-a-prod-k8s.example.invalid" }
            crossTenantKubeconfig = [ordered]@{ status = "denied" }
        }
        identity = [ordered]@{
            mode = "oidc-jwks"
            issuer = "https://issuer.example.invalid/realms/provider"
            jwksUri = "https://issuer.example.invalid/realms/provider/protocol/openid-connect/certs"
            allowedAlgorithms = @("RS256")
            groupsClaim = "groups"
            namespacesClaim = "tenant_namespace"
            labHs256EnvPresent = $false
            validTenantToken = [ordered]@{ status = "allowed" }
            crossTenantToken = [ordered]@{ status = "denied" }
            invalidSignature = [ordered]@{ status = "denied" }
            expiredToken = [ordered]@{ status = "denied" }
        }
    }
    Test-LiveEvidenceRejects "missing_required_identity_and_worker_pool" $badEvidence
}

Require-Text "docs\capk-oidc-runtime-cutover-readiness.md" @(
    "Required Larger-Cell Evidence",
    "OIDC/JWKS Runtime Evidence",
    "deterministic self-hosted keys",
    "Offline contract evidence is non-final"
)
Require-Text "iac\kubernetes\production-cell\capk-oidc-runtime-cutover-readiness.yaml" @(
    "capk-larger-cell-and-oidc-jwks-runtime",
    "tenantCluster.controlPlaneReplicas",
    "identity.labHs256EnvPresent",
    "final aggregate completion requires"
)
Require-Text "iac\kubernetes\production-cell\kustomization.yaml" @("capk-oidc-runtime-cutover-readiness.yaml")
Require-Text "docs\provider-roadmap.md" @(
    "verify-production-capk-oidc-runtime-cutover-readiness.ps1",
    "CAPK/OIDC runtime cutover readiness",
    "full Cluster API + CAPK tenant cluster lifecycle",
    "external OIDC/JWKS runtime"
)
Require-Text "docs\test-plan.md" @("CAPK/OIDC runtime cutover readiness", "verify-production-capk-oidc-runtime-cutover-readiness.ps1")
Require-Text "docs\operations-log.md" @("CAPK/OIDC runtime cutover readiness", "verify-production-capk-oidc-runtime-cutover-readiness.ps1")

Require-Text "docs\tenant-kubernetes-clusters.md" @(
    "verify-tenant-cluster-layer.sh",
    "verify-claim-lifecycle.sh",
    "verify-tenant-control-plane-restart.sh",
    "worker replicas at",
    "ControlPlaneReplicaLimitExceeded"
)
Require-Text "docs\production-identity.md" @(
    "external OIDC issuer",
    "remote JWKS",
    "not a claim"
)
Require-Text "iac\kubernetes\production-identity\provider-portal-oidc-patch.yaml" @(
    "PORTAL_WRITE_AUTH_MODE",
    "oidc-jwks",
    "PORTAL_JWT_JWKS_URI",
    "PORTAL_JWT_ALLOWED_ALGORITHMS",
    "PORTAL_WRITE_TOKENS_JSON",
    "PORTAL_JWT_HS256_SECRET",
    '$patch: delete'
)
Require-Text "iac\kubernetes\production-identity\oidc-contract.yaml" @(
    "requiredSigningAlgorithms",
    "RS256,ES256",
    "groupsClaim",
    "namespacesClaim"
)

$runtimePattern = "capk-oidc-runtime-cutover-readiness|verify-production-capk-oidc-runtime-cutover-readiness|provider-portal-oidc-contract|platform-production-identity"
Require-NoRegexTree "gitops\platform" $runtimePattern "Shared lab platform overlay must not apply CAPK/OIDC runtime cutover resources."
Require-NoRegexTree "gitops\cells\lab-hyperv" $runtimePattern "Hyper-V lab overlay must not apply CAPK/OIDC runtime cutover resources."

$scriptText = Get-Content -LiteralPath (Require-File "iac\scripts\verify-production-capk-oidc-runtime-cutover-readiness.ps1") -Raw
$forbidden = @(
    ("kub" + "ectl"),
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
        throw "Readiness verifier contains forbidden live mutation token: $pattern"
    }
}

Write-Output "production_capk_oidc_runtime_cutover_readiness_ok"
Test-FailClosedLiveEvidence
Write-Output "production_capk_oidc_runtime_cutover_fail_closed_ok"
Write-Output "production_capk_oidc_runtime_cutover_no_live_mutation_ok"
Write-Output "lab_overlay_no_capk_oidc_runtime_cutover_reference_ok"

if ($EvidenceFile) {
    Test-LiveEvidence $EvidenceFile
} else {
    Write-Output "production_capk_oidc_runtime_cutover_live_evidence_required"
}
