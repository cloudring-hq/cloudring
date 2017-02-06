#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
REPLICAS="${REPLICAS:-3}"
MIN_AVAILABLE="${MIN_AVAILABLE:-2}"

patch_deployment() {
  local namespace="$1"
  local deployment="$2"
  local selector_json="$3"
  local container_name="${4:-}"
  local container_patch=""

  if [[ -n "${container_name}" ]]; then
    container_patch=",\"containers\":[{\"name\":\"${container_name}\",\"resources\":{\"requests\":{\"cpu\":\"50m\",\"memory\":\"128Mi\"},\"limits\":{\"cpu\":\"500m\",\"memory\":\"512Mi\"}},\"livenessProbe\":{\"timeoutSeconds\":5,\"failureThreshold\":6},\"readinessProbe\":{\"timeoutSeconds\":5,\"failureThreshold\":6}}]"
  fi

  ${KUBECTL} -n "${namespace}" patch deployment "${deployment}" --type=strategic -p "{
    \"spec\": {
      \"replicas\": ${REPLICAS},
      \"strategy\": {
        \"type\": \"RollingUpdate\",
        \"rollingUpdate\": {\"maxSurge\": 1, \"maxUnavailable\": 0}
      },
      \"template\": {
        \"spec\": {
          \"affinity\": {
            \"nodeAffinity\": {
              \"preferredDuringSchedulingIgnoredDuringExecution\": [
                {
                  \"weight\": 100,
                  \"preference\": {
                    \"matchExpressions\": [
                      {
                        \"key\": \"kubernetes.io/hostname\",
                        \"operator\": \"NotIn\",
                        \"values\": [\"n1\"]
                      }
                    ]
                  }
                }
              ]
            },
            \"podAntiAffinity\": {
              \"preferredDuringSchedulingIgnoredDuringExecution\": [
                {
                  \"weight\": 100,
                  \"podAffinityTerm\": {
                    \"labelSelector\": {\"matchLabels\": ${selector_json}},
                    \"topologyKey\": \"kubernetes.io/hostname\"
                  }
                }
              ]
            }
          },
          \"topologySpreadConstraints\": [
            {
              \"maxSkew\": 1,
              \"topologyKey\": \"kubernetes.io/hostname\",
              \"whenUnsatisfiable\": \"ScheduleAnyway\",
              \"labelSelector\": {\"matchLabels\": ${selector_json}}
            }
          ]${container_patch}
        }
      }
    }
  }"

  cat <<YAML | ${KUBECTL} apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ${deployment}
  namespace: ${namespace}
  labels:
    platform.privatecloud.local/ha-hardened: "true"
spec:
  minAvailable: ${MIN_AVAILABLE}
  selector:
    matchLabels: ${selector_json}
YAML

  ${KUBECTL} -n "${namespace}" rollout status "deployment/${deployment}" --timeout=5m
}

apply_pdb() {
  local namespace="$1"
  local deployment="$2"
  local selector_json="$3"

  cat <<YAML | ${KUBECTL} apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: ${deployment}
  namespace: ${namespace}
  labels:
    platform.privatecloud.local/ha-hardened: "true"
spec:
  minAvailable: ${MIN_AVAILABLE}
  selector:
    matchLabels: ${selector_json}
YAML
}

