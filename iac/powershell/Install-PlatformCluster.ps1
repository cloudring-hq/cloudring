[CmdletBinding()]
param(
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform",
    [string]$SshUser = "platform",
    [string]$SshKey = "C:\Users\yuri\Personal\Sources\Platform\.ssh\platform_lab_ed25519",
    [string[]]$NodeIPs = @("172.28.10.11", "172.28.10.12", "172.28.10.13"),
    [string]$ApiVIP = "172.28.10.10",
    [string]$K3sChannel = "stable",
    [string]$CiliumVersion = "1.19.5",
    [string]$LonghornVersion = "1.12.0",
    [string]$MetalLBVersion = "0.16.1",
    [string]$KyvernoChartVersion = "3.8.1"
)

$ErrorActionPreference = "Stop"
$LogPath = Join-Path $ProjectRoot ("logs\cluster-install-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))

function Write-Step([string]$Message) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
    Add-Content -LiteralPath $LogPath -Value $line
}

function Invoke-Ssh {
    param(
        [string]$HostIp,
        [string]$Command
    )

    $sshArgs = @(
        "-i", $SshKey,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=$ProjectRoot\.ssh\known_hosts",
        "-o", "ConnectTimeout=10",
        "$SshUser@$HostIp",
        $Command
    )

    $output = & ssh.exe @sshArgs
    if ($LASTEXITCODE -ne 0) {
        throw "SSH command failed on ${HostIp} with exit code $LASTEXITCODE"
    }
    return $output
}

function Wait-SshReady([string]$HostIp) {
    Write-Step "Waiting for SSH on $HostIp"
    for ($i = 1; $i -le 90; $i++) {
        $result = & ssh.exe -i $SshKey -o StrictHostKeyChecking=no -o UserKnownHostsFile="$ProjectRoot\.ssh\known_hosts" -o ConnectTimeout=5 "$SshUser@$HostIp" "echo ready" 2>$null
        if ($LASTEXITCODE -eq 0 -and $result -match "ready") {
            Write-Step "SSH ready on $HostIp"
            return
        }
        Start-Sleep -Seconds 10
    }
    throw "SSH did not become ready on $HostIp"
}

function Copy-ToNode {
    param([string]$HostIp, [string]$LocalPath, [string]$RemotePath)
    & scp.exe -i $SshKey -o StrictHostKeyChecking=no -o UserKnownHostsFile="$ProjectRoot\.ssh\known_hosts" -r $LocalPath "$SshUser@${HostIp}:$RemotePath"
    if ($LASTEXITCODE -ne 0) { throw "scp failed to $HostIp" }
}

New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "logs"), (Join-Path $ProjectRoot ".ssh") | Out-Null

foreach ($ip in $NodeIPs) {
    Wait-SshReady $ip
}

foreach ($ip in $NodeIPs) {
    Write-Step "Checking nested virtualization on $ip"
    Copy-ToNode $ip (Join-Path $ProjectRoot "iac\scripts\prepare-node.sh") "/tmp/prepare-node.sh"
    Invoke-Ssh $ip "chmod +x /tmp/prepare-node.sh && /tmp/prepare-node.sh"
    Invoke-Ssh $ip "if command -v k3s >/dev/null 2>&1 && ! sudo systemctl is-active --quiet k3s; then sudo /usr/local/bin/k3s-uninstall.sh; fi"
}

$serverArgs = "--flannel-backend=none --disable-network-policy --disable servicelb --disable traefik --write-kubeconfig-mode 644 --tls-san $ApiVIP --cluster-cidr 10.42.0.0/16 --service-cidr 10.43.0.0/16"
$first = $NodeIPs[0]

Write-Step "Installing first k3s server on $first"
Invoke-Ssh $first "if ! command -v k3s >/dev/null 2>&1; then curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL=$K3sChannel sh -s - server --cluster-init --node-ip $first --advertise-address $first $serverArgs; fi"

Write-Step "Reading k3s node token"
$token = (Invoke-Ssh $first "sudo cat /var/lib/rancher/k3s/server/node-token").Trim()

foreach ($ip in $NodeIPs[1..($NodeIPs.Count - 1)]) {
    Write-Step "Installing additional k3s server on $ip"
    Invoke-Ssh $ip "if ! command -v k3s >/dev/null 2>&1; then curl -sfL https://get.k3s.io | INSTALL_K3S_CHANNEL=$K3sChannel K3S_TOKEN='$token' sh -s - server --server https://${first}:6443 --node-ip $ip --advertise-address $ip $serverArgs; fi"
}

Write-Step "Installing Helm on first node"
Invoke-Ssh $first "if ! command -v helm >/dev/null 2>&1; then curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash; fi"

Write-Step "Waiting for all k3s nodes"
Invoke-Ssh $first "for i in `$(seq 1 60); do sudo k3s kubectl get nodes && exit 0; sleep 10; done; exit 1"

Write-Step "Installing Cilium"
Invoke-Ssh $first "set -e; sudo helm repo add cilium https://helm.cilium.io >/dev/null; sudo helm repo update >/dev/null; sudo helm upgrade --install cilium cilium/cilium --version $CiliumVersion --namespace kube-system --set k8sServiceHost=$first --set k8sServicePort=6443 --set kubeProxyReplacement=false --set operator.replicas=1 --set hubble.relay.enabled=true --set hubble.ui.enabled=true --kubeconfig /etc/rancher/k3s/k3s.yaml"

