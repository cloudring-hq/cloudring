[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform"
)

$controllerPath = Join-Path $ProjectRoot "iac\kubernetes\provider-controller\controller.py"
$templatePath = Join-Path $ProjectRoot "iac\kubernetes\provider-controller\controller.yaml"
$outPath = Join-Path $ProjectRoot "iac\kubernetes\provider-controller\rendered-controller.yaml"

$controller = Get-Content -LiteralPath $controllerPath
$indented = ($controller | ForEach-Object { "    $_" }) -join "`n"
$template = Get-Content -LiteralPath $templatePath -Raw
$rendered = $template.Replace("    PLACEHOLDER", $indented)
Set-Content -LiteralPath $outPath -Value $rendered -Encoding ascii
Write-Host $outPath
