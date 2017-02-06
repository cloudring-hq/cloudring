param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$OutputPath = "",
    [string]$SshUser = "platform",
    [string]$SshHost = "172.28.10.11",
    [string]$SshKey = "",
    [string]$KnownHosts = "",
    [string]$VmPrefix = "platform",
    [string]$PortalRuntimeEvidenceFile = "",
    [int]$TimeoutSeconds = 15
)

$ErrorActionPreference = "Stop"

if (-not $SshKey) { $SshKey = Join-Path $Root ".ssh\platform_lab_ed25519" }
if (-not $KnownHosts) { $KnownHosts = Join-Path $Root ".ssh\known_hosts" }
if (-not $OutputPath) {
    $OutputPath = Join-Path $Root ".omo\ulw-loop\evidence\live-larger-cell-capk-oidc-preflight.json"
}
if (-not $PortalRuntimeEvidenceFile) {
    $PortalRuntimeEvidenceFile = Join-Path $Root ".omo\ulw-loop\evidence\production-capk-oidc-runtime-live-evidence.json"
}

. (Join-Path $PSScriptRoot "live-larger-cell-capk-oidc-preflight-lib.ps1")

$checks = New-Object System.Collections.Generic.List[object]
$facts = [ordered]@{}

$os = Get-CimInstance Win32_OperatingSystem
$freeMemoryBytes = [int64]$os.FreePhysicalMemory * 1KB
$facts.host = [ordered]@{
    totalMemoryBytes = [int64]$os.TotalVisibleMemorySize * 1KB
    freeMemoryBytes = $freeMemoryBytes
}
$checks.Add((New-Check "windows_host_memory" ($(if ($freeMemoryBytes -ge 8GB) { "pass" } else { "blocker" })) "Free host memory must be enough for live larger-cell promotion." $facts.host))

try {
    $vmHost = Get-VMHost
    $vms = @(Get-VM -Name "$VmPrefix-*" | Sort-Object Name)
    $facts.hyperv = [ordered]@{
        logicalProcessorCount = $vmHost.LogicalProcessorCount
        memoryCapacityBytes = $vmHost.MemoryCapacity
        platformVmCount = $vms.Count
        platformVms = @($vms | ForEach-Object {
            [ordered]@{
                name = $_.Name
                state = $_.State.ToString()
                processorCount = $_.ProcessorCount
                memoryAssignedBytes = $_.MemoryAssigned
            }
        })
    }
    $running = @($vms | Where-Object { $_.State -eq "Running" })
    $checks.Add((New-Check "hyperv_management_cell" ($(if ($running.Count -ge 3) { "pass" } else { "blocker" })) "At least three Hyper-V management VMs must be running." $facts.hyperv))
} catch {
    $checks.Add((New-Check "hyperv_management_cell" "blocker" $_.Exception.Message))
}

$kubectlCommand = Get-Command kubectl -ErrorAction SilentlyContinue
$checks.Add((New-Check "windows_kubectl_command" ($(if ($kubectlCommand) { "pass" } else { "warning" })) "Windows kubectl is optional because SSH fallback is supported." @{ source = $kubectlCommand.Source }))

$bashCommand = Get-Command bash -ErrorAction SilentlyContinue
if ($bashCommand) {
    $bashProbe = Invoke-ProcessWithTimeout "bash.exe" @("-lc", "timeout 8s sudo -n k3s kubectl get providers -A") 12
    $facts.wslBashProbe = $bashProbe
    $checks.Add((New-Check "wsl_bash_kubectl_path" ($(if ($bashProbe.exitCode -eq 0 -and -not $bashProbe.timedOut) { "pass" } elseif ($bashProbe.timedOut) { "blocker" } else { "warning" })) "WSL/bash kubectl path must not be used for live evidence if it times out." $bashProbe))
} else {
    $checks.Add((New-Check "wsl_bash_kubectl_path" "warning" "bash.exe is unavailable; SSH fallback is required."))
}

$nodes = Invoke-SshKubectlJson "get nodes"
if (-not $nodes.ok) {
    $checks.Add((New-Check "ssh_management_kubectl" "blocker" "SSH sudo k3s kubectl failed." $nodes.result))
} else {
    $readyNodes = @($nodes.json.items | Where-Object {
        @($_.status.conditions | Where-Object { $_.type -eq "Ready" -and $_.status -eq "True" }).Count -gt 0
    })
    $facts.managementNodesReady = $readyNodes.Count
    $checks.Add((New-Check "ssh_management_kubectl" "pass" "SSH sudo k3s kubectl is available." @{ readyNodes = $readyNodes.Count }))
    $checks.Add((New-Check "management_nodes_ready" ($(if ($readyNodes.Count -ge 3) { "pass" } else { "blocker" })) "Live evidence requires at least three Ready management nodes." @{ readyNodes = $readyNodes.Count }))
}

