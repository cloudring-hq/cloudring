[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$script = Join-Path $ProjectRoot "iac\powershell\New-PlatformHyperVLab.ps1"
$args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$script`"", "-RecreateVMs")
Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs -WindowStyle Normal
Write-Host "Started elevated Hyper-V recreate. Confirm the UAC prompt if Windows asks."
