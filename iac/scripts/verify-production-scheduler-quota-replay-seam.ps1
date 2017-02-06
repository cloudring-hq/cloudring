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
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing required file: $RelativePath" }
    return $path
}

function Resolve-Python {
    $candidates = @()
    if ($env:PYTHON) { $candidates += $env:PYTHON }
    $candidates += @("python3", "python", "C:\Users\yuri\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe")
    foreach ($candidate in $candidates) {
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
    throw "No Python interpreter found via PYTHON, python3, python, or bundled runtime."
}

function Require-Equal {
    param($Actual, $Expected, [Parameter(Mandatory = $true)][string]$Message)
    if ($Actual -ne $Expected) { throw "$Message Expected '$Expected', got '$Actual'." }
}

function Require-Contains {
    param([Parameter(Mandatory = $true)]$Values, [Parameter(Mandatory = $true)][string]$Expected, [Parameter(Mandatory = $true)][string]$Message)
    if ($Expected -notin @($Values)) { throw "$Message Missing '$Expected'." }
}

function Require-NoRegex {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string]$Pattern, [Parameter(Mandatory = $true)][string]$Message)
    $text = Get-Content -LiteralPath (Require-File $RelativePath) -Raw
    if ($text -match $Pattern) { throw $Message }
}

$scriptRelative = "iac\scripts\production-scheduler-quota-replay-seam.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python
$fixturePath = Join-Path ([System.IO.Path]::GetTempPath()) ("provider-scheduler-quota-replay-" + [System.Guid]::NewGuid().ToString("N") + ".json")

& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) { throw "py_compile failed for $scriptRelative" }
Write-Output "python_py_compile_ok"

$fixtureJson = @'
{
  "canaryScope": "provider-scheduler-quota-replay-canary",
  "cases": [
    {"name":"vm-replay","admissionJournal":{"name":"journal-vm","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-a","uid":"uid-vm-a","generation":3},"duplicate":{"decision":"Admitted"}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid-vm-a","claimGeneration":3,"capacityCell":"cell-a","resources":{"cpuMillicores":1000,"memoryMi":1024}},"projectQuota":{"name":"tenant-a","vms":2,"quotaVms":10,"cpuMillicores":4000,"quotaCpuMillicores":12000},"repair":{"vms":1,"cpuMillicores":1000}},
    {"name":"cluster-replay-idempotent","admissionJournal":{"name":"journal-cluster","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"KubernetesClusterClaim","namespace":"tenant-a","name":"cluster-a","uid":"uid-cluster-a","generation":5},"duplicate":{"decision":"Admitted"}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid-cluster-a","claimGeneration":5,"capacityCell":"cell-b","resources":{"cpuMillicores":2000,"memoryMi":4096}},"projectQuota":{"name":"tenant-a","tenantClusters":1,"quotaTenantClusters":4,"cpuMillicores":5000,"quotaCpuMillicores":12000},"repair":{"tenantClusters":1,"cpuMillicores":2000}},
    {"name":"missing-journal","capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"missing-reservation","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1}},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"missing-quota","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"repair":{}},
    {"name":"stale-generation","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":2}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"conflicting-duplicate","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1},"duplicate":{"decision":"Rejected"}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"quota-underflow","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a","vms":0},"repair":{"vms":-1}},
    {"name":"quota-overflow","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a","vms":10,"quotaVms":10},"repair":{"vms":1}},
    {"name":"unknown-kind","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"Volume","namespace":"tenant-a","name":"vol","uid":"uid","generation":1}},"capacityReservation":{"phase":"Active","projectRef":"tenant-a","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"cross-project","admissionJournal":{"name":"j","decision":"Admitted","projectRef":"tenant-a","claimRef":{"kind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm","uid":"uid","generation":1}},"capacityReservation":{"phase":"Active","projectRef":"tenant-b","claimUid":"uid","claimGeneration":1,"capacityCell":"cell-a"},"projectQuota":{"name":"tenant-a"},"repair":{}},
    {"name":"malformed-case","admissionJournal":{"name":"j","decision":"Admitted"},"capacityReservation":{"phase":"Active"},"projectQuota":{"name":"tenant-a"},"repair":{}}
  ]
}
'@
[System.IO.File]::WriteAllText($fixturePath, $fixtureJson, [System.Text.UTF8Encoding]::new($false))

