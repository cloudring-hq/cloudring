#!/usr/bin/env bash
set -euo pipefail

KUBECTL="${KUBECTL:-sudo k3s kubectl}"
NAMESPACE="${NAMESPACE:-platform-tests}"
DATAVOLUME_NAME="${DATAVOLUME_NAME:-cdi-blank-rootdisk}"
STORAGE_CLASS="${STORAGE_CLASS:-longhorn}"
SIZE="${SIZE:-128Mi}"

${KUBECTL} get crd datavolumes.cdi.kubevirt.io storageprofiles.cdi.kubevirt.io >/dev/null
${KUBECTL} -n cdi get cdi cdi -o jsonpath='{.status.phase}' | grep -qx Deployed
${KUBECTL} create namespace "${NAMESPACE}" --dry-run=client -o yaml | ${KUBECTL} apply -f -
${KUBECTL} -n "${NAMESPACE}" delete datavolume "${DATAVOLUME_NAME}" --ignore-not-found=true --wait=true

cat <<YAML | ${KUBECTL} apply -f -
apiVersion: cdi.kubevirt.io/v1beta1
kind: DataVolume
metadata:
  name: ${DATAVOLUME_NAME}
  namespace: ${NAMESPACE}
spec:
  source:
    blank: {}
  storage:
    storageClassName: ${STORAGE_CLASS}
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: ${SIZE}
YAML

for _ in $(seq 1 120); do
  phase="$(${KUBECTL} -n "${NAMESPACE}" get datavolume "${DATAVOLUME_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  pvc_phase="$(${KUBECTL} -n "${NAMESPACE}" get pvc "${DATAVOLUME_NAME}" -o jsonpath='{.status.phase}' 2>/dev/null || true)"
  echo "DataVolume phase=${phase:-missing} PVC phase=${pvc_phase:-missing}"
  [[ "${phase}" == "Succeeded" && "${pvc_phase}" == "Bound" ]] && break
  sleep 5
done

phase="$(${KUBECTL} -n "${NAMESPACE}" get datavolume "${DATAVOLUME_NAME}" -o jsonpath='{.status.phase}')"
pvc_phase="$(${KUBECTL} -n "${NAMESPACE}" get pvc "${DATAVOLUME_NAME}" -o jsonpath='{.status.phase}')"
[[ "${phase}" == "Succeeded" && "${pvc_phase}" == "Bound" ]] || {
  echo "expected DataVolume Succeeded and PVC Bound, got DataVolume=${phase} PVC=${pvc_phase}" >&2
  ${KUBECTL} -n "${NAMESPACE}" describe datavolume "${DATAVOLUME_NAME}" || true
  ${KUBECTL} -n "${NAMESPACE}" get pods,pvc,datavolume -o wide || true
  exit 1
}

${KUBECTL} -n "${NAMESPACE}" get datavolume,pvc "${DATAVOLUME_NAME}" -o wide
