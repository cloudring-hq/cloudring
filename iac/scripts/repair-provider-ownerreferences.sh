#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-kubectl}"
MODE="${MODE:-plan}"
NEW_GROUP="${NEW_GROUP:-platform.privatecloud.local}"

case "${MODE}" in
  plan|apply) ;;
  *)
    echo "MODE must be plan or apply" >&2
    exit 1
    ;;
esac

if [[ "${MODE}" == "apply" && "${CONFIRM_PROVIDER_OWNERREF_REPAIR:-false}" != "true" ]]; then
  echo "set CONFIRM_PROVIDER_OWNERREF_REPAIR=true before MODE=apply" >&2
  exit 1
fi

python3 - "${MODE}" "${NEW_GROUP}" "${KUBECTL}" <<'PY'
import hashlib
import json
import subprocess
import sys

MODE = sys.argv[1]
NEW_GROUP = sys.argv[2]
KUBECTL = sys.argv[3].split()

PROVIDER_PLURALS = {
    "Project": "projects",
    "CapacityCell": "capacitycells",
    "CapacityReservation": "capacityreservations",
    "AdmissionJournal": "admissionjournals",
    "VirtualMachineClaim": "virtualmachineclaims",
    "KubernetesClusterClaim": "kubernetesclusterclaims",
    "Image": "images",
    "Volume": "volumes",
    "Network": "networks",
    "FirewallRule": "firewallrules",
    "BackupPlan": "backupplans",
    "RestoreRequest": "restorerequests",
    "AccessGrant": "accessgrants",
    "SelfServiceAuditEvent": "selfserviceauditevents",
}

CHILD_RESOURCES = [
    "persistentvolumeclaims",
    "networkpolicies.networking.k8s.io",
    "virtualmachines.kubevirt.io",
    "virtualmachinesnapshots.snapshot.kubevirt.io",
    "virtualmachinerestores.snapshot.kubevirt.io",
    "rolebindings.rbac.authorization.k8s.io",
    "secrets",
    "services",
    "deployments.apps",
    "poddisruptionbudgets.policy",
    "clusters.cluster.x-k8s.io",
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


def ref_group(ref):
    return str(ref.get("apiVersion", "")).split("/", 1)[0]


def ref_key(ref):
    return (ref.get("kind"), ref.get("name"), ref.get("uid"))


def provider_objects():
    objects = {}
    for kind, plural in PROVIDER_PLURALS.items():
        result = run(["get", f"{plural}.{NEW_GROUP}", "-A", "-o", "json"], check=False)
        if result.returncode != 0:
            result = run(["get", f"{plural}.{NEW_GROUP}", "-o", "json"], check=False)
        if result.returncode != 0:
            continue
        for item in json.loads(result.stdout).get("items", []):
            metadata = item.get("metadata", {})
            objects[(kind, metadata.get("namespace"), metadata.get("name"))] = {
                "apiVersion": f"{NEW_GROUP}/v1alpha1",
                "kind": kind,
                "name": metadata.get("name"),
                "uid": metadata.get("uid"),
                "controller": True,
                "blockOwnerDeletion": False,
            }
    return objects


def target_for(ref, namespace, targets):
    return (
        targets.get((ref.get("kind"), namespace, ref.get("name")))
        or targets.get((ref.get("kind"), None, ref.get("name")))
    )


targets = provider_objects()
findings = []

for resource in CHILD_RESOURCES:
    result = run(["get", resource, "-A", "-o", "json"], check=False)
    if result.returncode != 0:
        continue
    for item in json.loads(result.stdout).get("items", []):
        metadata = item.get("metadata", {})
        namespace = metadata.get("namespace")
        owner_refs = metadata.get("ownerReferences") or []
        if not owner_refs:
            continue
        new_refs = []
        seen = set()
        changed = False
        replaced = []
        for ref in owner_refs:
            target = target_for(ref, namespace, targets)
            replacement = None
            if (
                target
                and ref.get("controller") is True
                and ref_group(ref) != NEW_GROUP
            ):
                replacement = target
                changed = True
                replaced.append(
                    {
                        "kind": ref.get("kind"),
                        "name": ref.get("name"),
                        "previousGroupFingerprint": hashlib.sha256(ref_group(ref).encode("utf-8")).hexdigest()[:16],
                    }
                )
            candidate = replacement or ref
            key = ref_key(candidate)
            if key in seen:
                changed = True
                continue
            seen.add(key)
            new_refs.append(candidate)
        if not changed:
            continue
        finding = {
            "resource": resource,
            "namespace": namespace,
            "name": metadata.get("name"),
            "replaced": replaced,
        }
        findings.append(finding)
        if MODE == "apply":
            args = ["patch", resource, metadata["name"], "--type=merge", "-p", json.dumps({"metadata": {"ownerReferences": new_refs}})]
            if namespace:
                args[1:1] = ["-n", namespace]
            run(args)

print(json.dumps({"mode": MODE, "newGroup": NEW_GROUP, "repairs": findings, "count": len(findings)}, indent=2))
PY
