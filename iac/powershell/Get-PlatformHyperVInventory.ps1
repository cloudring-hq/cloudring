[CmdletBinding()]
param(
    [string]$Prefix = "platform",
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$ErrorActionPreference = "Stop"
$principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Run this script from an elevated PowerShell session."
}

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "logs") | Out-Null
$log = Join-Path $ProjectRoot ("logs\hyperv-inventory-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
Start-Transcript -Path $log -Append | Out-Null

try {
    Get-VM -Name "$Prefix-*" | Sort-Object Name |
        Select-Object Name, State, Status, CPUUsage, MemoryAssigned, MemoryStartup, ProcessorCount, Uptime, Generation |
        Format-Table -AutoSize

    Get-VM -Name "$Prefix-*" | Sort-Object Name | ForEach-Object {
        Write-Host "== $($_.Name) firmware =="
        Get-VMFirmware -VMName $_.Name | Select-Object VMName, SecureBoot, SecureBootTemplate, BootOrder | Format-List
        Write-Host "== $($_.Name) network =="
        Get-VMNetworkAdapter -VMName $_.Name |
            Select-Object VMName, Name, SwitchName, Status, MacAddress, MacAddressSpoofing, IPAddresses |
            Format-List
        Write-Host "== $($_.Name) disks =="
        Get-VMHardDiskDrive -VMName $_.Name | Select-Object VMName, ControllerType, ControllerNumber, ControllerLocation, Path | Format-Table -AutoSize
        Write-Host "== $($_.Name) integration =="
        Get-VMIntegrationService -VMName $_.Name | Select-Object VMName, Name, Enabled, PrimaryStatusDescription, SecondaryStatusDescription | Format-Table -AutoSize
    }
}
finally {
    Stop-Transcript | Out-Null
}
