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
    if ($Actual -ne $Expected) {
        throw "$Message Expected '$Expected', got '$Actual'."
    }
}

function Require-Contains {
    param([Parameter(Mandatory = $true)][string[]]$Values, [Parameter(Mandatory = $true)][string]$Expected, [Parameter(Mandatory = $true)][string]$Message)
    if ($Expected -notin $Values) {
        throw "$Message Missing '$Expected'."
    }
}

function Require-NoRegex {
    param([Parameter(Mandatory = $true)][string]$RelativePath, [Parameter(Mandatory = $true)][string]$Pattern, [Parameter(Mandatory = $true)][string]$Message)
    $text = Get-Content -LiteralPath (Require-File $RelativePath) -Raw
    if ($text -match $Pattern) { throw $Message }
}

$scriptRelative = "iac\scripts\production-scheduler-runtime-admission-seam.py"
$scriptPath = Require-File $scriptRelative
$python = Resolve-Python
$fixturePath = Join-Path ([System.IO.Path]::GetTempPath()) ("provider-scheduler-runtime-admission-" + [System.Guid]::NewGuid().ToString("N") + ".json")

& $python -m py_compile $scriptPath
if ($LASTEXITCODE -ne 0) { throw "py_compile failed for $scriptRelative" }
Write-Output "python_py_compile_ok"

$fixtureJson = @'
{
  "canaryScope": "provider-scheduler-runtime-canary",
  "cases": [
    {"name":"vm-accepted","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-a","uid":"uid-vm-a","generation":3,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":1000,"memoryMi":1024,"failureDomains":{"region":"euw"}}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"usedVMs":2,"allowedKinds":["VirtualMachineClaim","KubernetesClusterClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"reservedClaims":1,"failureDomains":{"region":"euw","zone":"a"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]},{"name":"cell-b","phase":"Ready","availableCpuMillicores":5000,"availableMemoryMi":8192,"reservedClaims":0,"failureDomains":{"region":"euw","zone":"b"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"tenant-cluster-accepted","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"KubernetesClusterClaim","namespace":"tenant-a","name":"cluster-a","uid":"uid-cluster-a","generation":5,"projectRef":"tenant-a","serviceClass":"ha-tenant-kubernetes","cpuMillicores":2000,"memoryMi":4096,"controlPlaneReplicas":3,"failureDomains":{"region":"euw"}}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"usedTenantClusters":1,"allowedKinds":["VirtualMachineClaim","KubernetesClusterClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3500,"availableMemoryMi":6144,"reservedClaims":2,"failureDomains":{"region":"euw","zone":"a"},"serviceClasses":[{"name":"ha-tenant-kubernetes","kind":"KubernetesClusterClaim","minControlPlaneReplicas":3,"maxControlPlaneReplicas":5}]},{"name":"cell-b","phase":"Ready","availableCpuMillicores":7000,"availableMemoryMi":12288,"reservedClaims":0,"failureDomains":{"region":"euw","zone":"b"},"serviceClasses":[{"name":"ha-tenant-kubernetes","kind":"KubernetesClusterClaim","minControlPlaneReplicas":3,"maxControlPlaneReplicas":5}]}]},
    {"name":"malformed-missing-fixture-fields","review":{"kind":"SchedulerAdmissionReview","spec":{"namespace":"tenant-a","name":"bad"}},"project":{"name":"tenant-a","quotaCpuMillicores":1,"quotaMemoryMi":1,"quotaVMs":1,"quotaTenantClusters":1,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[]},
    {"name":"malformed-boolean-numbers","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-bool","uid":"uid-bool","generation":true,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":true,"memoryMi":true}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"unknown-cell","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-missing-cell","uid":"uid-missing-cell","generation":1,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":500,"memoryMi":512,"capacityCell":"missing-cell"}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim","KubernetesClusterClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"insufficient-quota","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-quota","uid":"uid-quota","generation":1,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":500,"memoryMi":512}},"project":{"name":"tenant-a","quotaCpuMillicores":1000,"quotaMemoryMi":1024,"quotaVMs":1,"quotaTenantClusters":1,"usedCpuMillicores":800,"usedMemoryMi":256,"usedVMs":0,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"stale-capacity","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-stale","uid":"uid-stale","generation":1,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":500,"memoryMi":512}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","stale":true,"availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"missing-reservation-lock","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-lock","uid":"uid-lock","generation":1,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":500,"memoryMi":512}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":false},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]},
    {"name":"tenant-policy-denial","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"KubernetesClusterClaim","namespace":"tenant-a","name":"cluster-denied","uid":"uid-denied","generation":1,"projectRef":"tenant-a","serviceClass":"ha-tenant-kubernetes","cpuMillicores":1000,"memoryMi":2048,"controlPlaneReplicas":3}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"ha-tenant-kubernetes","kind":"KubernetesClusterClaim","minControlPlaneReplicas":3,"maxControlPlaneReplicas":5}]}]},
    {"name":"unsupported-request-kind","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"Volume","namespace":"tenant-a","name":"volume-unsupported","uid":"uid-volume","generation":1,"projectRef":"tenant-a","serviceClass":"premium-volume","cpuMillicores":0,"memoryMi":0}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":24000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["Volume"]},"locks":{"projectQuota":true,"capacity":true},"cells":[]},
    {"name":"insufficient-capacity","review":{"kind":"SchedulerAdmissionReview","spec":{"requestKind":"VirtualMachineClaim","namespace":"tenant-a","name":"vm-too-large","uid":"uid-large","generation":1,"projectRef":"tenant-a","serviceClass":"small-vm","cpuMillicores":9000,"memoryMi":32768}},"project":{"name":"tenant-a","quotaCpuMillicores":12000,"quotaMemoryMi":64000,"quotaVMs":10,"quotaTenantClusters":4,"allowedKinds":["VirtualMachineClaim"]},"locks":{"projectQuota":true,"capacity":true},"cells":[{"name":"cell-a","phase":"Ready","availableCpuMillicores":3000,"availableMemoryMi":4096,"failureDomains":{"region":"euw"},"serviceClasses":[{"name":"small-vm","kind":"VirtualMachineClaim"}]}]}
  ]
}
'@
[System.IO.File]::WriteAllText($fixturePath, $fixtureJson, [System.Text.UTF8Encoding]::new($false))

