[CmdletBinding()]
param(
    [ValidateSet("Plan", "StopVm", "StartVm", "RestartVm", "WaitRecovery")]
    [string]$Action = "Plan",

    [string]$VMName = "platform-n1",
    [string]$VMNamePattern = "^platform-n[1-3]$",

    [hashtable]$NodeIps = @{
        "platform-n1" = "172.28.10.11"
        "platform-n2" = "172.28.10.12"
        "platform-n3" = "172.28.10.13"
    },

    [string]$SshUser = "platform",
    [string]$SshKeyPath = "",
    [string]$KubeReadyNodeName = "",

    [int]$SshTimeoutSeconds = 300,
    [int]$KubernetesTimeoutSeconds = 600,
    [int]$PollSeconds = 10,

    [string]$LogRoot = "",

    [switch]$Execute,
    [switch]$ConfirmDestructive,
    [switch]$SkipSshWait,
    [switch]$SkipKubernetesWait,
    [switch]$AllowDiskOperations
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-ProjectRoot {
    $scriptDir = Split-Path -Parent $PSCommandPath
    return (Resolve-Path (Join-Path $scriptDir "..\..")).Path
}

function New-LogContext {
    param([string]$Root)

    if ([string]::IsNullOrWhiteSpace($Root)) {
        $projectRoot = Resolve-ProjectRoot
        $artifacts = Join-Path $projectRoot "artifacts"
        if (Test-Path -LiteralPath $artifacts) {
            $Root = Join-Path $artifacts "hyperv-failure-drills"
        } else {
            $Root = Join-Path $projectRoot "docs\logs\hyperv-failure-drills"
        }
    }

    New-Item -ItemType Directory -Force -Path $Root | Out-Null
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $suffix = "$stamp-pid$PID"
    return [pscustomobject]@{
        Text = Join-Path $Root "$suffix-hyperv-failure-drill.log"
        Json = Join-Path $Root "$suffix-hyperv-failure-drill.ndjson"
    }
}

function Write-DrillLog {
    param(
        [Parameter(Mandatory = $true)][pscustomobject]$Log,
        [Parameter(Mandatory = $true)][string]$Level,
        [Parameter(Mandatory = $true)][string]$Message,
        [hashtable]$Data = @{}
    )

    $event = [ordered]@{
        timestamp = (Get-Date).ToString("o")
        level = $Level
        message = $Message
        data = $Data
    }

    $line = "[{0}] {1}: {2}" -f $event.timestamp, $Level, $Message
    if ($Data.Count -gt 0) {
        $line = "$line $($Data | ConvertTo-Json -Compress)"
    }

    Add-Content -LiteralPath $Log.Text -Value $line -Encoding ascii
    Add-Content -LiteralPath $Log.Json -Value ($event | ConvertTo-Json -Compress -Depth 8) -Encoding ascii
    Write-Host $line
}

function Assert-SafeVmName {
    param([string]$Name, [string]$Pattern)

    if ($Name -notmatch $Pattern) {
        throw "VMName '$Name' does not match allowed pattern '$Pattern'. Pass -VMNamePattern explicitly if this lab uses different names."
    }
}

function Assert-AdminForExecute {
    param([string]$RequestedAction, [bool]$IsExecute)

    if (-not $IsExecute -or ($RequestedAction -notin @("StopVm", "StartVm", "RestartVm"))) {
        return
    }

    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        throw "Execute mode requires an elevated PowerShell session. Re-run as Administrator."
    }
}

function Assert-DestructiveConfirmation {
    param([string]$RequestedAction, [bool]$IsExecute, [bool]$Confirmed)

    $destructiveActions = @("StopVm", "StartVm", "RestartVm")
    if (($destructiveActions -contains $RequestedAction) -and $IsExecute -and -not $Confirmed) {
        throw "Action '$RequestedAction' changes VM state. Add -ConfirmDestructive together with -Execute to run it."
    }
}

