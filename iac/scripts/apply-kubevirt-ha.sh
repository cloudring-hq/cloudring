#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
MANIFEST="${MANIFEST:-${PROJECT_ROOT}/iac/kubernetes/platform/kubevirt-configuration.yaml}"
NAMESPACE="${NAMESPACE:-kubevirt}"

echo "== apply KubeVirt CR HA configuration =="
${KUBECTL} apply --server-side --dry-run=server -f "${MANIFEST}"
${KUBECTL} apply -f "${MANIFEST}"

echo "== harden virt-operator deployment =="
${KUBECTL} -n "${NAMESPACE}" patch deployment virt-operator --type=merge -p '{
  "spec": {
    "replicas": 3,
    "strategy": {
      "type": "RollingUpdate",
      "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 1}
    },
    "template": {
      "spec": {
        "topologySpreadConstraints": [
          {
            "maxSkew": 1,
            "topologyKey": "kubernetes.io/hostname",
            "whenUnsatisfiable": "DoNotSchedule",
            "labelSelector": {"matchLabels": {"kubevirt.io": "virt-operator"}}
          }
        ],
        "affinity": {
          "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [
              {
                "labelSelector": {"matchLabels": {"kubevirt.io": "virt-operator"}},
                "topologyKey": "kubernetes.io/hostname"
              }
            ],
            "preferredDuringSchedulingIgnoredDuringExecution": [
              {
                "weight": 100,
                "podAffinityTerm": {
                  "labelSelector": {"matchLabels": {"kubevirt.io": "virt-operator"}},
                  "topologyKey": "kubernetes.io/hostname"
                }
              }
            ]
          }
        }
      }
    }
  }
}'

echo "== tune virt-operator probes for nested lab recovery =="
${KUBECTL} -n "${NAMESPACE}" patch deployment virt-operator --type=strategic -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "virt-operator",
            "startupProbe": {
              "httpGet": {"scheme": "HTTPS", "path": "/metrics", "port": 8443},
              "failureThreshold": 36,
              "periodSeconds": 5,
              "timeoutSeconds": 10
            },
            "livenessProbe": {
              "httpGet": {"scheme": "HTTPS", "path": "/metrics", "port": 8443},
              "initialDelaySeconds": 60,
              "failureThreshold": 6,
              "periodSeconds": 10,
              "timeoutSeconds": 10
            },
            "readinessProbe": {
              "httpGet": {"scheme": "HTTPS", "path": "/metrics", "port": 8443},
              "initialDelaySeconds": 20,
              "failureThreshold": 12,
              "periodSeconds": 10,
              "timeoutSeconds": 10
            }
          }
        ]
      }
    }
  }
}'

cat <<'YAML' | ${KUBECTL} apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: virt-operator
  namespace: kubevirt
  labels:
    platform.privatecloud.local/ha-hardened: "true"
spec:
  minAvailable: 2
  selector:
    matchLabels:
      kubevirt.io: virt-operator
YAML

echo "== wait for KubeVirt components =="
${KUBECTL} -n "${NAMESPACE}" wait kubevirt/kubevirt --for=condition=Available --timeout=10m
${KUBECTL} -n "${NAMESPACE}" rollout status deployment/virt-api --timeout=10m
${KUBECTL} -n "${NAMESPACE}" rollout status deployment/virt-controller --timeout=10m
${KUBECTL} -n "${NAMESPACE}" rollout status deployment/virt-operator --timeout=10m

echo "KubeVirt HA configuration applied. Run verify-kubevirt-ha.sh."
