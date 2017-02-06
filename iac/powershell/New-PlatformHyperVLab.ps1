[CmdletBinding()]
param(
    [string]$Prefix = "platform",
    [string]$SwitchName = "Platform-Fabric",
    [string]$NatName = "PlatformNAT",
    [string]$Subnet = "172.28.10.0/24",
    [string]$Gateway = "172.28.10.1",
    [string]$UbuntuImgUrl = "https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img",
    [string]$QemuImgZipUrl = "https://cloudbase.it/downloads/qemu-img-win-x64-2_3_0.zip",
    [string]$LabRoot = "C:\HyperV\PlatformLab",
    [string]$ProjectRoot = "C:\Users\yuri\Personal\Sources\Platform",
    [Int64]$NodeMemoryBytes = 7GB,
    [switch]$RecreateVMs
)

$ErrorActionPreference = "Stop"

function Assert-Admin {
    $principal = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Run this script from an elevated PowerShell session."
    }
}

function Write-Step([string]$Message) {
    $line = "[{0}] {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Host $line
}

function Get-FileWithCurl {
    param(
        [string]$Uri,
        [string]$OutFile,
        [Int64]$MinimumBytes
    )

    if ((Test-Path -LiteralPath $OutFile) -and ((Get-Item -LiteralPath $OutFile).Length -lt $MinimumBytes)) {
        Write-Step "Removing incomplete download: $OutFile"
        Remove-Item -LiteralPath $OutFile -Force
    }

    if (-not (Test-Path -LiteralPath $OutFile)) {
        Write-Step "Downloading $Uri"
        & curl.exe -L --fail --retry 5 --retry-delay 5 -o $OutFile $Uri
        if ($LASTEXITCODE -ne 0) { throw "curl failed with exit code $LASTEXITCODE for $Uri" }
    }

    if ((Get-Item -LiteralPath $OutFile).Length -lt $MinimumBytes) {
        throw "Downloaded file is unexpectedly small: $OutFile"
    }
}

function ConvertTo-NetplanMac([string]$Mac) {
    return (($Mac.ToLower() -replace "(.{2})(?!$)", '$1:'))
}

function New-CidataDisk {
    param(
        [string]$SeedPath,
        [string]$Hostname,
        [string]$IpAddress,
        [string]$MacAddress,
        [string]$PublicKey
    )

    $seedDir = Join-Path $ProjectRoot "iac\cloud-init\$Hostname"
    New-Item -ItemType Directory -Force -Path $seedDir | Out-Null
    $mac = ConvertTo-NetplanMac $MacAddress

    @"
instance-id: platform-$Hostname-v2
local-hostname: $Hostname
"@ | Set-Content -LiteralPath (Join-Path $seedDir "meta-data") -Encoding ascii

    @"
version: 2
ethernets:
  eth0:
    match:
      macaddress: "$mac"
    set-name: eth0
    dhcp4: false
    addresses:
      - $IpAddress/24
    routes:
      - to: default
        via: $Gateway
    nameservers:
      addresses:
        - 1.1.1.1
        - 8.8.8.8
"@ | Set-Content -LiteralPath (Join-Path $seedDir "network-config") -Encoding ascii

    @"
#cloud-config
hostname: $Hostname
manage_etc_hosts: true
ssh_pwauth: false
disable_root: true
users:
  - name: platform
    groups: [adm, sudo]
    shell: /bin/bash
    sudo: ["ALL=(ALL) NOPASSWD:ALL"]
    lock_passwd: true
    ssh_authorized_keys:
      - $PublicKey
package_update: true
packages:
  - ca-certificates
  - curl
  - gnupg
  - jq
  - open-iscsi
  - nfs-common
  - qemu-guest-agent
  - socat
  - conntrack
  - ipset
  - ethtool
  - ebtables
  - bridge-utils
  - parted
write_files:
  - path: /etc/modules-load.d/k8s.conf
    content: |
      overlay
      br_netfilter
      kvm
      kvm_intel
      kvm_amd
  - path: /etc/sysctl.d/99-kubernetes.conf
    content: |
      net.bridge.bridge-nf-call-iptables = 1
      net.bridge.bridge-nf-call-ip6tables = 1
      net.ipv4.ip_forward = 1
runcmd:
  - swapoff -a
  - sed -ri '/\sswap\s/s/^#?/#/' /etc/fstab
  - modprobe overlay || true
  - modprobe br_netfilter || true
  - modprobe kvm || true
  - modprobe kvm_intel || true
  - modprobe kvm_amd || true
  - sysctl --system
  - systemctl enable --now qemu-guest-agent
  - systemctl enable --now iscsid
  - mkdir -p /var/lib/longhorn
  - |
    DATA_DISK=`$(lsblk -dpno NAME,TYPE,SIZE | awk '`$2=="disk" && `$3 ~ /^180G/ {print `$1; exit}')
    if [ -n "`$DATA_DISK" ]; then
      if ! blkid "`${DATA_DISK}1" >/dev/null 2>&1; then
        parted -s "`$DATA_DISK" mklabel gpt mkpart primary ext4 0% 100%
        mkfs.ext4 -F "`${DATA_DISK}1"
      fi
      grep -q '/var/lib/longhorn' /etc/fstab || echo "`${DATA_DISK}1 /var/lib/longhorn ext4 defaults,nofail 0 2" >> /etc/fstab
      mount -a
    fi