function Assert-NoDiskOperations {
    param([bool]$AllowDisks)

    if ($AllowDisks) {
        throw "Disk operations are intentionally not implemented by this script. Remove -AllowDiskOperations; use a separate reviewed script for disk drills."
    }
}

function Get-NodeIp {
    param([string]$Name, [hashtable]$Map)

    if (-not $Map.ContainsKey($Name)) {
        throw "No IP mapping for '$Name'. Pass -NodeIps with a mapping for this VM."
    }
    return [string]$Map[$Name]
}

function Get-DefaultSshKeyPath {
    $projectRoot = Resolve-ProjectRoot
    return (Join-Path $projectRoot ".ssh\platform_lab_ed25519")
}

function Get-DefaultKubernetesNodeName {
    param([string]$Name)

    if ($Name -match "^platform-(n[1-3])$") {
        return $Matches[1]
    }
    return $Name
}

function Invoke-HyperV {
    param(
        [Parameter(Mandatory = $true)][scriptblock]$Script,
        [Parameter(Mandatory = $true)][string]$Description,
        [Parameter(Mandatory = $true)][bool]$IsExecute,
        [Parameter(Mandatory = $true)][pscustomobject]$Log
    )

    if (-not $IsExecute) {
        Write-DrillLog -Log $Log -Level "DRY-RUN" -Message $Description
        return $null
    }

    Write-DrillLog -Log $Log -Level "INFO" -Message $Description
    return & $Script
}

function Invoke-SshPollCommand {
    param(
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    try {
        $output = & ssh.exe @Arguments 2>$null
        $exitCode = $LASTEXITCODE
    } catch {
        if ($_.FullyQualifiedErrorId -notmatch "^(NativeCommandError|ProgramExitedWithNonZeroCode)(,|$)") {
            throw
        }

        $output = @()
        $exitCode = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 255 }
    }

    return [pscustomobject]@{
        Output = $output
        ExitCode = $exitCode
    }
}

