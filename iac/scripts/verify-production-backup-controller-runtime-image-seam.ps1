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
    foreach ($line in $lines) {
        if ($line -match "^$([regex]::Escape($Section)):\s*$") { $inSection = $true; continue }
        if ($inSection -and $line -match "^[A-Za-z0-9_-]+:") { break }
        if ($inSection -and $line -match "^\s{2}([A-Za-z0-9_.\/-]+):\s*(.*)$") { $map[$Matches[1]] = Normalize-YamlScalar $Matches[2] }
    }
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
function Require-DataContains { param([hashtable]$Data, [string]$Key, [string]$Needle) if (-not $Data.ContainsKey($Key) -or -not $Data[$Key].Contains($Needle)) { throw "Missing '$Needle' in $Key" } }
function Require-DataValue { param([hashtable]$Data, [string]$Key, [string]$Expected) if ($Data[$Key] -ne $Expected) { throw "Unexpected $Key" } }
function Require-ListContains {
    param([hashtable]$Data, [string]$Key, [string[]]$Items)
    $values = @($Data[$Key].Split(",") | ForEach-Object { $_.Trim() })
    foreach ($item in $Items) { if ($values -notcontains $item) { throw "Missing list item $item in $Key" } }
}

Require-Text "iac\kubernetes\production-backup-runtime\kustomization.yaml" @("runtime-image-seam.yaml")
$contractText = Read-RepoText "iac\kubernetes\production-backup-runtime\runtime-image-seam.yaml"
$data = Get-TopLevelMap $contractText "data"
$annotations = Get-NestedMap $contractText "metadata" "annotations"
Require-DataValue $annotations "platform.privatecloud.local/template-only" "true"
Require-DataValue $annotations "platform.privatecloud.local/cutover-disabled-by-default" "true"
Require-DataValue $data "owner" "provider-backup-runtime-controller"
Require-DataContains $data "image" "provider-backup-controller:REPLACE_WITH_VERSION"
Require-DataValue $data "entrypoint" "/usr/local/bin/provider-backup-controller"
Require-DataValue $data "runtime-enabled-env" "RUNTIME_ENABLED=false"
Require-ListContains $data "target-kinds" @("Volume", "Namespace", "KubernetesClusterClaim")
Require-DataContains $data "input-contract" "BackupPlan.v1alpha1"
Require-DataContains $data "output-contract" "Velero Schedule"
Require-DataContains $data "status-fields" "BackupPlan.status.lastRun"
Require-DataContains $data "status-fields" "RestoreRequest.status.veleroRestoreName"
Require-ListContains $data "slo-hooks" @("backup_runtime_reconcile_duration_seconds", "backup_runtime_velero_create_total", "backup_runtime_idempotency_replay_total", "backup_runtime_rejected_total")
Require-DataContains $data "promotion-gates" "disabled->canary requires RUNTIME_ENABLED=true"
Require-DataContains $data "fail-closed-policy" "enabled without canary scope"
Write-Output "production_backup_controller_runtime_image_contract_ok"

$scriptRelative = "iac\scripts\production-backup-controller-runtime-image-seam.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python
& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) { throw "py_compile failed for $scriptRelative" }
Write-Output "python_py_compile_ok"