$output = & $python $scriptPath $fixturePath
if ($LASTEXITCODE -ne 0) { throw "Quota replay seam execution failed." }

$jsonLine = $output | Where-Object { $_.StartsWith("QUOTA_REPLAY_JSON:") } | Select-Object -First 1
if (-not $jsonLine) { throw "Quota replay seam did not emit QUOTA_REPLAY_JSON." }
$payload = $jsonLine.Substring("QUOTA_REPLAY_JSON:".Length) | ConvertFrom-Json

foreach ($marker in @(
    "provider_scheduler_quota_replay_fixture_parse_ok",
    "production_scheduler_quota_replay_seam_ok",
    "production_scheduler_quota_replay_fail_closed_ok",
    "production_scheduler_quota_replay_no_cluster_access_ok",
    "lab_overlay_no_scheduler_quota_replay_reference_ok"
)) {
    if ($marker -notin $output) { throw "Quota replay output missing marker: $marker" }
}
Write-Output "provider_scheduler_quota_replay_fixture_parse_ok"

Require-Equal $payload.adapterMode "disabled-by-default-scheduler-quota-replay-seam" "Adapter mode mismatch."
Require-Equal $payload.inputMode "SchedulerQuotaReplay fixtures" "Input mode mismatch."
Require-Equal $payload.preflightGate.canaryScope "provider-scheduler-quota-replay-canary" "Canary scope mismatch."
Require-Equal $payload.clusterAccess.mode "offline" "Cluster access mode mismatch."
Require-Equal $payload.replayed.Count 2 "Replay count mismatch."
foreach ($scenario in $payload.replayed) {
    Require-Equal $scenario.quotaReplayEvent.decision "Replayed" "Replay event decision mismatch."
    Require-Equal $scenario.reservationReplayDecision.allowed $true "Reservation replay must allow accepted cases."
    Require-Equal $scenario.statusPatch.phase "Admitted" "Accepted status patch mismatch."
    if ($scenario.quotaRepairPlan.committedActions.Count -lt 1) { throw "Accepted replay must include deterministic repair actions." }
}
$acceptedKinds = @($payload.replayed | ForEach-Object { $_.quotaReplayEvent.claimRef.kind })
Require-Contains $acceptedKinds "VirtualMachineClaim" "Accepted replay missing VM claim."
Require-Contains $acceptedKinds "KubernetesClusterClaim" "Accepted replay missing tenant cluster claim."
$vmReplay = $payload.replayed | Where-Object { $_.name -eq "vm-replay" } | Select-Object -First 1
$clusterReplay = $payload.replayed | Where-Object { $_.name -eq "cluster-replay-idempotent" } | Select-Object -First 1
if (-not $vmReplay -or -not $clusterReplay) { throw "Accepted replay set must include VM and tenant-cluster named fixtures." }
Require-Equal $vmReplay.quotaReplayEvent.idempotencyKey "uid-vm-a:3" "VM replay idempotency key mismatch."
Require-Equal $clusterReplay.quotaReplayEvent.idempotencyKey "uid-cluster-a:5" "Tenant-cluster replay idempotency key mismatch."
Require-Equal $vmReplay.quotaReplayEvent.decision "Replayed" "Accepted VM duplicate journal must remain idempotent."
Require-Equal $clusterReplay.quotaReplayEvent.decision "Replayed" "Accepted tenant-cluster duplicate journal must remain idempotent."
Write-Output "production_scheduler_quota_replay_seam_ok"

