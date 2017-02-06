Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")

function Read-Text {
    param([Parameter(Mandatory = $true)][string]$Path)
    $resolved = Join-Path $repoRoot $Path
    if (-not (Test-Path -LiteralPath $resolved)) {
        throw "Missing required file: $Path"
    }
    return Get-Content -LiteralPath $resolved -Raw
}

function Assert-Contains {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Needle,
        [Parameter(Mandatory = $true)][string]$Context
    )
    if (-not $Text.Contains($Needle)) {
        throw "$Context does not contain expected text: $Needle"
    }
}

function Assert-NotContains {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Needle,
        [Parameter(Mandatory = $true)][string]$Context
    )
    if ($Text.Contains($Needle)) {
        throw "$Context unexpectedly contains: $Needle"
    }
}

$requiredFiles = @(
    "iac/kubernetes/production-identity/README.md",
    "iac/kubernetes/production-identity/kustomization.yaml",
    "iac/kubernetes/production-identity/oidc-contract.yaml",
    "iac/kubernetes/production-identity/provider-portal-oidc-patch.yaml",
    "gitops/platform-production-identity/README.md",
    "gitops/platform-production-identity/kustomization.yaml",
    "docs/production-identity.md"
)

foreach ($file in $requiredFiles) {
    [void](Read-Text -Path $file)
}

$contract = Read-Text -Path "iac/kubernetes/production-identity/oidc-contract.yaml"
$patch = Read-Text -Path "iac/kubernetes/production-identity/provider-portal-oidc-patch.yaml"
$overlay = Read-Text -Path "gitops/platform-production-identity/kustomization.yaml"
$docs = Read-Text -Path "docs/production-identity.md"
$platform = Read-Text -Path "gitops/platform/kustomization.yaml"
$labCell = Read-Text -Path "gitops/cells/lab-hyperv/kustomization.yaml"
$portal = Read-Text -Path "iac/kubernetes/provider-portal/portal.yaml"

Assert-Contains -Text $contract -Needle "provider-portal-oidc-contract" -Context "OIDC contract"
Assert-Contains -Text $contract -Needle "REPLACE_WITH_OIDC_ISSUER" -Context "OIDC contract"
Assert-Contains -Text $contract -Needle "jwksUri" -Context "OIDC contract"
Assert-Contains -Text $contract -Needle "requiredSigningAlgorithms" -Context "OIDC contract"
Assert-Contains -Text $contract -Needle "template-only" -Context "OIDC contract"

Assert-Contains -Text $patch -Needle "PORTAL_WRITE_AUTH_MODE" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle "oidc-jwks" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle "PORTAL_JWT_JWKS_URI" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle "PORTAL_JWT_ALLOWED_ALGORITHMS" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle "PORTAL_WRITE_TOKENS_JSON" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle "PORTAL_JWT_HS256_SECRET" -Context "portal OIDC patch"
Assert-Contains -Text $patch -Needle '$patch: delete' -Context "portal OIDC patch"

Assert-Contains -Text $overlay -Needle "../platform" -Context "production identity overlay"
Assert-Contains -Text $overlay -Needle "../../iac/kubernetes/production-identity" -Context "production identity overlay"
Assert-Contains -Text $overlay -Needle "provider-portal-oidc-patch.yaml" -Context "production identity overlay"

Assert-NotContains -Text $platform -Needle "production-identity" -Context "lab platform overlay"
Assert-NotContains -Text $platform -Needle "platform-production-identity" -Context "lab platform overlay"
Assert-NotContains -Text $labCell -Needle "production-identity" -Context "lab cell overlay"
Assert-NotContains -Text $labCell -Needle "platform-production-identity" -Context "lab cell overlay"

Assert-Contains -Text $portal -Needle "PORTAL_WRITE_AUTH_MODE" -Context "lab portal manifest"
Assert-Contains -Text $portal -Needle "oidc-jwks" -Context "lab portal manifest"
Assert-Contains -Text $portal -Needle "PORTAL_JWT_JWKS_URI" -Context "lab portal manifest"
Assert-Contains -Text $portal -Needle "PORTAL_JWT_ALLOWED_ALGORITHMS" -Context "lab portal manifest"
Assert-Contains -Text $portal -Needle "jwt-rs256-private-jwk" -Context "lab portal manifest"
Assert-NotContains -Text $portal -Needle "PORTAL_JWT_HS256_SECRET" -Context "lab portal manifest"
Assert-NotContains -Text $portal -Needle "jwt-hs256-secret" -Context "lab portal manifest"

Assert-Contains -Text $docs -Needle "external OIDC issuer" -Context "production identity docs"
Assert-Contains -Text $docs -Needle "remote JWKS" -Context "production identity docs"
Assert-Contains -Text $docs -Needle "not a claim" -Context "production identity docs"

Write-Output "production_identity_blueprint_ok"
