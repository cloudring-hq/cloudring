[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$script = Join-Path $ProjectRoot "iac\powershell\Get-PlatformHyperVInventory.ps1"
$args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$script`"")
Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs -WindowStyle Normal
Write-Host "Started elevated Hyper-V inventory. Confirm the UAC prompt if Windows asks."