$expectedReasons = @(
    "MissingAdmissionJournal",
    "MissingCapacityReservation",
    "MissingProjectQuota",
    "StaleReservationGeneration",
    "ConflictingDuplicateJournal",
    "QuotaUnderflowRepair",
    "QuotaOverflowRepair",
    "UnknownRequestKind",
    "CrossProjectReplayAttempt",
    "MalformedAdmissionJournal"
)
Require-Equal $payload.failClosed.Count 10 "Fail-closed replay count mismatch."
foreach ($scenario in $payload.failClosed) {
    Require-Equal $scenario.reservationReplayDecision.allowed $false "Fail-closed replay must deny."
    Require-Equal $scenario.quotaRepairPlan.committedActions.Count 0 "Fail-closed replay must commit zero repair actions."
}
$actualReasons = @($payload.failClosed | ForEach-Object { $_.statusPatch.admission.reason })
foreach ($reason in $expectedReasons) {
    Require-Contains $actualReasons $reason "Fail-closed reason set is incomplete."
}

$badScopePath = Join-Path ([System.IO.Path]::GetTempPath()) ("provider-scheduler-quota-replay-bad-scope-" + [System.Guid]::NewGuid().ToString("N") + ".json")
[System.IO.File]::WriteAllText($badScopePath, '{"canaryScope":"wrong","cases":[]}', [System.Text.UTF8Encoding]::new($false))
$badOutput = & $python $scriptPath $badScopePath
$badJsonLine = $badOutput | Where-Object { $_.StartsWith("QUOTA_REPLAY_JSON:") } | Select-Object -First 1
$badPayload = $badJsonLine.Substring("QUOTA_REPLAY_JSON:".Length) | ConvertFrom-Json
Require-Equal $badPayload.replayed.Count 0 "Wrong canary scope must not replay."
Require-Equal $badPayload.failClosed.Count 1 "Wrong canary scope must fail closed."
Require-Equal $badPayload.failClosed[0].quotaRepairPlan.committedActions.Count 0 "Wrong canary scope must commit zero repair actions."
Write-Output "production_scheduler_quota_replay_fail_closed_ok"

Require-Equal $payload.clusterAccess.commandsInvoked.Count 0 "Seam must not invoke commands."
Require-Equal $payload.clusterAccess.networkClients.Count 0 "Seam must not use network clients."
Require-Equal $payload.clusterAccess.configFilesRead.Count 0 "Seam must not read cluster config files."
$scriptText = Get-Content -LiteralPath $scriptPath -Raw
foreach ($pattern in @(
    '(?im)^\s*(from|import)\s+kubernetes\b',
    '(?im)^\s*(from|import)\s+requests\b',
    '(?im)^\s*(from|import)\s+httpx2?\b',
    '(?im)^\s*(from|import)\s+urllib\b',
    '(?im)^\s*(from|import)\s+socket\b',
    '(?im)^\s*(from|import)\s+subprocess\b',
    '(?im)^\s*(from|import)\s+os\b',
    'kubectl',
    '(?i)kubeconfig',
    '\.kube',
    'load_kube_config'
)) {
    if ($scriptText -match $pattern) { throw "Quota replay source contains forbidden cluster, network, or process token for pattern: $pattern" }
}
Write-Output "production_scheduler_quota_replay_no_cluster_access_ok"

$quotaReplayPattern = "production-scheduler-quota-replay|provider-scheduler-quota-replay|scheduler-quota-replay"
Require-NoRegex "gitops\platform\kustomization.yaml" $quotaReplayPattern "The shared lab platform overlay must not reference scheduler quota replay."
Require-NoRegex "gitops\cells\lab-hyperv\kustomization.yaml" $quotaReplayPattern "The Hyper-V lab overlay must not reference scheduler quota replay."
Write-Output "lab_overlay_no_scheduler_quota_replay_reference_ok"
Write-Output "production_scheduler_quota_replay_seam_ok"

Remove-Item -LiteralPath $fixturePath -Force -ErrorAction SilentlyContinue
Remove-Item -LiteralPath $badScopePath -Force -ErrorAction SilentlyContinue