$fixture = Join-Path ([System.IO.Path]::GetTempPath()) ("production-backup-controller-runtime-image-seam-" + [Guid]::NewGuid().ToString("N") + ".json")
@'
{"runtime":{"image":"registry.example.invalid/privatecloud/provider-backup-controller:REPLACE_WITH_VERSION","entrypoint":"/usr/local/bin/provider-backup-controller","runtimeEnabled":false,"canaryScope":"provider-backup-runtime-canary"},"cases":[
{"name":"volume","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-vol","restoreUid":"rr-vol","generation":1,"preflight":true,"immutable":true},
{"name":"namespace","targetKind":"Namespace","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-ns","restoreUid":"rr-ns","generation":1,"preflight":true,"immutable":true},
{"name":"tenant-cluster","targetKind":"KubernetesClusterClaim","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-kcc","restoreUid":"rr-kcc","generation":1,"preflight":true,"immutable":true},
{"backupPlan":{"metadata":{"name":"nested-tenant-cluster","uid":"bp-nested-kcc","generation":2,"labels":{"platform.privatecloud.local/project":"tenant-a"}},"spec":{"targetKind":"KubernetesClusterClaim","projectRef":"tenant-a","preflightReady":true,"immutableStorage":true}},"restoreRequest":{"metadata":{"name":"nested-tenant-cluster-restore","uid":"rr-nested-kcc"},"spec":{"targetProjectRef":"tenant-a","preflightReady":true,"immutableStorage":true}}},
{"name":"unsupported","targetKind":"Unknown","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true},
{"name":"malformed","targetKind":"Volume","projectRef":"","targetProjectRef":"tenant-a","backupUid":"bp","restoreUid":"rr","generation":1,"preflight":true,"immutable":true},
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
if ($LASTEXITCODE -ne 0) { throw "Runtime image seam harness failed" }
$jsonLine = $output | Where-Object { $_.StartsWith("RUNTIME_IMAGE_SEAM_JSON:") } | Select-Object -First 1
if (-not $jsonLine) { throw "Missing RUNTIME_IMAGE_SEAM_JSON" }
$payload = $jsonLine.Substring("RUNTIME_IMAGE_SEAM_JSON:".Length) | ConvertFrom-Json
if ($payload.mode -ne "offline-disabled-runtime-image-seam") { throw "Unexpected mode" }
if ($payload.runtime.runtimeEnabled -ne $false) { throw "Runtime image seam must stay disabled by default" }
if ($payload.accepted.Count -ne 4) { throw "Expected four accepted runtime image seam fixtures including nested BackupPlan/RestoreRequest" }
foreach ($kind in @("Volume", "Namespace", "KubernetesClusterClaim")) {
    if ($kind -notin @($payload.accepted | ForEach-Object { $_.targetKind })) { throw "Missing accepted target $kind" }
}
$nested = @($payload.accepted | Where-Object { $_.name -eq "nested-tenant-cluster" }) | Select-Object -First 1
if (-not $nested -or $nested.targetKind -ne "KubernetesClusterClaim") { throw "Nested BackupPlan/RestoreRequest fixture was not accepted as KubernetesClusterClaim" }
foreach ($case in $payload.accepted) {
    if ($case.veleroObjects.Count -ne 3) { throw "Accepted case must create Schedule, Backup, Restore" }
    $schedule = @($case.veleroObjects | Where-Object { $_.kind -eq "Schedule" }) | Select-Object -First 1
    $backup = @($case.veleroObjects | Where-Object { $_.kind -eq "Backup" }) | Select-Object -First 1
    $restore = @($case.veleroObjects | Where-Object { $_.kind -eq "Restore" }) | Select-Object -First 1
    if (-not $schedule) { throw "Missing Schedule object" }
    if (-not $backup) { throw "Missing Backup object" }
    if (-not $restore) { throw "Missing Restore object" }
    if (-not $schedule.spec.schedule -or -not $schedule.spec.template.storageLocation -or -not $schedule.spec.template.includedResources) { throw "Schedule object missing reconcile spec payload" }
    if (-not $backup.spec.storageLocation -or -not $backup.spec.includedResources -or $backup.spec.snapshotVolumes -ne $true) { throw "Backup object missing reconcile spec payload" }
    if (-not $restore.spec.backupName -or -not $restore.spec.includedResources -or -not $restore.spec.namespaceMapping -or $restore.spec.restorePVs -ne $true) { throw "Restore object missing reconcile spec payload" }
    if ($case.targetKind -eq "KubernetesClusterClaim" -and "kubernetesclusterclaims" -notin @($backup.spec.includedResources)) { throw "KubernetesClusterClaim backup missing provider resource selection" }
    if (-not $case.idempotencyKeys.schedule -or -not $case.idempotencyKeys.backup -or -not $case.idempotencyKeys.restore) { throw "Accepted case missing idempotency keys" }
    if (($case.states -join ",") -ne "observed,preflighted,planned,velero-objects-created,status-patched,audit-recorded,slo-recorded,completed") { throw "State ordering mismatch" }
    $backupStatus = @($case.statusPatches | Where-Object { $_.apiKind -eq "BackupPlan" }) | Select-Object -First 1
    $restoreStatus = @($case.statusPatches | Where-Object { $_.apiKind -eq "RestoreRequest" }) | Select-Object -First 1
    if (-not $backupStatus.lastRun -or -not $backupStatus.lastSuccess -or $backupStatus.conditions.Count -lt 2) { throw "Accepted case missing BackupPlan status fields" }
    if (-not $restoreStatus.veleroRestoreName -or $restoreStatus.conditions.Count -lt 2) { throw "Accepted case missing RestoreRequest status fields" }
    if ("backup_runtime_idempotency_replay_total" -notin @($case.sloHooks)) { throw "Accepted case missing idempotency SLO hook" }
    if ($case.auditEvents.Count -lt 4) { throw "Accepted case missing audit events" }
}
Write-Output "production_backup_controller_runtime_image_seam_ok"

$reasons = @($payload.rejected | ForEach-Object { $_.reason })
foreach ($reason in @("UnsupportedTargetKind","MalformedProviderFixture","DuplicateIdempotencyKeySuppressed","VeleroCreateBeforePreflightDenied","MutableStoragePolicyDenied","CrossTenantRestoreDenied","MissingStatusPatchDenied","MissingAuditEventDenied","MissingSloHookDenied")) {
    if ($reason -notin $reasons) { throw "Missing rejection reason $reason" }
}
foreach ($case in $payload.rejected) {
    if ($case.veleroObjects.Count -ne 0) { throw "Rejected case created Velero objects" }
}

$badRuntimeFixture = Join-Path ([System.IO.Path]::GetTempPath()) ("production-backup-controller-runtime-image-bad-" + [Guid]::NewGuid().ToString("N") + ".json")
@'
{"runtime":{"image":"registry.example.invalid/privatecloud/provider-backup-controller:REPLACE_WITH_VERSION","entrypoint":"/usr/local/bin/provider-backup-controller","runtimeEnabled":true,"canaryScope":"wrong"},"cases":[
{"name":"volume","targetKind":"Volume","projectRef":"tenant-a","targetProjectRef":"tenant-a","backupUid":"bp-vol","restoreUid":"rr-vol","generation":1,"preflight":true,"immutable":true}
]}
'@ | Set-Content -LiteralPath $badRuntimeFixture -Encoding ASCII
$badOutput = & $python $scriptPath $badRuntimeFixture
$badJsonLine = $badOutput | Where-Object { $_.StartsWith("RUNTIME_IMAGE_SEAM_JSON:") } | Select-Object -First 1
$badPayload = $badJsonLine.Substring("RUNTIME_IMAGE_SEAM_JSON:".Length) | ConvertFrom-Json
if ($badPayload.accepted.Count -ne 0) { throw "Enabled runtime without canary scope accepted a case" }
if ("EnabledWithoutCanaryScopeDenied" -notin @($badPayload.rejected | ForEach-Object { $_.reason })) { throw "Missing enabled-without-canary rejection" }
Write-Output "production_backup_controller_runtime_image_fail_closed_ok"

if ($payload.clusterAccess.mode -ne "offline" -or $payload.clusterAccess.commandsInvoked.Count -ne 0 -or $payload.clusterAccess.networkClients.Count -ne 0 -or $payload.clusterAccess.configFilesRead.Count -ne 0) { throw "Harness used live access" }
$source = Get-Content -LiteralPath $scriptPath -Raw
foreach ($pattern in @("\bkubectl\b","\bkubeconfig\b","load_kube_config","\bsubprocess\b","import\s+requests","from\s+requests","\bhttpx\b","\burllib\b","\bsocket\b")) {
    if ($source -match $pattern) { throw "Forbidden live access token in runtime-image seam harness: $pattern" }
}
Write-Output "production_backup_controller_runtime_image_no_cluster_access_ok"

$runtimePattern = "runtime-image-seam.yaml|provider-backup-controller-runtime-image-seam|production-backup-controller-runtime-image-seam|BackupControllerRuntime|backup_runtime_idempotency_replay_total"
Require-NoRegex "gitops\platform" $runtimePattern "The shared lab platform overlay must not apply backup controller runtime-image resources."
Require-NoRegex "gitops\cells\lab-hyperv" $runtimePattern "The Hyper-V lab cell overlay must not apply backup controller runtime-image resources."
Require-NoRegex "iac\kubernetes\production-backup" $runtimePattern "The contract-only backup blueprint must not include backup controller runtime-image resources."
Require-NoRegex "gitops\platform-production-backup" $runtimePattern "The contract-only backup overlay must not include backup controller runtime-image resources."
Write-Output "lab_overlay_no_backup_controller_runtime_image_reference_ok"

Require-Text "iac\kubernetes\production-backup-runtime\README.md" @("Runtime Image Seam", "verify-production-backup-controller-runtime-image-seam.ps1", "provider-backup-controller-runtime-image-seam")
Require-Text "docs\production-backup-operations.md" @("Production Backup Controller Runtime Image Seam", "verify-production-backup-controller-runtime-image-seam.ps1", "backup_runtime_idempotency_replay_total")
Require-Text "docs\provider-roadmap.md" @("production backup controller runtime image seam", "verify-production-backup-controller-runtime-image-seam.ps1")
Require-Text "docs\test-plan.md" @("Production backup controller runtime image seam", "verify-production-backup-controller-runtime-image-seam.ps1")
Require-Text "docs\operations-log.md" @("Production backup controller runtime image seam", "verify-production-backup-controller-runtime-image-seam.ps1")

Remove-Item -LiteralPath $fixture -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $badRuntimeFixture -Force -ErrorAction SilentlyContinue
Write-Output "production_backup_controller_runtime_image_ok"
