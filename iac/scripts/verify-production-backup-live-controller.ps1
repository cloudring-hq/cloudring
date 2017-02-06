param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

function Resolve-RepoPath { param([string]$RelativePath) Join-Path $Root $RelativePath }
function Require-File {
    param([string]$RelativePath)
    $path = Resolve-RepoPath $RelativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required file: $RelativePath" }
    return $path
}
function Read-RepoText { param([string]$RelativePath) Get-Content -LiteralPath (Require-File $RelativePath) -Raw }
function Require-Text {
    param([string]$RelativePath, [string[]]$Patterns)
    $text = Read-RepoText $RelativePath
    foreach ($pattern in $Patterns) { if (-not $text.Contains($pattern)) { throw "Missing pattern '$pattern' in $RelativePath" } }
}
function Require-NoRegex {
    param([string]$RelativePath, [string]$Pattern, [string]$Message)
    $path = Resolve-RepoPath $RelativePath
    $files = if (Test-Path -LiteralPath $path -PathType Leaf) { @(Get-Item -LiteralPath $path) } else { @(Get-ChildItem -LiteralPath $path -Recurse -File) }
    foreach ($file in $files) {
        if ((Get-Content -LiteralPath $file.FullName -Raw) -match $Pattern) { throw "$Message Offending file: $($file.FullName)" }
    }
}
function Resolve-Python {
    foreach ($candidate in @($env:PYTHON, "python3", "python", "C:\Users\yuri\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")) {
        if (-not $candidate) { continue }
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        $resolved = if ($command) { $command.Source } elseif (Test-Path -LiteralPath $candidate -PathType Leaf) { $candidate } else { $null }
        if ($resolved) {
            $previous = $ErrorActionPreference
            $ErrorActionPreference = "Continue"
            try {
                & $resolved --version 2>$null | Out-Null
                if ($LASTEXITCODE -eq 0) { return $resolved }
            } finally {
                $ErrorActionPreference = $previous
            }
        }
    }
    throw "No Python interpreter found."
}
function Normalize-YamlScalar {
    param([AllowEmptyString()][string]$Value)
    if ($null -eq $Value) { return "" }
    $v = $Value.Trim()
    if ($v.Length -ge 2 -and $v.StartsWith('"') -and $v.EndsWith('"')) { return $v.Substring(1, $v.Length - 2) }
    return $v
}
function Get-TopLevelMap {
    param([string]$Document, [string]$Section)
    $map = @{}
    $lines = $Document -split "`r?`n"
    $inSection = $false
    $blockKey = $null
    $blockLines = @()
    foreach ($line in $lines) {
        if ($inSection -and $blockKey -and $line -match "^\s{4,}(.*)$") { $blockLines += $Matches[1]; continue }
        if ($inSection -and $blockKey) { $map[$blockKey] = ($blockLines -join "`n").TrimEnd(); $blockKey = $null; $blockLines = @() }
        if ($line -match "^$([regex]::Escape($Section)):\s*$") { $inSection = $true; continue }
        if ($inSection -and $line -match "^[A-Za-z0-9_-]+:") { break }
        if ($inSection -and $line -match "^\s{2}([A-Za-z0-9_.\/-]+):\s*\|\s*$") { $blockKey = $Matches[1]; $blockLines = @(); continue }
        if ($inSection -and $line -match "^\s{2}([A-Za-z0-9_.\/-]+):\s*(.*)$") { $map[$Matches[1]] = Normalize-YamlScalar $Matches[2] }
    }
    if ($inSection -and $blockKey) { $map[$blockKey] = ($blockLines -join "`n").TrimEnd() }
    return $map
}
function Get-NestedMap {
    param([string]$Document, [string]$Parent, [string]$Child)
    $map = @{}
    $lines = $Document -split "`r?`n"
    $inParent = $false; $inChild = $false
    foreach ($line in $lines) {
        if ($line -match "^$([regex]::Escape($Parent)):\s*$") { $inParent = $true; continue }
        if ($inParent -and $line -match "^[A-Za-z0-9_-]+:") { break }
        if ($inParent -and $line -match "^\s{2}$([regex]::Escape($Child)):\s*$") { $inChild = $true; continue }
        if ($inChild -and $line -match "^\s{2}[A-Za-z0-9_.\/-]+:") { break }
        if ($inChild -and $line -match "^\s{4}([A-Za-z0-9_.\/-]+):\s*(.*)$") { $map[$Matches[1]] = Normalize-YamlScalar $Matches[2] }
    }
    return $map
}
function Get-ConfigMapDocument {
    param([string]$Text, [string]$Name)
    foreach ($doc in ($Text -split "(?m)^---\s*$")) {
        if ($doc -match "(?m)^kind:\s*ConfigMap\s*$") {
            $metadata = Get-TopLevelMap $doc "metadata"
            if ($metadata["name"] -eq $Name) { return $doc }
        }
    }
    throw "ConfigMap $Name not found"
}
function Require-DataContains { param([hashtable]$Data, [string]$Key, [string]$Needle) if (-not $Data.ContainsKey($Key) -or -not $Data[$Key].Contains($Needle)) { throw "Missing '$Needle' in $Key" } }
function Require-DataValue { param([hashtable]$Data, [string]$Key, [string]$Expected) if ($Data[$Key] -ne $Expected) { throw "Unexpected $Key" } }
function Require-ListContains { param([hashtable]$Data, [string]$Key, [string[]]$Items) $values = @($Data[$Key].Split(",") | ForEach-Object { $_.Trim() }); foreach ($item in $Items) { if ($values -notcontains $item) { throw "Missing list item $item in $Key" } } }

