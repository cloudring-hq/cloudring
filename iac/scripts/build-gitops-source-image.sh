#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

IMAGE="${IMAGE:-localhost/platform-gitops-source:dev}"
BASE_IMAGE="${BASE_IMAGE:-docker.io/library/ubuntu:24.04}"
OUT="${OUT:-/tmp/platform-gitops-source-image.tar}"
CTR="${CTR:-sudo k3s ctr}"

work="$(mktemp -d)"
cleanup() {
  sudo rm -rf "${work}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

command -v git >/dev/null || { echo "git is required to build the GitOps source image" >&2; exit 1; }

mkdir -p "${work}/repo"
tar \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  -C "${PROJECT_ROOT}" \
  -cf - README.md docs gitops iac requirements | tar -C "${work}/repo" -xf -

git -C "${work}/repo" init -b main >/dev/null
git -C "${work}/repo" config user.email "platform-gitops@example.invalid"
git -C "${work}/repo" config user.name "Platform GitOps"
git -C "${work}/repo" add .
git -C "${work}/repo" commit -m "Platform desired state" >/dev/null
git clone --bare "${work}/repo" "${work}/platform.git" >/dev/null 2>&1
git -C "${work}/platform.git" update-server-info

mkdir -p "${work}/debs"
apt-cache depends --recurse \
  --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances \
  git python3 python3-minimal ca-certificates \
  | awk '/^[[:alnum:]][[:alnum:].+:-]*$/ {print}' \
  | sort -u >"${work}/packages.txt"
(
  cd "${work}/debs"
  while read -r package; do
    apt-get download "${package}" >/dev/null || echo "warning: skipped ${package}" >&2
  done <"${work}/packages.txt"
)
for deb in "${work}"/debs/*.deb; do
  dpkg-deb -x "${deb}" "${work}/rootfs"
done

mkdir -p "${work}/rootfs/srv/git"
cp -a "${work}/platform.git" "${work}/rootfs/srv/git/platform.git"
test -f "${work}/rootfs/srv/git/platform.git/HEAD"

mkdir -p "${work}/rootfs/opt/platform-gitops-source"
cat >"${work}/rootfs/opt/platform-gitops-source/server.py" <<'PY'
#!/usr/bin/env python3
import os
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class GitHttpHandler(BaseHTTPRequestHandler):
    server_version = "PlatformGitHTTP/1.0"

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)

    def do_GET(self):
        self.handle_git()

    def do_POST(self):
        self.handle_git()

    def handle_git(self):
        parsed = urllib.parse.urlsplit(self.path)
        if self.command == "GET" and parsed.path == "/platform.git/HEAD":
            try:
                with open("/srv/git/platform.git/HEAD", "rb") as handle:
                    response_body = handle.read()
            except FileNotFoundError:
                self.send_error(404, "repository HEAD not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(response_body)))
            self.end_headers()
            self.wfile.write(response_body)
            return
        body = b""
        if self.command == "POST":
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length > 50 * 1024 * 1024:
                self.send_error(413, "request too large")
                return
            body = self.rfile.read(length)
        env = os.environ.copy()
        env.update(
            {
                "GIT_PROJECT_ROOT": "/srv/git",
                "GIT_HTTP_EXPORT_ALL": "1",
                "REQUEST_METHOD": self.command,
                "PATH_INFO": urllib.parse.unquote(parsed.path),
                "QUERY_STRING": parsed.query,
                "REMOTE_ADDR": self.client_address[0],
                "CONTENT_TYPE": self.headers.get("Content-Type", ""),
                "CONTENT_LENGTH": str(len(body)),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "safe.directory",
                "GIT_CONFIG_VALUE_0": "*",
            }
        )
        proc = subprocess.run(
            ["/usr/lib/git-core/git-http-backend"],
            input=body,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )
        if proc.returncode != 0:
            stderr = proc.stderr.decode("utf-8", "replace")[:300]
            print(f"git-http-backend failed: {stderr}", flush=True)
            self.send_error(500, stderr)
            return
        header_blob, _, response_body = proc.stdout.partition(b"\r\n\r\n")
        if not response_body:
            header_blob, _, response_body = proc.stdout.partition(b"\n\n")
        status = 200
        headers = []
        for raw in header_blob.splitlines():
            if not raw:
                continue
            name, _, value = raw.decode("iso-8859-1").partition(":")
            if name.lower() == "status":
                try:
                    status = int(value.strip().split()[0])
                except (IndexError, ValueError):
                    status = 200
            elif name and value:
                headers.append((name, value.strip()))
        self.send_response(status)
        for name, value in headers:
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8000), GitHttpHandler)
    print("platform git smart-http listening on :8000", flush=True)
    server.serve_forever()
PY

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
    "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
    "LANG=C.UTF-8",
    "PYTHONDONTWRITEBYTECODE=1",
    "PYTHONUNBUFFERED=1",
]
config["config"]["Entrypoint"] = ["python3", "/opt/platform-gitops-source/server.py"]
config["config"]["Cmd"] = None
config["config"]["WorkingDir"] = "/opt/platform-gitops-source"
config["config"]["User"] = "65532:65532"
config["config"]["ExposedPorts"] = {"8000/tcp": {}}
config.setdefault("rootfs", {}).setdefault("diff_ids", []).append(f"sha256:{layer_diff_id}")
config.setdefault("history", []).append(
    {"created": created, "created_by": "build-gitops-source-image.sh", "comment": "add platform bare Git repository"}
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