$output = & $python $scriptPath $fixturePath
if ($LASTEXITCODE -ne 0) { throw "Adapter execution failed for $scriptRelative" }

$jsonLine = $output | Where-Object { $_.StartsWith("ADMISSION_JSON:") } | Select-Object -First 1
if (-not $jsonLine) { throw "Adapter did not emit ADMISSION_JSON." }
$payload = $jsonLine.Substring("ADMISSION_JSON:".Length) | ConvertFrom-Json

foreach ($marker in @(
    "provider_scheduler_fixture_parse_ok",
    "production_scheduler_runtime_admission_seam_ok",
    "production_scheduler_runtime_fail_closed_ok",
    "production_scheduler_runtime_no_cluster_access_ok",
    "lab_overlay_no_scheduler_runtime_reference_ok"
)) {
    if ($marker -notin $output) { throw "Adapter output missing marker: $marker" }
}
Write-Output "provider_scheduler_fixture_parse_ok"

Require-Equal $payload.adapterMode "disabled-by-default-scheduler-admission-seam" "Adapter mode mismatch."
Require-Equal $payload.inputMode "json-fixtures" "Input mode mismatch."
Require-Equal $payload.preflightGate.canaryScope "provider-scheduler-runtime-canary" "Canary scope mismatch."
Require-Equal $payload.accepted.Count 2 "Accepted scenario count mismatch."

$acceptedKinds = @($payload.accepted | ForEach-Object { $_.requestKind })
Require-Contains $acceptedKinds "VirtualMachineClaim" "Accepted kinds missing VM claim."
Require-Contains $acceptedKinds "KubernetesClusterClaim" "Accepted kinds missing tenant cluster claim."
foreach ($scenario in $payload.accepted) {
    Require-Equal $scenario.reservationIntents.Count 1 "Accepted scenario must emit one ReservationIntent."
    Require-Equal $scenario.quotaAdmissionDecision.allowed $true "Accepted quota decision must allow."
    Require-Equal $scenario.admissionJournal.decision "Admitted" "Accepted journal decision mismatch."
    Require-Equal $scenario.statusPatch.phase "Admitted" "Accepted status patch phase mismatch."
    foreach ($stage in @("Filter", "Score", "Reserve", "Permit")) {
        Require-Contains ([string[]]$scenario.pipeline) $stage "Accepted scenario pipeline missing stage."
    }
}
$vmAccepted = $payload.accepted | Where-Object { $_.name -eq "vm-accepted" } | Select-Object -First 1
$clusterAccepted = $payload.accepted | Where-Object { $_.name -eq "tenant-cluster-accepted" } | Select-Object -First 1
Require-Equal $vmAccepted.quotaAdmissionDecision.quotaSnapshot.vms 3 "Accepted VM quota snapshot must include prior VM usage plus the admitted VM."
Require-Equal $clusterAccepted.quotaAdmissionDecision.quotaSnapshot.tenantClusters 2 "Accepted cluster quota snapshot must include prior cluster usage plus the admitted cluster."
Write-Output "production_scheduler_runtime_admission_seam_ok"