Require-Text "iac\kubernetes\production-backup-runtime\kustomization.yaml" @("live-controller-contract.yaml")
$contractText = Read-RepoText "iac\kubernetes\production-backup-runtime\live-controller-contract.yaml"
$contractDoc = Get-ConfigMapDocument $contractText "provider-backup-live-controller-contract"
$drillDoc = Get-ConfigMapDocument $contractText "provider-backup-live-controller-drill"
$data = Get-TopLevelMap $contractDoc "data"
$annotations = Get-NestedMap $contractDoc "metadata" "annotations"
$drillData = Get-TopLevelMap $drillDoc "data"
Require-DataValue $annotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $annotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $data "owner" "provider-backup-runtime-controller"
Require-DataContains $data "controller-image-handoff" "provider-backup-controller:REPLACE_WITH_VERSION"
Require-DataValue $data "runtime-enabled-env" "RUNTIME_ENABLED=false"
Require-ListContains $data "target-kinds" @("Volume", "Namespace", "KubernetesClusterClaim")
Require-ListContains $data "reconcile-states" @("observed", "preflighted", "planned", "velero-objects-created", "status-patched", "audit-recorded", "slo-recorded", "completed")
Require-DataContains $data "velero-create-boundaries" "create Restore only after restore-plan and tenant isolation verified"
Require-DataContains $data "idempotency-keys" "backupPlan.uid:generation:targetKind:schedule"
Require-DataContains $data "status-patches" "RestoreRequest.status.phase=Succeeded"
Require-ListContains $data "audit-events" @("BackupLiveControllerObserved", "BackupLiveControllerRejected", "RestoreTenantIsolationRejected")
Require-ListContains $data "slo-hooks" @("backup_runtime_reconcile_duration_seconds", "backup_runtime_velero_create_total", "backup_runtime_rejected_total")
Require-DataContains $data "tenant-isolation" "cross-tenant restore rejected before Velero create"
Require-DataContains $data "failure-policy" "duplicate idempotency conflict"
Require-DataContains $drillData "drill" "states happen in order"
Write-Output "production_backup_live_controller_contract_ok"

$scriptRelative = "iac\scripts\production-backup-live-controller.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python
& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) { throw "py_compile failed for $scriptRelative" }
Write-Output "python_py_compile_ok"