patch_cdi_operands() {
  ${KUBECTL} patch cdi cdi --type=merge -p "{
    \"spec\": {
      \"infra\": {
        \"apiServerReplicas\": ${REPLICAS},
        \"deploymentReplicas\": ${REPLICAS},
        \"uploadProxyReplicas\": ${REPLICAS},
        \"affinity\": {
          \"podAntiAffinity\": {
            \"preferredDuringSchedulingIgnoredDuringExecution\": [
              {
                \"weight\": 100,
                \"podAffinityTerm\": {
                  \"labelSelector\": {
                    \"matchExpressions\": [
                      {
                        \"key\": \"cdi.kubevirt.io\",
                        \"operator\": \"In\",
                        \"values\": [\"cdi-apiserver\", \"cdi-deployment\", \"cdi-uploadproxy\"]
                      }
                    ]
                  },
                  \"topologyKey\": \"kubernetes.io/hostname\"
                }
              }
            ]
          }
        }
      }
    }
  }"

  ${KUBECTL} patch cdi cdi --type=merge -p '{
    "spec": {
      "customizeComponents": {
        "patches": [
          {
            "resourceType": "Deployment",
            "resourceName": "cdi-apiserver",
            "type": "strategic",
            "patch": "{\"spec\":{\"strategy\":{\"type\":\"RollingUpdate\",\"rollingUpdate\":{\"maxSurge\":1,\"maxUnavailable\":0}},\"template\":{\"spec\":{\"topologySpreadConstraints\":[{\"maxSkew\":1,\"topologyKey\":\"kubernetes.io/hostname\",\"whenUnsatisfiable\":\"ScheduleAnyway\",\"labelSelector\":{\"matchLabels\":{\"cdi.kubevirt.io\":\"cdi-apiserver\"}}}]}}}}"
          },
          {
            "resourceType": "Deployment",
            "resourceName": "cdi-deployment",
            "type": "strategic",
            "patch": "{\"spec\":{\"strategy\":{\"type\":\"RollingUpdate\",\"rollingUpdate\":{\"maxSurge\":1,\"maxUnavailable\":0}},\"template\":{\"spec\":{\"topologySpreadConstraints\":[{\"maxSkew\":1,\"topologyKey\":\"kubernetes.io/hostname\",\"whenUnsatisfiable\":\"ScheduleAnyway\",\"labelSelector\":{\"matchLabels\":{\"cdi.kubevirt.io\":\"cdi-deployment\"}}}]}}}}"
          },
          {
            "resourceType": "Deployment",
            "resourceName": "cdi-uploadproxy",
            "type": "strategic",
            "patch": "{\"spec\":{\"strategy\":{\"type\":\"RollingUpdate\",\"rollingUpdate\":{\"maxSurge\":1,\"maxUnavailable\":0}},\"template\":{\"spec\":{\"topologySpreadConstraints\":[{\"maxSkew\":1,\"topologyKey\":\"kubernetes.io/hostname\",\"whenUnsatisfiable\":\"ScheduleAnyway\",\"labelSelector\":{\"matchLabels\":{\"cdi.kubevirt.io\":\"cdi-uploadproxy\"}}}]}}}}"
          }
        ]
      }
    }
  }'

  ${KUBECTL} -n cdi rollout status deployment/cdi-apiserver --timeout=5m
  ${KUBECTL} -n cdi rollout status deployment/cdi-deployment --timeout=5m
  ${KUBECTL} -n cdi rollout status deployment/cdi-uploadproxy --timeout=5m

  apply_pdb "cdi" "cdi-apiserver" '{"cdi.kubevirt.io":"cdi-apiserver"}'
  apply_pdb "cdi" "cdi-deployment" '{"cdi.kubevirt.io":"cdi-deployment"}'
  apply_pdb "cdi" "cdi-uploadproxy" '{"cdi.kubevirt.io":"cdi-uploadproxy"}'
}

patch_deployment "capi-system" "capi-controller-manager" \
  '{"cluster.x-k8s.io/provider":"cluster-api","control-plane":"controller-manager"}' \
  "manager"

patch_deployment "capi-kubeadm-bootstrap-system" "capi-kubeadm-bootstrap-controller-manager" \
  '{"cluster.x-k8s.io/provider":"bootstrap-kubeadm","control-plane":"controller-manager"}' \
  "manager"

patch_deployment "capi-kubeadm-control-plane-system" "capi-kubeadm-control-plane-controller-manager" \
  '{"cluster.x-k8s.io/provider":"control-plane-kubeadm","control-plane":"controller-manager"}' \
  "manager"

patch_deployment "capk-system" "capk-controller-manager" \
  '{"cluster.x-k8s.io/provider":"kubevirt","control-plane":"controller-manager"}' \
  "manager"

patch_deployment "cert-manager" "cert-manager" \
  '{"app.kubernetes.io/component":"controller","app.kubernetes.io/instance":"cert-manager","app.kubernetes.io/name":"cert-manager"}'

patch_deployment "cert-manager" "cert-manager-cainjector" \
  '{"app.kubernetes.io/component":"cainjector","app.kubernetes.io/instance":"cert-manager","app.kubernetes.io/name":"cainjector"}'

patch_deployment "cert-manager" "cert-manager-webhook" \
  '{"app.kubernetes.io/component":"webhook","app.kubernetes.io/instance":"cert-manager","app.kubernetes.io/name":"webhook"}'

if ${KUBECTL} -n cdi get deployment cdi-operator >/dev/null 2>&1; then
  patch_deployment "cdi" "cdi-operator" \
    '{"name":"cdi-operator","operator.cdi.kubevirt.io":""}'
  patch_cdi_operands
fi

${KUBECTL} get deployment -n capi-system capi-controller-manager
${KUBECTL} get deployment -n capi-kubeadm-bootstrap-system capi-kubeadm-bootstrap-controller-manager
${KUBECTL} get deployment -n capi-kubeadm-control-plane-system capi-kubeadm-control-plane-controller-manager
${KUBECTL} get deployment -n capk-system capk-controller-manager
${KUBECTL} get deployment -n cert-manager cert-manager cert-manager-cainjector cert-manager-webhook
${KUBECTL} get deployment -n cdi cdi-operator cdi-apiserver cdi-deployment cdi-uploadproxy 2>/dev/null || true
${KUBECTL} get pdb -A -l platform.privatecloud.local/ha-hardened=true
