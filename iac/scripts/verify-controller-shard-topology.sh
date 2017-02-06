#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
PYTHON="${PYTHON:-python3}"
MANIFEST="${MANIFEST:-${PROJECT_ROOT}/iac/kubernetes/provider-controller/sharded-controller.yaml}"
SHARD_TOTAL="${SHARD_TOTAL:-2}"
REPLICAS_PER_SHARD="${REPLICAS_PER_SHARD:-3}"
GLOBAL_SHARD_INDEX="${GLOBAL_SHARD_INDEX:-0}"
EXPECTED_IMAGE="${EXPECTED_IMAGE:-localhost/platform-provider-controller:dev}"

[[ -f "${MANIFEST}" ]] || { echo "manifest not found: ${MANIFEST}" >&2; exit 1; }

echo "== provider-controller shard topology manifest =="
echo "manifest=${MANIFEST}"

tmp_json="$(mktemp)"
trap 'rm -f "${tmp_json}"' EXIT

${KUBECTL} create --dry-run=client -f "${MANIFEST}" -o json > "${tmp_json}"
${KUBECTL} apply --dry-run=server -f "${MANIFEST}" >/dev/null

"${PYTHON}" - "${tmp_json}" "${SHARD_TOTAL}" "${REPLICAS_PER_SHARD}" "${GLOBAL_SHARD_INDEX}" "${EXPECTED_IMAGE}" <<'PY'
import json
import sys

path, shard_total_text, replicas_text, global_text, expected_image = sys.argv[1:]
shard_total = int(shard_total_text)
replicas = int(replicas_text)
global_shard_index = int(global_text)

with open(path, "r", encoding="utf-8") as handle:
    raw = handle.read()

decoder = json.JSONDecoder()
documents = []
position = 0
while position < len(raw):
    while position < len(raw) and raw[position].isspace():
        position += 1
    if position >= len(raw):
        break
    document, position = decoder.raw_decode(raw, position)
    documents.append(document)

items = []
for parsed in documents:
    items.extend(parsed.get("items") or [parsed])
deployments = {item["metadata"]["name"]: item for item in items if item.get("kind") == "Deployment"}
pdbs = {item["metadata"]["name"]: item for item in items if item.get("kind") == "PodDisruptionBudget"}
services = {item["metadata"]["name"]: item for item in items if item.get("kind") == "Service"}

expected_deployments = {f"provider-controller-shard-{index}" for index in range(shard_total)}
if set(deployments) != expected_deployments:
    raise SystemExit(f"unexpected shard deployments: {sorted(deployments)}")
if set(pdbs) != expected_deployments:
    raise SystemExit(f"unexpected shard PDBs: {sorted(pdbs)}")
expected_services = {f"provider-controller-shard-{index}-metrics" for index in range(shard_total)}
if set(services) != expected_services:
    raise SystemExit(f"unexpected shard Services: {sorted(services)}")

leases = set()
global_owners = []
for index in range(shard_total):
    name = f"provider-controller-shard-{index}"
    deployment = deployments[name]
    labels = deployment["spec"]["template"]["metadata"]["labels"]
    selector = deployment["spec"]["selector"]["matchLabels"]
    shard_label = str(index)
    for label_set, label_name in ((labels, "template labels"), (selector, "selector")):
        if label_set.get("platform.privatecloud.local/controller-shard") != shard_label:
            raise SystemExit(f"{name} missing shard label in {label_name}")
        if label_set.get("app.kubernetes.io/name") != "provider-controller":
            raise SystemExit(f"{name} missing app.kubernetes.io/name in {label_name}")
    if deployment["spec"].get("replicas") != replicas:
        raise SystemExit(f"{name} replicas mismatch")
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    if container.get("image") != expected_image:
        raise SystemExit(f"{name} image mismatch: {container.get('image')}")
    env = {}
    for item in container.get("env", []):
        if "value" in item:
            env[item["name"]] = item["value"]
    expected_env = {
        "CONTROLLER_SHARD_TOTAL": str(shard_total),
        "CONTROLLER_SHARD_INDEX": str(index),
        "CONTROLLER_GLOBAL_SHARD_INDEX": str(global_shard_index),
        "LEADER_ELECTION_LEASE_NAME": name,
        "CONTROLLER_NAMESPACE_ALLOWLIST": "",
    }
    for key, expected in expected_env.items():
        actual = env.get(key)
        if actual != expected:
            raise SystemExit(f"{name} {key} expected {expected!r}, got {actual!r}")
    leases.add(env["LEADER_ELECTION_LEASE_NAME"])
    if index == global_shard_index:
        global_owners.append(name)
    topology = deployment["spec"]["template"]["spec"].get("topologySpreadConstraints", [])
    if not topology:
        raise SystemExit(f"{name} missing topologySpreadConstraints")
    topology_labels = topology[0]["labelSelector"]["matchLabels"]
    if topology_labels.get("platform.privatecloud.local/controller-shard") != shard_label:
        raise SystemExit(f"{name} topology spread is not shard-scoped")
    service = services[f"{name}-metrics"]
    if service["spec"]["selector"].get("platform.privatecloud.local/controller-shard") != shard_label:
        raise SystemExit(f"{name} metrics Service is not shard-scoped")
    pdb = pdbs[name]
    if pdb["spec"]["selector"]["matchLabels"].get("platform.privatecloud.local/controller-shard") != shard_label:
        raise SystemExit(f"{name} PDB is not shard-scoped")

if len(leases) != shard_total:
    raise SystemExit("leases are not unique per shard")
if len(global_owners) != 1:
    raise SystemExit(f"expected one global shard owner, got {global_owners}")

print(
    f"active-active shard topology valid: shards={shard_total} "
    f"replicasPerShard={replicas} globalOwner={global_owners[0]}"
)
PY

echo "provider-controller shard topology verification passed"
