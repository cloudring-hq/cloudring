#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
APP_DIR="${PROJECT_ROOT}/iac/kubernetes/provider-portal"

IMAGE="${IMAGE:-localhost/platform-provider-portal:dev}"
BASE_IMAGE="${BASE_IMAGE:-docker.io/library/python:3.12-slim}"
OUT="${OUT:-/tmp/platform-provider-portal-image.tar}"
CTR="${CTR:-sudo k3s ctr}"

work="$(mktemp -d)"
cleanup() {
  sudo rm -rf "${work}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

mkdir -p "${work}/rootfs/opt/platform-provider-portal"
cp "${APP_DIR}/app.py" "${work}/rootfs/opt/platform-provider-portal/app.py"

tar --sort=name --mtime="@0" --owner=0 --group=0 --numeric-owner \
  -C "${work}/rootfs" -cf "${work}/layer.tar" .
gzip -n -c "${work}/layer.tar" >"${work}/layer.tar.gz"

${CTR} images export --platform linux/amd64 "${work}/base.tar" "${BASE_IMAGE}"
mkdir -p "${work}/image"
tar -C "${work}/image" -xf "${work}/base.tar"

python3 - "$work" "$IMAGE" <<'PY'
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

work = Path(sys.argv[1])
image = sys.argv[2]
image_root = work / "image"
layer_tar = work / "layer.tar"
layer_gz = work / "layer.tar.gz"

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

layer_digest = digest(layer_gz)
layer_diff_id = digest(layer_tar)
blob_dir = image_root / "blobs" / "sha256"
blob_dir.mkdir(parents=True, exist_ok=True)
shutil.copyfile(layer_gz, blob_dir / layer_digest)

docker_manifest_path = image_root / "manifest.json"
docker_manifest = json.loads(docker_manifest_path.read_text())
docker_entry = docker_manifest[0]

index_path = image_root / "index.json"
index = json.loads(index_path.read_text())
top = index["manifests"][0]
top_blob = json.loads((blob_dir / top["digest"].split(":", 1)[1]).read_text())
if top.get("mediaType", "").endswith("image.index.v1+json"):
    candidates = [
        item for item in top_blob.get("manifests", [])
        if item.get("platform", {}).get("os") == "linux"
        and item.get("platform", {}).get("architecture") == "amd64"
    ]
    if not candidates:
        raise SystemExit("base image index does not contain linux/amd64 manifest")
    base_manifest_descriptor = candidates[0]
else:
    base_manifest_descriptor = top

base_manifest = json.loads((blob_dir / base_manifest_descriptor["digest"].split(":", 1)[1]).read_text())
config = json.loads((blob_dir / base_manifest["config"]["digest"].split(":", 1)[1]).read_text())
created = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
config["created"] = created
config.setdefault("config", {})
config["config"]["Env"] = [
    "PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG=C.UTF-8",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
    "PORT=8080",
]
config["config"]["Entrypoint"] = ["python", "/opt/platform-provider-portal/app.py"]
config["config"]["Cmd"] = None
config["config"]["WorkingDir"] = "/opt/platform-provider-portal"
config["config"]["User"] = "65532:65532"
config["config"]["ExposedPorts"] = {"8080/tcp": {}}
config.setdefault("rootfs", {}).setdefault("diff_ids", []).append(f"sha256:{layer_diff_id}")
config.setdefault("history", []).append(
    {"created": created, "created_by": "build-provider-portal-image.sh", "comment": "add provider portal app"}
)
config["architecture"] = "amd64"
config["os"] = "linux"

config_bytes = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
config_digest = hashlib.sha256(config_bytes).hexdigest()
(blob_dir / config_digest).write_bytes(config_bytes)

docker_entry["Config"] = f"blobs/sha256/{config_digest}"
docker_entry["RepoTags"] = [image]
docker_entry.setdefault("Layers", []).append(f"blobs/sha256/{layer_digest}")
docker_manifest_path.write_text(json.dumps(docker_manifest, separators=(",", ":")))

image_manifest = dict(base_manifest)
image_manifest["config"] = {
    "mediaType": "application/vnd.oci.image.config.v1+json",
    "digest": f"sha256:{config_digest}",
    "size": len(config_bytes),
}
image_manifest["layers"] = list(base_manifest.get("layers", [])) + [
    {
        "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
        "digest": f"sha256:{layer_digest}",
        "size": layer_gz.stat().st_size,
    }
]
image_manifest["annotations"] = {**base_manifest.get("annotations", {}), "org.opencontainers.image.created": created}
image_manifest_bytes = json.dumps(image_manifest, sort_keys=True, separators=(",", ":")).encode()
image_manifest_digest = hashlib.sha256(image_manifest_bytes).hexdigest()
(blob_dir / image_manifest_digest).write_bytes(image_manifest_bytes)

_, _, tag = image.rpartition(":")
if not tag:
    tag = "latest"
index["manifests"] = [
    {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": f"sha256:{image_manifest_digest}",
        "size": len(image_manifest_bytes),
        "platform": {"architecture": "amd64", "os": "linux"},
        "annotations": {
            "io.containerd.image.name": image,
            "org.opencontainers.image.ref.name": tag,
        },
    }
]
index_path.write_text(json.dumps(index, separators=(",", ":")))
PY

tar -C "${work}/image" -cf "${OUT}" .
repo="${IMAGE%:*}"
${CTR} images import --base-name "${repo}" "${OUT}"

echo "Built and imported ${IMAGE}"
echo "Archive: ${OUT}"