Write-Step "Waiting for Cilium"
Invoke-Ssh $first "sudo k3s kubectl -n kube-system rollout status ds/cilium --timeout=600s"

Write-Step "Installing MetalLB"
Invoke-Ssh $first "set -e; sudo helm repo add metallb https://metallb.github.io/metallb >/dev/null; sudo helm repo update >/dev/null; sudo helm upgrade --install metallb metallb/metallb --version $MetalLBVersion --namespace metallb-system --create-namespace --kubeconfig /etc/rancher/k3s/k3s.yaml; sudo k3s kubectl -n metallb-system rollout status deploy/metallb-controller --timeout=600s"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\metallb-statuscleaner-lab-patch.yaml") "/tmp/metallb-statuscleaner-lab-patch.yaml"
Invoke-Ssh $first "set -e; sudo k3s kubectl -n metallb-system patch deploy metallb-frr-k8s-statuscleaner --type=strategic --patch-file /tmp/metallb-statuscleaner-lab-patch.yaml; sudo k3s kubectl -n metallb-system rollout status deploy/metallb-frr-k8s-statuscleaner --timeout=600s"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\metallb-frr-k8s-lab-patch.yaml") "/tmp/metallb-frr-k8s-lab-patch.yaml"
Invoke-Ssh $first "set -e; sudo k3s kubectl -n metallb-system patch ds metallb-frr-k8s --type=strategic --patch-file /tmp/metallb-frr-k8s-lab-patch.yaml; sudo k3s kubectl -n metallb-system rollout status ds/metallb-frr-k8s --timeout=600s"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\metallb-pool.yaml") "/tmp/metallb-pool.yaml"
Invoke-Ssh $first "sudo k3s kubectl apply -f /tmp/metallb-pool.yaml"

Write-Step "Installing Longhorn"
Invoke-Ssh $first "set -e; sudo helm repo add longhorn https://charts.longhorn.io >/dev/null; sudo helm repo update >/dev/null; sudo helm upgrade --install longhorn longhorn/longhorn --version $LonghornVersion --namespace longhorn-system --create-namespace --set defaultSettings.defaultReplicaCount=3 --set persistence.defaultClass=true --kubeconfig /etc/rancher/k3s/k3s.yaml; sudo k3s kubectl -n longhorn-system rollout status deploy/longhorn-driver-deployer --timeout=900s"

Write-Step "Installing KubeVirt"
Invoke-Ssh $first "set -e; KV_VERSION=`$(curl -s https://storage.googleapis.com/kubevirt-prow/release/kubevirt/kubevirt/stable.txt); sudo k3s kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/`$KV_VERSION/kubevirt-operator.yaml; sudo k3s kubectl apply -f https://github.com/kubevirt/kubevirt/releases/download/`$KV_VERSION/kubevirt-cr.yaml; sudo k3s kubectl -n kubevirt wait kv kubevirt --for condition=Available --timeout=900s"

Write-Step "Installing Kyverno policy layer"
Invoke-Ssh $first "set -e; sudo helm repo add kyverno https://kyverno.github.io/kyverno >/dev/null; sudo helm repo update >/dev/null; sudo helm upgrade --install kyverno kyverno/kyverno --version $KyvernoChartVersion --namespace kyverno --create-namespace --set admissionController.replicas=3 --set backgroundController.replicas=2 --set cleanupController.replicas=2 --set reportsController.replicas=2 --kubeconfig /etc/rancher/k3s/k3s.yaml; sudo k3s kubectl -n kyverno rollout status deploy/kyverno-admission-controller --timeout=300s"

Write-Step "Applying tenant policies and tests"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\tenants.yaml") "/tmp/tenants.yaml"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\tests\pvc-test.yaml") "/tmp/pvc-test.yaml"
Invoke-Ssh $first "sudo k3s kubectl apply -f /tmp/tenants.yaml; sudo k3s kubectl apply -f /tmp/pvc-test.yaml"

Write-Step "Applying provider hardening manifests"
Invoke-Ssh $first "rm -rf /tmp/platform-iac && mkdir -p /tmp/platform-iac/kubernetes"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\kubernetes\platform") "/tmp/platform-iac/kubernetes/"
Copy-ToNode $first (Join-Path $ProjectRoot "iac\scripts\apply-provider-hardening.sh") "/tmp/apply-provider-hardening.sh"
Invoke-Ssh $first "chmod +x /tmp/apply-provider-hardening.sh && /tmp/apply-provider-hardening.sh /tmp/platform-iac"


Write-Step "Fetching kubeconfig"
$kubeDir = Join-Path $ProjectRoot ".kube"
New-Item -ItemType Directory -Force -Path $kubeDir | Out-Null
& scp.exe -i $SshKey -o StrictHostKeyChecking=no -o UserKnownHostsFile="$ProjectRoot\.ssh\known_hosts" "$SshUser@${first}:/etc/rancher/k3s/k3s.yaml" (Join-Path $kubeDir "config.raw")
(Get-Content -LiteralPath (Join-Path $kubeDir "config.raw") -Raw).Replace("127.0.0.1", $first) |
    Set-Content -LiteralPath (Join-Path $kubeDir "config") -Encoding ascii

Write-Step "Cluster install completed"
Write-Step "Kubeconfig: $(Join-Path $kubeDir "config")"
