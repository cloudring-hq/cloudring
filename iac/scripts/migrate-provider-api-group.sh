#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-kubectl}"
MODE="${MODE:-plan}"
NEW_GROUP="${NEW_GROUP:-platform.privatecloud.local}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CRD_MANIFEST="${CRD_MANIFEST:-${PROJECT_ROOT}/iac/kubernetes/provider-api/crds.yaml}"
APPLY_TARGET_CRDS="${APPLY_TARGET_CRDS:-true}"

case "${MODE}" in
  plan|apply|retire) ;;
  *)
    echo "MODE must be plan, apply, or retire" >&2
    exit 1
    ;;
esac

if [[ "${MODE}" == "apply" || "${MODE}" == "retire" ]]; then
  if [[ "${CONFIRM_PROVIDER_API_GROUP_MIGRATION:-false}" != "true" ]]; then
    echo "set CONFIRM_PROVIDER_API_GROUP_MIGRATION=true before MODE=${MODE}" >&2
    exit 1
  fi
fi

if [[ "${MODE}" == "retire" && "${CONFIRM_PROVIDER_API_GROUP_RETIRE:-false}" != "true" ]]; then
  echo "set CONFIRM_PROVIDER_API_GROUP_RETIRE=true before retiring previous CRDs" >&2
  exit 1
fi

if [[ "${MODE}" == "apply" && "${APPLY_TARGET_CRDS}" == "true" ]]; then
  "${KUBECTL}" apply --server-side --dry-run=server -f "${CRD_MANIFEST}" >/dev/null
  "${KUBECTL}" apply -f "${CRD_MANIFEST}"
fi

python3 - "${MODE}" "${NEW_GROUP}" "${KUBECTL}" <<'PY'
import json
import hashlib
import os
import subprocess
import sys

MODE = sys.argv[1]
NEW_GROUP = sys.argv[2]
KUBECTL = sys.argv[3].split()
PLURALS = [
    "projects",
    "capacitycells",
    "capacityreservations",
    "admissionjournals",
    "virtualmachineclaims",
    "kubernetesclusterclaims",
    "images",
    "volumes",
    "networks",
    "firewallrules",
    "backupplans",
    "restorerequests",
    "accessgrants",
    "selfserviceauditevents",
]


def run(args, input_text=None, check=True):
    completed = subprocess.run(
        KUBECTL + args,
        input=input_text,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or completed.stdout.strip())
    return completed


def load_json(args):
    return json.loads(run(args + ["-o", "json"]).stdout)


def clean_metadata(metadata, legacy_group):
    keep = {}
    for key in ("name", "namespace", "labels", "annotations"):
        if key in metadata:
            keep[key] = metadata[key]
    for map_key in ("labels", "annotations"):
        values = keep.get(map_key)
        if isinstance(values, dict):
            keep[map_key] = {
                key.replace(legacy_group, NEW_GROUP): value
                for key, value in values.items()
            }
    return keep


def migrate_item(item, legacy_group, target_version):
    migrated = {
        "apiVersion": f"{NEW_GROUP}/{target_version}",
        "kind": item["kind"],
        "metadata": clean_metadata(item.get("metadata", {}), legacy_group),
    }
    for key in ("spec", "data", "stringData", "type"):
        if key in item:
            migrated[key] = item[key]
    return migrated


def patch_status(plural, item):
    status = item.get("status")
    if not isinstance(status, dict) or not status:
        return
    metadata = item.get("metadata", {})
    name = metadata.get("name")
    namespace = metadata.get("namespace")
    if not name:
        return
    args = ["patch", f"{plural}.{NEW_GROUP}", name, "--subresource=status", "--type=merge", "-p", json.dumps({"status": status})]
    if namespace:
        args[1:1] = ["-n", namespace]
    result = run(args, check=False)
    if result.returncode != 0:
        print(f"warning: status patch failed for {plural}/{name}: {result.stderr.strip()}", file=sys.stderr)


crds = load_json(["get", "crd"])["items"]
by_plural = {plural: [] for plural in PLURALS}
for crd in crds:
    plural = crd.get("spec", {}).get("names", {}).get("plural")
    if plural in by_plural:
        by_plural[plural].append(crd)

target = {}
legacy = {}
for plural, items in by_plural.items():
    for crd in items:
        group = crd.get("spec", {}).get("group")
        if group == NEW_GROUP:
            target[plural] = crd
        elif group:
            legacy.setdefault(group, {})[plural] = crd

if MODE in ("apply", "retire"):
    missing_targets = [plural for plural in PLURALS if plural not in target]
    if missing_targets:
        raise SystemExit(f"missing target CRDs for {', '.join(missing_targets)}")

provider_anchors = {"projects", "capacitycells", "virtualmachineclaims"}
legacy = {
    group: items
    for group, items in legacy.items()
    if items and provider_anchors.intersection(items.keys())
}
if not legacy:
    print(json.dumps({"mode": MODE, "newGroup": NEW_GROUP, "previousGroupDetected": False, "migrated": 0}, indent=2))
    raise SystemExit(0)
if len(legacy) != 1:
    fingerprints = [
        hashlib.sha256(group.encode("utf-8")).hexdigest()[:16]
        for group in sorted(legacy)
    ]
    raise SystemExit("expected exactly one previous provider API group, found fingerprints: " + ", ".join(fingerprints))

legacy_group, legacy_crds = next(iter(legacy.items()))
report = {
    "mode": MODE,
    "newGroup": NEW_GROUP,
    "previousGroupDetected": True,
    "previousGroupFingerprint": hashlib.sha256(legacy_group.encode("utf-8")).hexdigest()[:16],
    "resources": [],
}
migrated_total = 0

for plural in PLURALS:
    legacy_crd = legacy_crds.get(plural)
    if not legacy_crd:
        continue
    scope = legacy_crd.get("spec", {}).get("scope", "Namespaced")
    target_crd = target.get(plural) or legacy_crd
    versions = target_crd.get("spec", {}).get("versions", [])
    target_version = next((v["name"] for v in versions if v.get("storage")), versions[0]["name"] if versions else "v1alpha1")
    get_args = ["get", f"{plural}.{legacy_group}"]
    if scope == "Namespaced":
        get_args.append("-A")
    result = run(get_args + ["-o", "json"], check=False)
    if result.returncode != 0:
        items = []
    else:
        items = json.loads(result.stdout).get("items", [])
    report["resources"].append({"plural": plural, "scope": scope, "count": len(items)})
    if MODE == "apply":
        migrated_items = []
        for item in items:
            migrated_items.append(migrate_item(item, legacy_group, target_version))
        if migrated_items:
            stream = "\n---\n".join(json.dumps(item) for item in migrated_items)
            run(["apply", "-f", "-"], input_text=stream)
        for item in items:
            patch_status(plural, item)
            migrated_total += 1

if MODE == "retire":
    for plural, crd in legacy_crds.items():
        crd_name = crd["metadata"]["name"]
        print(f"retiring previous CRD for {plural}", file=sys.stderr)
        run(["delete", "crd", crd_name, "--wait=false"], check=False)

report["migrated"] = migrated_total
print(json.dumps(report, indent=2))
PY