$providers = Invoke-SshKubectlJson "get providers -A"
if ($providers.ok) {
    $providerNames = @($providers.json.items | ForEach-Object { "$($_.metadata.name):$($_.type):$($_.version)" })
    $facts.providers = $providerNames
    $requiredProviders = @("cluster-api", "infrastructure-kubevirt", "bootstrap-kubeadm", "control-plane-kubeadm")
    $missing = @($requiredProviders | Where-Object { $name = $_; -not (@($providerNames | Where-Object { $_ -match $name }).Count) })
    $checks.Add((New-Check "cluster_api_capk_providers" ($(if ($missing.Count -eq 0) { "pass" } else { "blocker" })) "Cluster API and CAPK providers must be installed." @{ providers = $providerNames; missing = $missing }))
} else {
    $checks.Add((New-Check "cluster_api_capk_providers" "blocker" "Cannot read Cluster API providers." $providers.result))
}

$clusters = Invoke-SshKubectlJson "get clusters.cluster.x-k8s.io -A"
if ($clusters.ok) {
    $clusterSummaries = @($clusters.json.items | ForEach-Object {
        [ordered]@{
            namespace = $_.metadata.namespace
            name = $_.metadata.name
            phase = $_.status.phase
            controlPlaneDesired = Convert-ToIntOrZero $_.status.controlPlaneDesiredReplicas
            controlPlaneReady = Convert-ToIntOrZero $_.status.controlPlaneReadyReplicas
            workersDesired = Convert-ToIntOrZero $_.status.workersDesiredReplicas
            workersReady = Convert-ToIntOrZero $_.status.workersReadyReplicas
        }
    })
    $facts.tenantClusters = $clusterSummaries
    $larger = @($clusterSummaries | Where-Object { $_.controlPlaneReady -ge 3 -and $_.workersReady -ge 1 })
    $checks.Add((New-Check "larger_cell_tenant_cluster_shape" ($(if ($larger.Count -gt 0) { "pass" } else { "blocker" })) "Need a live tenant cluster with 3 ready control-plane replicas and at least one ready worker." @{ clusters = $clusterSummaries }))
} else {
    $checks.Add((New-Check "larger_cell_tenant_cluster_shape" "blocker" "Cannot read tenant CAPI clusters." $clusters.result))
}

$claims = Invoke-SshKubectlJson "get kubernetesclusterclaims -A"
if ($claims.ok) {
    $claimSummaries = @($claims.json.items | ForEach-Object {
        [ordered]@{
            namespace = $_.metadata.namespace
            name = $_.metadata.name
            phase = $_.status.phase
            apiEndpoint = $_.status.apiEndpoint
            kubeconfigSecret = $_.status.kubeconfigSecret
        }
    })
    $facts.claims = $claimSummaries
    $readyClaims = @($claimSummaries | Where-Object { $_.phase -eq "Ready" -and $_.kubeconfigSecret })
    $checks.Add((New-Check "tenant_kubeconfig_handoff" ($(if ($readyClaims.Count -gt 0) { "pass" } else { "blocker" })) "At least one tenant claim must expose a kubeconfig handoff." @{ claims = $claimSummaries }))
} else {
    $checks.Add((New-Check "tenant_kubeconfig_handoff" "blocker" "Cannot read KubernetesClusterClaim objects." $claims.result))
}

$vms = Invoke-SshKubectlJson "get vmi -A"
if ($vms.ok) {
    $vmiSummaries = @($vms.json.items | ForEach-Object {
        [ordered]@{
            namespace = $_.metadata.namespace
            name = $_.metadata.name
            phase = $_.status.phase
            nodeName = $_.status.nodeName
            liveMigratable = $_.status.conditions | Where-Object { $_.type -eq "LiveMigratable" } | Select-Object -First 1 -ExpandProperty status
        }
    })
    $facts.virtualMachineInstances = $vmiSummaries
    $tenantCp = @($vmiSummaries | Where-Object { $_.name -match "control-plane" -and $_.phase -eq "Running" })
    $checks.Add((New-Check "tenant_control_plane_vmis" ($(if ($tenantCp.Count -ge 3) { "pass" } else { "blocker" })) "Need three running tenant control-plane VMIs for larger-cell HA evidence." @{ controlPlaneVmis = $tenantCp }))
} else {
    $checks.Add((New-Check "tenant_control_plane_vmis" "blocker" "Cannot read KubeVirt VMIs." $vms.result))
}

