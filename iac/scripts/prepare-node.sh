#!/usr/bin/env bash
set -euo pipefail

echo "== CPU virtualization =="
lscpu | grep -E 'Virtualization|Hypervisor' || true
test -e /dev/kvm

echo "== Longhorn data disk =="
DATA_DISK="$(lsblk -dpno NAME,TYPE,SIZE | awk '$2=="disk" && $3 ~ /^180G/ {print $1; exit}')"
if [[ -n "${DATA_DISK}" ]]; then
  sudo mkdir -p /var/lib/longhorn
  if ! sudo blkid -o value -s TYPE "${DATA_DISK}1" 2>/dev/null | grep -qx ext4; then
    sudo parted -s "${DATA_DISK}" mklabel gpt mkpart primary ext4 0% 100%
    sudo partprobe "${DATA_DISK}" || true
    sleep 2
    sudo mkfs.ext4 -F "${DATA_DISK}1"
  fi
  grep -q '/var/lib/longhorn' /etc/fstab || echo "${DATA_DISK}1 /var/lib/longhorn ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab >/dev/null
  sudo mount -a
fi

df -h /var/lib/longhorn