function Wait-ForSsh {
    param(
        [string]$Ip,
        [string]$User,
        [string]$KeyPath,
        [int]$TimeoutSeconds,
        [int]$SleepSeconds,
        [pscustomobject]$Log
    )

    if (-not (Test-Path -LiteralPath $KeyPath)) {
        throw "SSH key not found at '$KeyPath'."
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $sshArgs = @(
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=5",
        "$User@$Ip",
        "echo ssh-ready"
    )

    while ((Get-Date) -lt $deadline) {
        $sshResult = Invoke-SshPollCommand -Arguments $sshArgs
        if ($sshResult.ExitCode -eq 0 -and ($sshResult.Output -join "`n") -match "ssh-ready") {
            Write-DrillLog -Log $Log -Level "INFO" -Message "SSH is ready" -Data @{ ip = $Ip; user = $User }
            return
        }

        Write-DrillLog -Log $Log -Level "INFO" -Message "Waiting for SSH" -Data @{ ip = $Ip; sleepSeconds = $SleepSeconds }
        Start-Sleep -Seconds $SleepSeconds
    }

    throw "Timed out waiting for SSH on $Ip after $TimeoutSeconds seconds."
}

function Wait-ForKubernetesNode {
    param(
        [string]$Ip,
        [string]$User,
        [string]$KeyPath,
        [string]$NodeName,
        [int]$TimeoutSeconds,
        [int]$SleepSeconds,
        [pscustomobject]$Log
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    $remoteCommand = "sudo k3s kubectl get node $NodeName --no-headers"
    $sshArgs = @(
        "-i", $KeyPath,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=5",
        "$User@$Ip",
        $remoteCommand
    )

    while ((Get-Date) -lt $deadline) {
        $sshResult = Invoke-SshPollCommand -Arguments $sshArgs
        if ($sshResult.ExitCode -eq 0 -and (($sshResult.Output -join "`n") -match "\sReady\s")) {
            Write-DrillLog -Log $Log -Level "INFO" -Message "Kubernetes node is Ready" -Data @{ node = $NodeName; ip = $Ip }
            return
        }

        Write-DrillLog -Log $Log -Level "INFO" -Message "Waiting for Kubernetes node readiness" -Data @{ node = $NodeName; ip = $Ip; sleepSeconds = $SleepSeconds }
        Start-Sleep -Seconds $SleepSeconds
    }

    throw "Timed out waiting for Kubernetes node '$NodeName' to become Ready after $TimeoutSeconds seconds."
}

$log = New-LogContext -Root $LogRoot
$dryRun = -not [bool]$Execute
$nodeName = if ([string]::IsNullOrWhiteSpace($KubeReadyNodeName)) { Get-DefaultKubernetesNodeName -Name $VMName } else { $KubeReadyNodeName }
if ([string]::IsNullOrWhiteSpace($SshKeyPath)) {
    $SshKeyPath = Get-DefaultSshKeyPath
}

try {
    Assert-NoDiskOperations -AllowDisks ([bool]$AllowDiskOperations)
    Assert-SafeVmName -Name $VMName -Pattern $VMNamePattern
    Assert-DestructiveConfirmation -RequestedAction $Action -IsExecute ([bool]$Execute) -Confirmed ([bool]$ConfirmDestructive)
    Assert-AdminForExecute -RequestedAction $Action -IsExecute ([bool]$Execute)

    $ip = Get-NodeIp -Name $VMName -Map $NodeIps
    Write-DrillLog -Log $log -Level "INFO" -Message "Hyper-V failure drill initialized" -Data @{
        action = $Action
        vmName = $VMName
        ip = $ip
        dryRun = $dryRun
        logText = $log.Text
        logJson = $log.Json
    }

    if ($Action -eq "Plan") {
        Write-DrillLog -Log $log -Level "DRY-RUN" -Message "Planned Hyper-V inventory check" -Data @{ command = "Get-VM -Name $VMName" }
        Write-DrillLog -Log $log -Level "DRY-RUN" -Message "No VM state changes requested"
        return
    }

    if ($Action -in @("StopVm", "RestartVm")) {
        Invoke-HyperV -Description "Stop VM '$VMName'" -IsExecute ([bool]$Execute) -Log $log -Script {
            Stop-VM -Name $VMName -Force
        } | Out-Null
    }

    if ($Action -eq "RestartVm") {
        Invoke-HyperV -Description "Start VM '$VMName' after stop" -IsExecute ([bool]$Execute) -Log $log -Script {
            Start-VM -Name $VMName
        } | Out-Null
    }

    if ($Action -eq "StartVm") {
        Invoke-HyperV -Description "Start VM '$VMName'" -IsExecute ([bool]$Execute) -Log $log -Script {
            Start-VM -Name $VMName
        } | Out-Null
    }

    if ($Action -in @("WaitRecovery", "StartVm", "RestartVm")) {
        if ($dryRun) {
            Write-DrillLog -Log $log -Level "DRY-RUN" -Message "Planned SSH recovery wait" -Data @{ ip = $ip; key = $SshKeyPath; user = $SshUser }
            Write-DrillLog -Log $log -Level "DRY-RUN" -Message "Planned Kubernetes node readiness wait" -Data @{ node = $nodeName }
            return
        }

        if (-not $SkipSshWait) {
            Wait-ForSsh -Ip $ip -User $SshUser -KeyPath $SshKeyPath -TimeoutSeconds $SshTimeoutSeconds -SleepSeconds $PollSeconds -Log $log
        }

        if (-not $SkipKubernetesWait) {
            Wait-ForKubernetesNode -Ip $ip -User $SshUser -KeyPath $SshKeyPath -NodeName $nodeName -TimeoutSeconds $KubernetesTimeoutSeconds -SleepSeconds $PollSeconds -Log $log
        }
    }

    Write-DrillLog -Log $log -Level "INFO" -Message "Hyper-V failure drill completed" -Data @{ action = $Action; vmName = $VMName; dryRun = $dryRun }
} catch {
    Write-DrillLog -Log $log -Level "ERROR" -Message $_.Exception.Message -Data @{ action = $Action; vmName = $VMName; dryRun = $dryRun }
    throw
}