$expectedReasons = @(
    "MalformedSchedulerFixture",
    "CapacityCellNotFound",
    "ProjectQuotaExceeded",
    "StaleCapacitySnapshot",
    "ReservationLockUnavailable",
    "TenantPolicyDenied",
    "UnsupportedRequestKind",
    "InsufficientCapacity"
)
Require-Equal $payload.failClosed.Count 9 "Fail-closed scenario count mismatch."
foreach ($scenario in $payload.failClosed) {
    Require-Equal $scenario.reservationIntents.Count 0 "Fail-closed scenario emitted ReservationIntent."
    Require-Equal $scenario.quotaAdmissionDecision.allowed $false "Fail-closed quota decision must reject."
    if ($scenario.statusPatch.phase -notin @("Rejected", "Degraded")) {
        throw "Fail-closed status phase must be Rejected or Degraded; got '$($scenario.statusPatch.phase)'."
    }
}
$actualReasons = @($payload.failClosed | ForEach-Object { $_.statusPatch.admission.reason })
foreach ($reason in $expectedReasons) {
    Require-Contains $actualReasons $reason "Fail-closed reason set is incomplete."
}
$booleanNumbers = $payload.failClosed | Where-Object { $_.name -eq "malformed-boolean-numbers" } | Select-Object -First 1
if (-not $booleanNumbers) { throw "Boolean numeric fields must produce a fail-closed malformed case." }
Require-Equal $booleanNumbers.statusPatch.admission.reason "MalformedSchedulerFixture" "Boolean numeric fields must be rejected as malformed."
Write-Output "production_scheduler_runtime_fail_closed_ok"

Require-Equal $payload.clusterAccess.mode "offline" "Cluster access mode mismatch."
Require-Equal $payload.clusterAccess.commandsInvoked.Count 0 "Adapter must not invoke commands."
Require-Equal $payload.clusterAccess.networkClients.Count 0 "Adapter must not use network clients."
Require-Equal $payload.clusterAccess.configFilesRead.Count 0 "Adapter must not read cluster config files."

$scriptText = Get-Content -LiteralPath $scriptPath -Raw
foreach ($pattern in @(
    '(?im)^\s*(from|import)\s+kubernetes\b',
    '(?im)^\s*(from|import)\s+requests\b',
    '(?im)^\s*(from|import)\s+httpx2?\b',
    '(?im)^\s*(from|import)\s+urllib\b',
    '(?im)^\s*(from|import)\s+socket\b',
    '(?im)^\s*(from|import)\s+subprocess\b',
    'kubectl',
    '(?i)kubeconfig',
    '\.kube',
    'load_kube_config'
)) {
    if ($scriptText -match $pattern) {
        throw "Adapter source contains forbidden cluster, network, or process token for pattern: $pattern"
    }
}
Write-Output "production_scheduler_runtime_no_cluster_access_ok"

$runtimePattern = "production-scheduler-runtime|provider-scheduler-runtime-controller|production-scheduler-runtime-admission-seam"
Require-NoRegex "gitops\platform\kustomization.yaml" $runtimePattern "The shared lab platform overlay must not reference the scheduler runtime seam."
Require-NoRegex "gitops\cells\lab-hyperv\kustomization.yaml" $runtimePattern "The Hyper-V lab overlay must not reference the scheduler runtime seam."
Write-Output "lab_overlay_no_scheduler_runtime_reference_ok"
Write-Output "production_scheduler_runtime_admission_seam_ok"
Remove-Item -LiteralPath $fixturePath -Force -ErrorAction SilentlyContinue
