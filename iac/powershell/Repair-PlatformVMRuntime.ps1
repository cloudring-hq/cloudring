[CmdletBinding()]
param(
    [string]$Prefix = "platform",
    [Int64]$NodeMemoryBytes = 7GB,
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$ErrorActionPreference = "Stop"

$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell session."
}

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "logs") | Out-Null
$log = Join-Path $ProjectRoot ("logs\hyperv-repair-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
Start-Transcript -Path $log -Append | Out-Null

try {
    foreach ($name in @("$Prefix-n1", "$Prefix-n2", "$Prefix-n3")) {
        $vm = Get-VM -Name $name -ErrorAction SilentlyContinue
        if (-not $vm) {
            Write-Host "VM $name not found"
            continue
        }

        Write-Host "Reconciling $name"
        if ($vm.State -ne "Off") {
            try {
                Stop-VM -Name $name -TurnOff -Force
            }
            catch {
                Write-Host "Stop-VM failed for $name, trying to terminate vmwp worker for this VM only"
                $id = $vm.Id.Guid.ToString()
                $workers = Get-CimInstance Win32_Process -Filter "Name = 'vmwp.exe'" |
                    Where-Object { $_.CommandLine -match $id }
                foreach ($worker in $workers) {
                    Write-Host "Stopping vmwp.exe PID $($worker.ProcessId) for $name"
                    Stop-Process -Id $worker.ProcessId -Force
                }
                Start-Sleep -Seconds 5
            }
        }
        $vm = Get-VM -Name $name
        if ($vm.State -ne "Off") {
            throw "$name is still not Off after forced stop path; current state: $($vm.State)"
        }
        Set-VMMemory -VMName $name -DynamicMemoryEnabled $false -StartupBytes $NodeMemoryBytes
        Set-VMProcessor -VMName $name -Count 4 -ExposeVirtualizationExtensions $true
        Set-VMNetworkAdapter -VMName $name -MacAddressSpoofing On
        Start-VM -Name $name
    }
}
finally {
    Stop-Transcript | Out-Null
}
