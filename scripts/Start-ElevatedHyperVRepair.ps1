[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$script = Join-Path $ProjectRoot "iac\powershell\Repair-PlatformVMRuntime.ps1"
$args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$script`"")
Start-Process -FilePath "powershell.exe" -ArgumentList $args -Verb RunAs -WindowStyle Normal
Write-Host "Started elevated Hyper-V VM repair. Confirm the UAC prompt if Windows asks."