$deploys = Invoke-SshKubectlJson "get deploy -A"
if ($deploys.ok) {
    $portalDeployments = @($deploys.json.items | Where-Object { $_.metadata.name -match "provider-portal|portal" })
    $portalFacts = @($portalDeployments | ForEach-Object {
        $container = $_.spec.template.spec.containers | Select-Object -First 1
        $namespace = $_.metadata.namespace
        $authMode = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_WRITE_AUTH_MODE") $namespace
        $issuer = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_ISSUER") $namespace
        $jwksUri = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_JWKS_URI") $namespace
        $allowedAlgorithms = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_ALLOWED_ALGORITHMS") $namespace
        $hs256Secret = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_HS256_SECRET") $namespace
        $groupsClaim = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_GROUPS_CLAIM") $namespace
        $namespacesClaim = Resolve-EnvSetting (Read-EnvSetting $container "PORTAL_JWT_NAMESPACES_CLAIM") $namespace
        [ordered]@{
            namespace = $namespace
            name = $_.metadata.name
            authMode = $authMode.resolvedValue
            authModeFrom = $authMode.valueFrom
            authModeResolvedFrom = $authMode.resolvedFrom
            authModeResolveError = $authMode.resolveError
            issuer = $issuer.resolvedValue
            issuerFrom = $issuer.valueFrom
            issuerResolvedFrom = $issuer.resolvedFrom
            issuerResolveError = $issuer.resolveError
            jwksUri = $jwksUri.resolvedValue
            jwksUriFrom = $jwksUri.valueFrom
            jwksUriResolvedFrom = $jwksUri.resolvedFrom
            jwksUriResolveError = $jwksUri.resolveError
            allowedAlgorithms = $allowedAlgorithms.resolvedValue
            allowedAlgorithmsFrom = $allowedAlgorithms.valueFrom
            allowedAlgorithmsResolvedFrom = $allowedAlgorithms.resolvedFrom
            allowedAlgorithmsResolveError = $allowedAlgorithms.resolveError
            hs256SecretPresent = $hs256Secret.present
            hs256SecretFrom = $hs256Secret.valueFrom
            hs256SecretResolvedFrom = $hs256Secret.resolvedFrom
            hs256SecretResolveError = $hs256Secret.resolveError
            groupsClaim = $groupsClaim.value
            groupsClaimFrom = $groupsClaim.valueFrom
            namespacesClaim = $namespacesClaim.value
            namespacesClaimFrom = $namespacesClaim.valueFrom
        }
    })
    $facts.portalIdentity = $portalFacts
    $oidcReady = @($portalFacts | Where-Object {
        $_.authMode -eq "oidc-jwks" -and $_.issuer -and $_.jwksUri -and $_.allowedAlgorithms -and -not $_.hs256SecretPresent -and $_.allowedAlgorithms -notmatch "HS256"
    })
    $checks.Add((New-Check "provider_portal_oidc_jwks_runtime" ($(if ($oidcReady.Count -gt 0) { "pass" } else { "blocker" })) "Provider portal runtime must use external oidc-jwks without lab HS256." @{ portalIdentity = $portalFacts }))
} else {
    $checks.Add((New-Check "provider_portal_oidc_jwks_runtime" "blocker" "Cannot read provider portal deployments." $deploys.result))
}

$runtimeEvidence = [ordered]@{ path = $PortalRuntimeEvidenceFile; exists = (Test-Path -LiteralPath $PortalRuntimeEvidenceFile -PathType Leaf); accepted = $false; markers = @() }
if ($runtimeEvidence.exists) {
    try {
        $evidenceJson = Get-Content -LiteralPath $PortalRuntimeEvidenceFile -Raw | ConvertFrom-Json
        $runtimeEvidence.markers = @($evidenceJson.markers)
        $runtimeEvidence.accepted = @($runtimeEvidence.markers) -contains "production_capk_oidc_runtime_live_evidence_ok"
    } catch {
        $runtimeEvidence.parseError = $_.Exception.Message
    }
}
$checks.Add((New-Check "provider_portal_oidc_token_runtime" ($(if ($runtimeEvidence.accepted) { "pass" } else { "blocker" })) "Deployment env is only a precondition; final OIDC readiness requires accepted runtime token/JWKS evidence." $runtimeEvidence))

$blockers = @($checks | Where-Object { $_.status -eq "blocker" })
$status = if ($blockers.Count -eq 0) { "liveEvidenceReady" } else { "blocked" }
$markers = if ($status -eq "liveEvidenceReady") {
    @("live_larger_cell_capk_oidc_preflight_ok")
} else {
    @("live_larger_cell_capk_oidc_preflight_blocked", "live_larger_cell_capk_oidc_no_aggregate_completion_claim")
}
$checkArray = @($checks.ToArray())
$blockerArray = @($blockers | ForEach-Object { [ordered]@{ name = $_.name; message = $_.message; data = $_.data } })
$report = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    status = $status
    finalAggregateClaim = $false
    markers = @($markers)
    checks = $checkArray
    facts = $facts
    blockers = $blockerArray
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPath) | Out-Null
$json = $report | ConvertTo-Json -Depth 30
[System.IO.File]::WriteAllText($OutputPath, $json, (New-Object System.Text.UTF8Encoding($false)))

if ($status -eq "liveEvidenceReady") {
    Write-Output "live_larger_cell_capk_oidc_preflight_ok"
} else {
    Write-Output "live_larger_cell_capk_oidc_preflight_blocked"
    foreach ($blocker in $blockers) { Write-Output ("blocker: {0}" -f $blocker.name) }
    Write-Output "live_larger_cell_capk_oidc_no_aggregate_completion_claim"
}
Write-Output ("report: {0}" -f $OutputPath)
