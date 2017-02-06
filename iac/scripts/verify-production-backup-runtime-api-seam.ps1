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

function Read-RepoText {
    param([Parameter(Mandatory = $true)][string]$RelativePath)
    return Get-Content -LiteralPath (Require-File $RelativePath) -Raw
}

function Require-Text {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string[]]$Patterns
    )
    $text = Read-RepoText $RelativePath
    foreach ($pattern in $Patterns) {
        if (-not $text.Contains($pattern)) {
            throw "Missing pattern '$pattern' in $RelativePath"
        }
    }
}

function Require-NoRegex {
    param(
        [Parameter(Mandatory = $true)][string]$RelativePath,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
    $text = Read-RepoText $RelativePath
    if ($text -match $Pattern) {
        throw $Message
    }
}

function Get-YamlDocumentByName {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$MetadataName
    )
    $documents = [regex]::Split($Text, "(?m)^---\s*$")
    foreach ($document in $documents) {
        if ($document -match "(?m)^\s*name:\s+$([regex]::Escape($MetadataName))\s*$") {
            return $document
        }
    }
    throw "Missing YAML document with metadata.name $MetadataName"
}

function Get-YamlBlock {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$AnchorRegex
    )
    $lines = $Text -split "`r?`n"
    $start = -1
    $indent = 0
    for ($index = 0; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -match $AnchorRegex) {
            $start = $index
            $indent = ([regex]::Match($lines[$index], "^\s*")).Value.Length
            break
        }
    }
    if ($start -lt 0) {
        throw "Missing YAML block anchor matching $AnchorRegex"
    }

    $block = New-Object System.Collections.Generic.List[string]
    for ($index = $start; $index -lt $lines.Count; $index++) {
        $line = $lines[$index]
        if ($index -gt $start -and $line.Trim().Length -gt 0) {
            $currentIndent = ([regex]::Match($line, "^\s*")).Value.Length
            if ($currentIndent -le $indent) {
                break
            }
        }
        $block.Add($line)
    }
    return ($block -join "`n")
}

function Require-EnumValues {
    param(
        [Parameter(Mandatory = $true)][string]$Block,
        [Parameter(Mandatory = $true)][string[]]$ExpectedValues,
        [Parameter(Mandatory = $true)][string]$Context
    )
    $match = [regex]::Match($Block, 'enum:\s*\[([^\]]+)\]')
    if (-not $match.Success) {
        throw "Missing enum in $Context"
    }
    $values = @($match.Groups[1].Value.Split(",") | ForEach-Object { $_.Trim().Trim('"').Trim("'") })
    foreach ($value in $ExpectedValues) {
        if ($value -notin $values) {
            throw "Missing enum value '$value' in $Context"
        }
    }
    if ($values.Count -ne $ExpectedValues.Count) {
        throw "Unexpected enum values in $Context`: $($values -join ', ')"
    }
}

function Require-BlockText {
    param(
        [Parameter(Mandatory = $true)][string]$Block,
        [Parameter(Mandatory = $true)][string[]]$Patterns,
        [Parameter(Mandatory = $true)][string]$Context
    )
    foreach ($pattern in $Patterns) {
        if (-not $Block.Contains($pattern)) {
            throw "Missing pattern '$pattern' in $Context"
        }
    }
}

$crdText = Read-RepoText "iac\kubernetes\provider-api\crds.yaml"
$restoreRequest = Get-YamlDocumentByName $crdText "restorerequests.platform.privatecloud.local"

$targetBlock = Get-YamlBlock $restoreRequest "^\s{16}target:\s*$"
$kindBlock = Get-YamlBlock $targetBlock "^\s{20}kind:\s*$"
$modeBlock = Get-YamlBlock $targetBlock "^\s{20}mode:\s*$"
Require-EnumValues $kindBlock @("VirtualMachineClaim", "Volume", "Namespace", "KubernetesClusterClaim") "RestoreRequest spec.target.kind"
Require-EnumValues $modeBlock @("Copy", "InPlace") "RestoreRequest spec.target.mode"
Write-Output "restore_request_api_target_enum_ok"

$sourceBlock = Get-YamlBlock $restoreRequest "^\s{16}source:\s*$"
$approvalBlock = Get-YamlBlock $restoreRequest "^\s{16}approval:\s*$"
$statusBlock = Get-YamlBlock $restoreRequest "^\s{12}status:\s*$"
Require-BlockText $sourceBlock @(
    "backupPlanRef:",
    "recoveryPointRef:",
    "backupName:",
    "scheduleName:"
) "RestoreRequest spec.source"
Require-BlockText $targetBlock @(
    "namespaceMapping:",
    "additionalProperties:",
    "resourcePolicyRef:",
    "resourceModifierRefs:",
    "items:"
) "RestoreRequest spec.target restore policy"
Require-BlockText $approvalBlock @(
    "providerApproved:",
    "approvedBy:",
    "allowCrossTenant:"
) "RestoreRequest spec.approval"
Require-BlockText $statusBlock @(
    "restoreName:",
    "veleroRestoreName:",
    "restoredVMName:",
    "sourceBackupName:",
    "validationErrors:",
    "failureReason:"
) "RestoreRequest status"
Write-Output "restore_request_policy_fields_ok"

