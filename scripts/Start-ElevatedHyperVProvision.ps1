[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$script = Join-Path $ProjectRoot "iac\powershell\New-PlatformHyperVLab.ps1"
if (-not (Test-Path -LiteralPath $script)) {
    throw "Provisioning script not found: $script"
}

$args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$script`"")
Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs -WindowStyle Normal
Write-Host "Started elevated provisioning. Confirm the UAC prompt if Windows asks."