final_message: "cloud-init completed for $Hostname"
"@ | Set-Content -LiteralPath (Join-Path $seedDir "user-data") -Encoding ascii

    if (Test-Path -LiteralPath $SeedPath) {
        Remove-Item -LiteralPath $SeedPath -Force
    }

    $vhd = New-VHD -Path $SeedPath -SizeBytes 64MB -Dynamic
    $mounted = Mount-VHD -Path $vhd.Path -PassThru
    try {
        $disk = $mounted | Get-Disk
        Initialize-Disk -Number $disk.Number -PartitionStyle MBR
        $partition = New-Partition -DiskNumber $disk.Number -UseMaximumSize -AssignDriveLetter
        Format-Volume -Partition $partition -FileSystem FAT32 -NewFileSystemLabel CIDATA -Confirm:$false | Out-Null
        $drive = ($partition | Get-Volume).DriveLetter + ":"
        Copy-Item -LiteralPath (Join-Path $seedDir "meta-data") -Destination $drive
        Copy-Item -LiteralPath (Join-Path $seedDir "user-data") -Destination $drive
        Copy-Item -LiteralPath (Join-Path $seedDir "network-config") -Destination $drive
    }
    finally {
        Dismount-VHD -Path $vhd.Path
    }
}

Assert-Admin
New-Item -ItemType Directory -Force -Path $LabRoot, (Join-Path $ProjectRoot "logs") | Out-Null
$script:LogPath = Join-Path $ProjectRoot ("logs\hyperv-provision-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
Start-Transcript -Path $script:LogPath -Append | Out-Null

try {
    Write-Step "Preparing Hyper-V lab root: $LabRoot"

    $sshDir = Join-Path $ProjectRoot ".ssh"
    New-Item -ItemType Directory -Force -Path $sshDir | Out-Null
    $keyPath = Join-Path $sshDir "platform_lab_ed25519"
    if (-not (Test-Path -LiteralPath $keyPath)) {
        Write-Step "Generating SSH key: $keyPath"
        cmd.exe /c "`"%WINDIR%\System32\OpenSSH\ssh-keygen.exe`" -q -t ed25519 -N `"`" -f `"$keyPath`""
        if ($LASTEXITCODE -ne 0) {
            throw "ssh-keygen failed with exit code $LASTEXITCODE"
        }
    }
    $publicKey = (Get-Content -LiteralPath "$keyPath.pub" -Raw).Trim()

    if (-not (Get-VMSwitch -Name $SwitchName -ErrorAction SilentlyContinue)) {
        Write-Step "Creating internal Hyper-V switch: $SwitchName"
        New-VMSwitch -Name $SwitchName -SwitchType Internal | Out-Null
    }

    $ifAlias = "vEthernet ($SwitchName)"
    $existingIp = Get-NetIPAddress -InterfaceAlias $ifAlias -AddressFamily IPv4 -ErrorAction SilentlyContinue |
        Where-Object { $_.IPAddress -eq $Gateway }
    if (-not $existingIp) {
        Write-Step "Assigning host gateway $Gateway to $ifAlias"
        Get-NetIPAddress -InterfaceAlias $ifAlias -AddressFamily IPv4 -ErrorAction SilentlyContinue |
            Remove-NetIPAddress -Confirm:$false -ErrorAction SilentlyContinue
        New-NetIPAddress -InterfaceAlias $ifAlias -IPAddress $Gateway -PrefixLength 24 | Out-Null
    }

    if (-not (Get-NetNat -Name $NatName -ErrorAction SilentlyContinue)) {
        Write-Step "Creating Windows NAT $NatName for $Subnet"
        New-NetNat -Name $NatName -InternalIPInterfaceAddressPrefix $Subnet | Out-Null
    }

    $downloads = Join-Path $LabRoot "downloads"
    New-Item -ItemType Directory -Force -Path $downloads | Out-Null
    $tools = Join-Path $LabRoot "tools"
    New-Item -ItemType Directory -Force -Path $tools | Out-Null
    $qemuZip = Join-Path $downloads "qemu-img-win-x64-2_3_0.zip"
    $qemuImg = Join-Path $tools "qemu-img.exe"
    if (-not (Test-Path -LiteralPath $qemuImg)) {
        Get-FileWithCurl -Uri $QemuImgZipUrl -OutFile $qemuZip -MinimumBytes 1000000
        Write-Step "Extracting qemu-img"
        Expand-Archive -LiteralPath $qemuZip -DestinationPath $tools -Force
        $foundQemu = Get-ChildItem -LiteralPath $tools -Recurse -Filter "qemu-img.exe" | Select-Object -First 1
        if (-not $foundQemu) { throw "qemu-img.exe not found after extracting $qemuZip" }
        if ($foundQemu.FullName -ne $qemuImg) {
            Copy-Item -LiteralPath $foundQemu.FullName -Destination $qemuImg -Force
        }
    }

    $baseImg = Join-Path $downloads "ubuntu-24.04-server-cloudimg-amd64.img"
    $baseVhdx = Join-Path $downloads "ubuntu-24.04-server-cloudimg-amd64-generic.vhdx"

    Get-FileWithCurl -Uri $UbuntuImgUrl -OutFile $baseImg -MinimumBytes 600000000

    if (-not (Test-Path -LiteralPath $baseVhdx)) {
        Write-Step "Converting generic Ubuntu QCOW2 image to VHDX"
        & $qemuImg convert $baseImg -O vhdx -o subformat=dynamic $baseVhdx
        if ($LASTEXITCODE -ne 0) { throw "qemu-img convert failed with exit code $LASTEXITCODE" }
    }

    $nodes = @(
        @{ Name = "$Prefix-n1"; Hostname = "n1"; Ip = "172.28.10.11"; Mac = "00155D281011" },
        @{ Name = "$Prefix-n2"; Hostname = "n2"; Ip = "172.28.10.12"; Mac = "00155D281012" },
        @{ Name = "$Prefix-n3"; Hostname = "n3"; Ip = "172.28.10.13"; Mac = "00155D281013" }
    )

    foreach ($node in $nodes) {
        $vmDir = Join-Path $LabRoot $node.Name
        New-Item -ItemType Directory -Force -Path $vmDir | Out-Null
        $osVhd = Join-Path $vmDir "$($node.Name)-os.vhdx"
        $dataVhd = Join-Path $vmDir "$($node.Name)-longhorn.vhdx"
        $seedVhd = Join-Path $vmDir "$($node.Name)-cidata.vhdx"

        $existingVm = Get-VM -Name $node.Name -ErrorAction SilentlyContinue
        if ($existingVm -and $RecreateVMs) {
            Write-Step "Recreating VM $($node.Name)"
            if ($existingVm.State -ne "Off") {
                Stop-VM -Name $node.Name -TurnOff -Force
            }
            Remove-VM -Name $node.Name -Force
            Remove-Item -LiteralPath $vmDir -Recurse -Force
            New-Item -ItemType Directory -Force -Path $vmDir | Out-Null
            $existingVm = $null
        }
        if ($existingVm -and (-not (Test-Path -LiteralPath $seedVhd) -or -not (Test-Path -LiteralPath $dataVhd))) {
            Write-Step "Removing incomplete VM $($node.Name)"
            if ($existingVm.State -ne "Off") {
                Stop-VM -Name $node.Name -TurnOff -Force
            }
            Remove-VM -Name $node.Name -Force
            $existingVm = $null
        }

        if (-not $existingVm) {
            Write-Step "Creating VM $($node.Name)"
            Copy-Item -LiteralPath $baseVhdx -Destination $osVhd -Force
            Resize-VHD -Path $osVhd -SizeBytes 64GB
            New-VM -Name $node.Name -Generation 2 -MemoryStartupBytes $NodeMemoryBytes -VHDPath $osVhd -SwitchName $SwitchName -Path $LabRoot | Out-Null
            Set-VMProcessor -VMName $node.Name -Count 4 -ExposeVirtualizationExtensions $true
            Set-VMMemory -VMName $node.Name -DynamicMemoryEnabled $false
            Set-VMFirmware -VMName $node.Name -EnableSecureBoot On -SecureBootTemplate MicrosoftUEFICertificateAuthority
            Set-VM -Name $node.Name -CheckpointType Disabled -AutomaticStopAction ShutDown
            Set-VMNetworkAdapter -VMName $node.Name -StaticMacAddress $node.Mac -MacAddressSpoofing On

            New-CidataDisk -SeedPath $seedVhd -Hostname $node.Hostname -IpAddress $node.Ip -MacAddress $node.Mac -PublicKey $publicKey
            Add-VMHardDiskDrive -VMName $node.Name -Path $seedVhd

            New-VHD -Path $dataVhd -SizeBytes 180GB -Dynamic | Out-Null
            Add-VMHardDiskDrive -VMName $node.Name -Path $dataVhd
        }
        else {
            Write-Step "VM $($node.Name) already exists; leaving existing VM intact"
        }

        $vm = Get-VM -Name $node.Name
        if ($vm.MemoryStartup -ne $NodeMemoryBytes) {
            Write-Step "Reconciling memory for $($node.Name) to $([Math]::Round($NodeMemoryBytes / 1GB, 1)) GiB"
            if ($vm.State -ne "Off") {
                Stop-VM -Name $node.Name -TurnOff -Force
            }
            Set-VMMemory -VMName $node.Name -DynamicMemoryEnabled $false -StartupBytes $NodeMemoryBytes
        }

        $adapter = Get-VMNetworkAdapter -VMName $node.Name
        $seedNeedsUpdate = -not (Test-Path -LiteralPath (Join-Path $ProjectRoot "iac\cloud-init\$($node.Hostname)\network-config")) -or
            -not ((Get-Content -LiteralPath (Join-Path $ProjectRoot "iac\cloud-init\$($node.Hostname)\network-config") -Raw) -match (ConvertTo-NetplanMac $node.Mac))
        if ($adapter.MacAddress -ne $node.Mac -or $seedNeedsUpdate) {
            Write-Step "Reconciling MAC and cidata seed for $($node.Name)"
            $vm = Get-VM -Name $node.Name
            if ($vm.State -ne "Off") {
                Stop-VM -Name $node.Name -TurnOff -Force
            }
            Set-VMNetworkAdapter -VMName $node.Name -StaticMacAddress $node.Mac -MacAddressSpoofing On
            Get-VMHardDiskDrive -VMName $node.Name | Where-Object { $_.Path -eq $seedVhd } | Remove-VMHardDiskDrive
            New-CidataDisk -SeedPath $seedVhd -Hostname $node.Hostname -IpAddress $node.Ip -MacAddress $node.Mac -PublicKey $publicKey
            Add-VMHardDiskDrive -VMName $node.Name -Path $seedVhd
        }

        if ((Get-VM -Name $node.Name).State -ne "Running") {
            Write-Step "Starting VM $($node.Name)"
            Start-VM -Name $node.Name
        }
    }

    Write-Step "Hyper-V lab provisioning completed"
    Write-Step "SSH private key: $keyPath"
}
finally {
    Stop-Transcript | Out-Null
}
