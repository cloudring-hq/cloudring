param(
    [string]$BinDir = "$env:USERPROFILE\bin",
    [string[]]$RemoteHosts = @(),
    [string]$SshKey = ".ssh\platform_lab_ed25519",
    [string]$RemoteUser = "platform"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$Versions = @{
    Kubernetes = "v1.35.5"
    Helm = "v3.21.2"
    Flux = "v2.8.8"
    ClusterApi = "v1.13.2"
    Kubeconform = "v0.8.0"
    Conftest = "v0.68.2"
    Yq = "v4.53.3"
    Jq = "jq-1.8.2"
    KubeVirt = "v1.8.4"
}

function Invoke-Download {
    param([string]$Url, [string]$OutFile)
    Invoke-WebRequest -UseBasicParsing -Headers @{ "User-Agent" = "platform-live-verification-tooling" } -Uri $Url -OutFile $OutFile
}

function Get-GitHubAssetUrl {
    param([string]$Repo, [string]$Tag, [string]$Pattern)
    $release = Invoke-RestMethod -Headers @{ "User-Agent" = "platform-live-verification-tooling" } -Uri "https://api.github.com/repos/$Repo/releases/tags/$Tag"
    $asset = $release.assets | Where-Object { $_.name -match $Pattern } | Select-Object -First 1
    if (-not $asset) { throw "No asset matching '$Pattern' in $Repo $Tag" }
    $asset.browser_download_url
}

function Install-ZipAsset {
    param([string]$Url, [string]$ExecutableName, [string]$TmpDir)
    $zip = Join-Path $TmpDir "$ExecutableName.zip"
    $extract = Join-Path $TmpDir $ExecutableName
    Invoke-Download $Url $zip
    Expand-Archive -Force -Path $zip -DestinationPath $extract
    $exe = Get-ChildItem -Path $extract -Recurse -Filter $ExecutableName | Select-Object -First 1
    if (-not $exe) { throw "Missing $ExecutableName in $Url" }
    Copy-Item -Force $exe.FullName (Join-Path $BinDir $ExecutableName)
}

function Install-DirectAsset {
    param([string]$Url, [string]$ExecutableName)
    Invoke-Download $Url (Join-Path $BinDir $ExecutableName)
}

function Install-WindowsTooling {
    New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
    $tmp = Join-Path $env:TEMP ("platform-live-tools-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        Install-DirectAsset "https://dl.k8s.io/release/$($Versions.Kubernetes)/bin/windows/amd64/kubectl.exe" "kubectl.exe"
        Install-ZipAsset (Get-GitHubAssetUrl "helm/helm" $Versions.Helm "windows-amd64\.zip$") "helm.exe" $tmp
        Install-ZipAsset (Get-GitHubAssetUrl "fluxcd/flux2" $Versions.Flux "windows_amd64\.zip$") "flux.exe" $tmp
        Install-DirectAsset (Get-GitHubAssetUrl "kubernetes-sigs/cluster-api" $Versions.ClusterApi "clusterctl-windows-amd64\.exe$") "clusterctl.exe"
        Install-ZipAsset (Get-GitHubAssetUrl "yannh/kubeconform" $Versions.Kubeconform "kubeconform-windows-amd64\.zip$") "kubeconform.exe" $tmp
        Install-ZipAsset (Get-GitHubAssetUrl "open-policy-agent/conftest" $Versions.Conftest "Windows_x86_64\.zip$") "conftest.exe" $tmp
        Install-DirectAsset (Get-GitHubAssetUrl "mikefarah/yq" $Versions.Yq "yq_windows_amd64\.exe$") "yq.exe"
        Install-DirectAsset (Get-GitHubAssetUrl "jqlang/jq" $Versions.Jq "jq-windows-amd64\.exe$") "jq.exe"

        $virtUrl = Get-GitHubAssetUrl "kubevirt/kubectl-virt-plugin" $Versions.KubeVirt "virtctl-windows-amd64"
        if ($virtUrl -match "\.zip$") {
            Install-ZipAsset $virtUrl "virtctl.exe" $tmp
        } else {
            Install-DirectAsset $virtUrl "virtctl.exe"
        }

        $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
        $parts = @()
        if ($userPath) { $parts = $userPath -split ";" | Where-Object { $_ } }
        if ($parts -notcontains $BinDir) {
            [Environment]::SetEnvironmentVariable("Path", (($parts + $BinDir) -join ";"), "User")
        }
    }
    finally {
        Remove-Item -Recurse -Force $tmp -ErrorAction SilentlyContinue
    }
}

function Install-RemoteTooling {
    param([string]$HostName)
    $remoteScript = @"
set -euo pipefail
tmp="\$(mktemp -d)"
cleanup() { rm -rf "\$tmp"; }
trap cleanup EXIT
fetch() { curl -fsSL --retry 3 --connect-timeout 15 --max-time 300 -o "\$2" "\$1"; }
install_direct() { fetch "\$1" "\$tmp/\$2"; sudo install -m 0755 "\$tmp/\$2" "/usr/local/bin/\$2"; }
install_targz_bin() {
  local url="\$1" bin="\$2" dir="\$tmp/\${bin}-extract"
  mkdir -p "\$dir"
  fetch "\$url" "\$tmp/\${bin}.tar.gz"
  tar -xzf "\$tmp/\${bin}.tar.gz" -C "\$dir"
  local found="\$(find "\$dir" -type f -name "\$bin" | head -n 1)"
  test -n "\$found"
  sudo install -m 0755 "\$found" "/usr/local/bin/\$bin"
}
install_targz_bin 'https://get.helm.sh/helm-v3.21.2-linux-amd64.tar.gz' helm
install_targz_bin 'https://github.com/fluxcd/flux2/releases/download/v2.8.8/flux_2.8.8_linux_amd64.tar.gz' flux
install_direct 'https://github.com/kubernetes-sigs/cluster-api/releases/download/v1.13.2/clusterctl-linux-amd64' clusterctl
install_targz_bin 'https://github.com/yannh/kubeconform/releases/download/v0.8.0/kubeconform-linux-amd64.tar.gz' kubeconform
install_targz_bin 'https://github.com/open-policy-agent/conftest/releases/download/v0.68.2/conftest_0.68.2_Linux_x86_64.tar.gz' conftest
install_direct 'https://github.com/mikefarah/yq/releases/download/v4.53.3/yq_linux_amd64' yq
install_direct 'https://github.com/jqlang/jq/releases/download/jq-1.8.2/jq-linux-amd64' jq
printf 'node=%s\n' "\$(hostname)"
helm version --short
flux --version
clusterctl version | head -n 1
kubeconform -v
conftest --version | head -n 2
yq --version
jq -V
"@
    $tmpFile = Join-Path $env:TEMP ("platform-live-tools-" + $HostName + ".sh")
    [System.IO.File]::WriteAllText($tmpFile, $remoteScript, [System.Text.UTF8Encoding]::new($false))
    scp -i $SshKey -o StrictHostKeyChecking=no $tmpFile "${RemoteUser}@${HostName}:/tmp/platform-live-tools.sh"
    ssh -i $SshKey -o StrictHostKeyChecking=no "${RemoteUser}@${HostName}" "bash /tmp/platform-live-tools.sh"
    Remove-Item -Force $tmpFile -ErrorAction SilentlyContinue
}

Install-WindowsTooling
foreach ($hostName in $RemoteHosts) { Install-RemoteTooling -HostName $hostName }

foreach ($tool in "kubectl","helm","flux","virtctl","clusterctl","kubeconform","conftest","yq","jq") {
    $exe = Join-Path $BinDir "$tool.exe"
    if (Test-Path $exe) {
        [pscustomobject]@{ Tool = $tool; Path = $exe; Size = (Get-Item $exe).Length }
    }
}