Require-Text "iac\kubernetes\production-backup-runtime\runtime-controller-skeleton.yaml" @(
    "kind: ConfigMap",
    "provider-backup-runtime-reconciliation-contract",
    "BackupPlan.spec.schedule maps to Velero Schedule.spec.schedule",
    "Schedule.spec.template, which is a Velero BackupSpec",
    "one-shot provider backup action may create Velero Backup",
    "RestoreRequest.spec.source.backupName maps to Velero",
    "Restore.spec.backupName",
    "RestoreRequest.spec.source.scheduleName",
    "RestoreRequest.spec.target.namespaceMapping maps to Velero",
    "FailedValidation",
    "failurePolicy Fail",
    "--enabled-target-kinds=VirtualMachineClaim,Volume,Namespace,KubernetesClusterClaim",
    "--enabled-restore-modes=Copy,InPlace",
    "--require-restore-policy-refs=true",
    "--require-provider-admin-for-in-place=true",
    "--deny-cross-tenant-restore-by-default=true",
    "--status-failure-phase=FailedValidation",
    "replicas: 0",
    "platform.privatecloud.local/cutover-disabled-by-default: `"true`""
)
Require-Text "iac\kubernetes\production-backup-runtime\README.md" @(
    "API Runtime Seam",
    'BackupPlan` maps to Velero `Schedule.spec.schedule`',
    'Schedule.spec.template` (`BackupSpec`)',
    'RestoreRequest.spec.source.backupName` maps to Velero',
    "Restore.spec.backupName",
    "FailedValidation",
    "UnsupportedTarget",
    "https://velero.io/docs/"
)
Require-Text "docs\production-backup-operations.md" @(
    "API Runtime Seam",
    'BackupPlan` reconciles to Velero `Schedule.spec.schedule`',
    'RestoreRequest` reconciles to Velero `Restore.spec.backupName`',
    "uses KubeVirt snapshots for VM backup"
)
Require-Text "docs\production-backup-dr.md" @(
    "verify-production-backup-runtime-api-seam.ps1",
    'RestoreRequest` CRD is widened for the production seam',
    "UnsupportedTarget"
)
Write-Output "velero_mapping_contract_ok"

Require-Text "iac\kubernetes\provider-controller\controller.py" @(
    'if target_kind != "VirtualMachineClaim" or target_mode != "Copy":',
    '"reason": "UnsupportedTarget"',
    "lab restore backend currently supports VirtualMachineClaim targets with mode Copy"
)
Require-Text "iac\kubernetes\provider-controller\rendered-controller.yaml" @(
    'if target_kind != "VirtualMachineClaim" or target_mode != "Copy":',
    '"reason": "UnsupportedTarget"',
    "lab restore backend currently supports VirtualMachineClaim targets with mode Copy"
)
Write-Output "lab_restore_fail_closed_ok"

Require-NoRegex `
    "gitops\platform\kustomization.yaml" `
    "production-backup-runtime|platform-production-backup-runtime|provider-backup-runtime-controller" `
    "The shared lab platform overlay must not reference the production backup runtime."
Require-NoRegex `
    "gitops\cells\lab-hyperv\kustomization.yaml" `
    "production-backup-runtime|platform-production-backup-runtime|provider-backup-runtime-controller" `
    "The Hyper-V lab overlay must not reference the production backup runtime."
Require-NoRegex `
    "iac\kubernetes\production-backup\kustomization.yaml" `
    "production-backup-runtime|runtime-controller-skeleton|platform-production-backup-runtime" `
    "The contract-only production backup bundle must not reference the runtime skeleton."
Write-Output "lab_overlay_no_runtime_reference_ok"

Require-NoRegex `
    "iac\kubernetes\provider-controller\controller.yaml" `
    "velero\.io|BackupStorageLocation|VolumeSnapshotLocation|BackupRepository|provider-backup-runtime-controller|production-backup-runtime" `
    "The lab provider-controller RBAC must not include Velero production runtime access."
Require-NoRegex `
    "iac\kubernetes\provider-controller\controller.py" `
    "velero\.io|BackupStorageLocation|VolumeSnapshotLocation|BackupRepository|provider-backup-runtime-controller|production-backup-runtime" `
    "The lab provider-controller implementation must not reference Velero production runtime APIs."
Write-Output "lab_controller_no_velero_runtime_rbac_ok"

Require-Text "docs\provider-roadmap.md" @(
    'Expand the provider `RestoreRequest` API/runtime seam',
    "Implement and validate production backup service runtime integration"
)
Require-Text "docs\test-plan.md" @(
    "Production backup runtime API seam",
    "verify-production-backup-runtime-api-seam.ps1"
)
Require-Text "docs\operations-log.md" @(
    "Production backup runtime API seam",
    "This is an API/runtime seam only"
)
Write-Output "production_backup_runtime_api_seam_ok"