$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("production-backup-live-controller-" + [Guid]::NewGuid().ToString("N") + ".json")
@'
{"cases":[
{"name":"volume","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-vol","restoreUid":"rr-vol","generation":1,"preflight":true,"immutable":true},
{"name":"namespace","targetKind":"Namespace","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-ns","restoreUid":"rr-ns","generation":1,"preflight":true,"immutable":true},
{"name":"tenant-cluster","targetKind":"KubernetesClusterClaim","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-kcc","restoreUid":"rr-kcc","generation":1,"preflight":true,"immutable":true},
{"name":"missing-owner","targetKind":"Volume","projectRef":"","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true},
{"name":"duplicate-key","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true,"duplicateKey":true},
{"name":"before-preflight","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":false,"immutable":true},
{"name":"mutable-storage","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":false},
{"name":"cross-tenant","targetKind":"Namespace","projectRef":"tenant-a","targetProjectRef":"tenant-b","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true},
{"name":"missing-status","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true,"missingStatus":true},
{"name":"missing-audit","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true,"missingAudit":true},
{"name":"missing-slo","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true,"missingSlo":true}
]}
'@ | Set-Content -LiteralPath $fixture -Encoding ASCII
$output = & $python $scriptPath $fixture
if ($LASTEXITCODE -ne 0) { throw "Live controller simulator failed" }
$jsonLine = $output | Where-Object { $_.StartsWith("LIVE_CONTROLLER_JSON:") } | Select-Object -First 1
if (-not $jsonLine) { throw "Missing LIVE_CONTROLLER_JSON" }
$payload = $jsonLine.Substring("LIVE_CONTROLLER_JSON:".Length) | ConvertFrom-Json
if ($payload.mode -ne "offline-disabled-live-controller-contract") { throw "Unexpected mode" }
if ($payload.runtime.runtimeEnabled -ne $false) { throw "Runtime must be disabled" }
if ($payload.accepted.Count -ne 3) { throw "Expected three accepted targets" }
foreach ($kind in @("Volume", "Namespace", "KubernetesClusterClaim")) {
    if ($kind -notin @($payload.accepted | ForEach-Object { $_.targetKind })) { throw "Missing accepted target $kind" }
}
foreach ($case in $payload.accepted) {
    if ($case.veleroObjects.Count -ne 3) { throw "Accepted case must create Schedule, Backup, Restore" }
    if ($case.statusPatches.Count -ne 2) { throw "Accepted case must publish two status patches" }
    $backupStatus = @($case.statusPatches | Where-Object { $_.apiKind -eq "BackupPlan" }) | Select-Object -First 1
    $restoreStatus = @($case.statusPatches | Where-Object { $_.apiKind -eq "RestoreRequest" }) | Select-Object -First 1
    if (-not $backupStatus -or $backupStatus.phase -ne "Protected") { throw "Accepted case missing BackupPlan Protected status" }
    if (-not $backupStatus.lastRun -or -not $backupStatus.lastSuccess) { throw "Accepted case missing BackupPlan lastRun/lastSuccess" }
    if (-not $backupStatus.conditions -or $backupStatus.conditions.Count -lt 2) { throw "Accepted case missing BackupPlan conditions" }
    if (-not $restoreStatus -or $restoreStatus.phase -ne "Succeeded") { throw "Accepted case missing RestoreRequest Succeeded status" }
    if (-not $restoreStatus.veleroRestoreName) { throw "Accepted case missing RestoreRequest veleroRestoreName" }
    if (-not $restoreStatus.conditions -or $restoreStatus.conditions.Count -lt 2) { throw "Accepted case missing RestoreRequest conditions" }
    if ($case.auditEvents.Count -lt 4) { throw "Accepted case missing audit events" }
    if ($case.sloHooks.Count -lt 4) { throw "Accepted case missing SLO hooks" }
    if ("backup_runtime_idempotency_replay_total" -notin @($case.sloHooks)) { throw "Accepted case missing idempotency replay SLO hook" }
    if (($case.states -join ",") -ne "observed,preflighted,planned,velero-objects-created,status-patched,audit-recorded,slo-recorded,completed") { throw "State ordering mismatch" }
}
$reasons = @($payload.rejected | ForEach-Object { $_.reason })
foreach ($reason in @("MalformedProviderFixture","DuplicateIdempotencyKeySuppressed","VeleroCreateBeforePreflightDenied","MutableStoragePolicyDenied","CrossTenantRestoreDenied","MissingStatusPatchDenied","MissingAuditEventDenied","MissingSloHookDenied")) {
    if ($reason -notin $reasons) { throw "Missing rejection reason $reason" }
}
foreach ($case in $payload.rejected) {
    if ($case.veleroObjects.Count -ne 0) { throw "Rejected case created Velero objects" }
}
Write-Output "production_backup_live_controller_fail_closed_ok"

if ($payload.clusterAccess.mode -ne "offline" -or $payload.clusterAccess.commandsInvoked.Count -ne 0 -or $payload.clusterAccess.networkClients.Count -ne 0 -or $payload.clusterAccess.configFilesRead.Count -ne 0) { throw "Simulator used live access" }
$source = Get-Content -LiteralPath $scriptPath -Raw
foreach ($pattern in @("kubectl","kubeconfig","load_kube_config","subprocess","requests","httpx","urllib","socket")) {
    if ($source -match $pattern) { throw "Forbidden live access token in simulator: $pattern" }
}
Write-Output "production_backup_live_controller_no_cluster_access_ok"

$runtimePattern = "live-controller-contract.yaml|provider-backup-live-controller-contract|provider-backup-live-controller-drill|production-backup-live-controller|BackupLiveController|backup_runtime_velero_create_total"
Require-NoRegex "gitops\platform" $runtimePattern "The shared lab platform overlay must not apply backup live-controller resources."
Require-NoRegex "gitops\cells\lab-hyperv" $runtimePattern "The Hyper-V lab cell overlay must not apply backup live-controller resources."
Require-NoRegex "iac\kubernetes\production-backup" $runtimePattern "The contract-only backup blueprint must not include backup live-controller resources."
Require-NoRegex "gitops\platform-production-backup" $runtimePattern "The contract-only backup overlay must not include backup live-controller resources."
Write-Output "lab_overlay_no_backup_live_controller_reference_ok"

Require-Text "iac\kubernetes\production-backup-runtime\README.md" @("Live Controller Contract", "verify-production-backup-live-controller.ps1", "provider-backup-live-controller-contract")
Require-Text "docs\production-backup-operations.md" @("Production Backup Live Controller Contract", "verify-production-backup-live-controller.ps1", "BackupLiveControllerRejected")
Require-Text "docs\provider-roadmap.md" @("Implement and validate production backup service runtime integration", "verify-production-backup-live-controller.ps1")
Require-Text "docs\test-plan.md" @("Production backup live controller contract", "verify-production-backup-live-controller.ps1")
Require-Text "docs\operations-log.md" @("Production backup live controller contract", "verify-production-backup-live-controller.ps1")

Remove-Item -LiteralPath $fixture -Force -ErrorAction SilentlyContinue
Write-Output "production_backup_live_controller_ok"
