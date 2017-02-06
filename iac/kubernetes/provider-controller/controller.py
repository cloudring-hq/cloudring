import base64
import copy
import hashlib
import json
import os
import socket
import ssl
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timedelta, timezone
from kubernetes import client, config
from kubernetes.client import ApiException

GROUP = "platform.privatecloud.local"
VERSION = "v1alpha1"
FINALIZER = "platform.privatecloud.local/finalizer"
FAILURE_DOMAIN_KEYS = ("region", "site", "zone", "rack", "network", "storage")


class MetricsRegistry:
    def __init__(self):
        self.lock = threading.Lock()
        self.identity = ""
        self.is_leader = 0
        self.shard_index = 0
        self.shard_total = 1
        self.owns_global = 1
        self.reconcile_total = {"success": 0, "error": 0, "standby": 0}
        self.retention_deleted_total = {}
        self.reconcile_duration_sum = 0.0
        self.reconcile_duration_count = 0
        self.last_success_timestamp = 0.0
        self.last_error_timestamp = 0.0

    def set_identity(self, identity):
        with self.lock:
            self.identity = identity

    def set_leader(self, is_leader):
        with self.lock:
            self.is_leader = 1 if is_leader else 0

    def set_shard(self, shard_index, shard_total, owns_global):
        with self.lock:
            self.shard_index = shard_index
            self.shard_total = shard_total
            self.owns_global = 1 if owns_global else 0

    def record_reconcile(self, result, duration):
        now = time.time()
        with self.lock:
            self.reconcile_total[result] = self.reconcile_total.get(result, 0) + 1
            if result in ("success", "error"):
                self.reconcile_duration_sum += max(duration, 0.0)
                self.reconcile_duration_count += 1
            if result == "success":
                self.last_success_timestamp = now
            if result == "error":
                self.last_error_timestamp = now

    def record_retention(self, resource, deleted):
        if deleted <= 0:
            return
        with self.lock:
            self.retention_deleted_total[resource] = self.retention_deleted_total.get(resource, 0) + deleted

    def render(self):
        with self.lock:
            identity = self.identity
            is_leader = self.is_leader
            shard_index = self.shard_index
            shard_total = self.shard_total
            owns_global = self.owns_global
            totals = dict(self.reconcile_total)
            retention_deleted = dict(self.retention_deleted_total)
            duration_sum = self.reconcile_duration_sum
            duration_count = self.reconcile_duration_count
            last_success = self.last_success_timestamp
            last_error = self.last_error_timestamp
        lines = [
            "# HELP provider_controller_leader Whether this replica currently holds the leader lease.",
            "# TYPE provider_controller_leader gauge",
            f'provider_controller_leader{{identity="{identity}"}} {is_leader}',
            "# HELP provider_controller_shard_info Static shard metadata for this controller replica.",
            "# TYPE provider_controller_shard_info gauge",
            (
                f'provider_controller_shard_info{{identity="{identity}",'
                f'shard_index="{shard_index}",shard_total="{shard_total}",'
                f'owns_global="{owns_global}"}} 1'
            ),
            "# HELP provider_controller_reconcile_total Reconcile loop attempts by result.",
            "# TYPE provider_controller_reconcile_total counter",
        ]
        for result in sorted(totals):
            lines.append(f'provider_controller_reconcile_total{{result="{result}"}} {totals[result]}')
        lines.extend(
            [
                "# HELP provider_controller_retention_deleted_total Provider control-plane audit/journal objects deleted by retention.",
                "# TYPE provider_controller_retention_deleted_total counter",
            ]
        )
        for resource, value in sorted(retention_deleted.items()):
            lines.append(f'provider_controller_retention_deleted_total{{resource="{resource}"}} {value}')
        lines.extend(
            [
                "# HELP provider_controller_reconcile_duration_seconds_sum Total reconcile duration for active leader loops.",
                "# TYPE provider_controller_reconcile_duration_seconds_sum counter",
                f"provider_controller_reconcile_duration_seconds_sum {duration_sum:.6f}",
                "# HELP provider_controller_reconcile_duration_seconds_count Count of active leader reconcile loops with duration samples.",
                "# TYPE provider_controller_reconcile_duration_seconds_count counter",
                f"provider_controller_reconcile_duration_seconds_count {duration_count}",
                "# HELP provider_controller_last_success_timestamp_seconds Unix timestamp of the last successful active reconcile.",
                "# TYPE provider_controller_last_success_timestamp_seconds gauge",
                f"provider_controller_last_success_timestamp_seconds {last_success:.0f}",
                "# HELP provider_controller_last_error_timestamp_seconds Unix timestamp of the last failed active reconcile or leader-election error.",
                "# TYPE provider_controller_last_error_timestamp_seconds gauge",
                f"provider_controller_last_error_timestamp_seconds {last_error:.0f}",
            ]
        )
        return "\n".join(lines) + "\n"


METRICS = MetricsRegistry()


def start_metrics_server(port):
    class MetricsHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/healthz":
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"ok\n")
                return
            if self.path != "/metrics":
                self.send_response(404)
                self.end_headers()
                return
            payload = METRICS.render().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, _format, *_args):
            return

    server = ThreadingHTTPServer(("0.0.0.0", port), MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def load_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


def deep_merge(base, overlay):
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_utc_datetime(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def cpu_to_millicores(value):
    text = str(value or "0")
    if text.endswith("m"):
        return int(text[:-1])
    return int(float(text) * 1000)


def memory_to_mib(value):
    text = str(value or "0")
    units = {
        "Ki": 1 / 1024,
        "Mi": 1,
        "Gi": 1024,
        "Ti": 1024 * 1024,
        "K": 1 / 1000,
        "M": 1000 / 1024,
        "G": 1000 * 1000 / 1024,
        "T": 1000 * 1000 * 1000 / 1024,
    }
    for suffix, multiplier in units.items():
        if text.endswith(suffix):
            return int(float(text[: -len(suffix)]) * multiplier)
    return int(float(text) / (1024 * 1024))


def cpu_millicores_to_text(value):
    return f"{int(value)}m"


def memory_mib_to_text(value):
    return f"{int(value)}Mi"


def dns_label_name(raw, max_length=63):
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in raw.lower()).strip("-")
    if not cleaned:
        cleaned = "x"
    if len(cleaned) <= max_length:
        return cleaned
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"{cleaned[: max_length - 9].rstrip('-')}-{digest}"


def stable_shard(value, shard_total):
    if shard_total <= 1:
        return 0
    digest = hashlib.sha1(str(value).encode("utf-8")).hexdigest()
    return int(digest[:12], 16) % shard_total


def env_int(name, default):
    raw = os.environ.get(name, str(default))
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from exc


def env_bool(name, default):
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def ensure_namespaced(api_method_read, api_method_create, api_method_patch, name, namespace, body):
    try:
        existing = api_method_read(name=name, namespace=namespace)
        api_method_patch(name=name, namespace=namespace, body=body)
        return existing
    except ApiException as exc:
        if exc.status != 404:
            raise
        return api_method_create(namespace=namespace, body=body)


def ensure_clustered(api_method_read, api_method_create, api_method_patch, name, body):
    try:
        existing = api_method_read(name=name)
        api_method_patch(name=name, body=body)
        return existing
    except ApiException as exc:
        if exc.status != 404:
            raise
        return api_method_create(body=body)


class ProviderController:
    def __init__(self):
        self.core = client.CoreV1Api()
        self.net = client.NetworkingV1Api()
        self.rbac = client.RbacAuthorizationV1Api()
        self.apps = client.AppsV1Api()
        self.policy = client.PolicyV1Api()
        self.coordination = client.CoordinationV1Api()
        self.custom = client.CustomObjectsApi()
        self.identity = os.environ.get("POD_NAME") or os.environ.get("HOSTNAME") or f"provider-controller-{os.getpid()}"
        self.admission_lock_namespace = os.environ.get("CAPACITY_ADMISSION_LOCK_NAMESPACE", "platform-system")
        self.admission_lock_duration_seconds = max(5, env_int("CAPACITY_ADMISSION_LOCK_DURATION_SECONDS", 30))
        self.admission_lock_timeout_seconds = max(0, env_int("CAPACITY_ADMISSION_LOCK_TIMEOUT_SECONDS", 20))
        self.admission_lock_poll_seconds = max(1, env_int("CAPACITY_ADMISSION_LOCK_POLL_SECONDS", 1))
        self.reservation_ttl_seconds = int(os.environ.get("CAPACITY_RESERVATION_TTL_SECONDS", "300"))
        self.retention_reaper_interval_seconds = max(
            0, env_int("CONTROL_PLANE_RETENTION_REAPER_INTERVAL_SECONDS", 60)
        )
        self.admission_journal_retention_seconds = max(
            0, env_int("ADMISSION_JOURNAL_RETENTION_SECONDS", 7 * 24 * 60 * 60)
        )
        self.admission_journal_max_records_per_project = max(
            0, env_int("ADMISSION_JOURNAL_MAX_RECORDS_PER_PROJECT", 5000)
        )
        self.self_service_audit_retention_seconds = max(
            0, env_int("SELF_SERVICE_AUDIT_RETENTION_SECONDS", 7 * 24 * 60 * 60)
        )
        self.self_service_audit_max_records_per_namespace = max(
            0, env_int("SELF_SERVICE_AUDIT_MAX_RECORDS_PER_NAMESPACE", 1000)
        )
        self.last_retention_reaper_time = 0.0
        self.tenant_api_readyz_failure_threshold = max(1, env_int("TENANT_API_READYZ_FAILURE_THRESHOLD", 3))
        self.tenant_api_proxy_max_replicas = max(1, env_int("TENANT_API_PROXY_MAX_REPLICAS", 3))
        self.tenant_api_kubeconfig_insecure_skip_tls_verify = env_bool(
            "TENANT_API_KUBECONFIG_INSECURE_SKIP_TLS_VERIFY", True
        )
        self.shard_total = max(1, env_int("CONTROLLER_SHARD_TOTAL", 1))
        self.shard_index = env_int("CONTROLLER_SHARD_INDEX", 0)
        if self.shard_index < 0 or self.shard_index >= self.shard_total:
            raise ValueError(
                "CONTROLLER_SHARD_INDEX must be between 0 and "
                f"CONTROLLER_SHARD_TOTAL-1, got {self.shard_index}/{self.shard_total}"
            )
        self.global_shard_index = env_int("CONTROLLER_GLOBAL_SHARD_INDEX", 0)
        if self.global_shard_index < 0 or self.global_shard_index >= self.shard_total:
            raise ValueError(
                "CONTROLLER_GLOBAL_SHARD_INDEX must be between 0 and "
                f"CONTROLLER_SHARD_TOTAL-1, got {self.global_shard_index}/{self.shard_total}"
            )
        self.namespace_allowlist = {
            item.strip()
            for item in os.environ.get("CONTROLLER_NAMESPACE_ALLOWLIST", "").split(",")
            if item.strip()
        }
        METRICS.set_shard(self.shard_index, self.shard_total, self.owns_global_resources())

    def run_once(self):
        self.reconcile_capacity_reservations()
        if self.owns_global_resources():
            self.reconcile_capacity_cells()
            self.reconcile_projects()
            self.reconcile_product_plans()
            self.reconcile_images()
            self.reconcile_control_plane_retention()
        self.reconcile_orders()
        self.reconcile_subscriptions()
        self.reconcile_orders()
        self.reconcile_volumes()
        self.reconcile_networks()
        self.reconcile_firewall_rules()
        self.reconcile_backup_plans()
        self.reconcile_restore_requests()
        self.reconcile_access_grants()
        self.reconcile_vm_claims()
        self.reconcile_cluster_claims()
        self.reconcile_capacity_reservations()
        if self.owns_global_resources():
            self.reconcile_capacity_cells()

    def reconcile_control_plane_retention(self):
        now = time.time()
        if (
            self.retention_reaper_interval_seconds > 0
            and now - self.last_retention_reaper_time < self.retention_reaper_interval_seconds
        ):
            return
        self.prune_admission_journals()
        self.prune_self_service_audit_events()
        self.last_retention_reaper_time = now

    def retention_timestamp(self, item, spec_field):
        spec = item.get("spec", {})
        metadata = item.get("metadata", {})
        return (
            parse_utc_datetime(spec.get(spec_field))
            or parse_utc_datetime(metadata.get("creationTimestamp"))
        )

    def retention_candidates(self, items, spec_field, ttl_seconds, max_records_per_group, group_func):
        now = datetime.now(timezone.utc)
        candidates = {}
        grouped = {}
        for item in items:
            metadata = item.get("metadata", {})
            name = metadata.get("name")
            if not name:
                continue
            key = (metadata.get("namespace", ""), name)
            timestamp = self.retention_timestamp(item, spec_field)
            if ttl_seconds > 0 and timestamp and (now - timestamp).total_seconds() > ttl_seconds:
                candidates[key] = item
                continue
            group = group_func(item)
            grouped.setdefault(group, []).append((timestamp or datetime.min.replace(tzinfo=timezone.utc), item))
        if max_records_per_group > 0:
            for group_items in grouped.values():
                group_items.sort(
                    key=lambda entry: (
                        entry[0],
                        entry[1].get("metadata", {}).get("creationTimestamp", ""),
                        entry[1].get("metadata", {}).get("name", ""),
                    ),
                    reverse=True,
                )
                for _, item in group_items[max_records_per_group:]:
                    metadata = item.get("metadata", {})
                    candidates[(metadata.get("namespace", ""), metadata["name"])] = item
        return list(candidates.values())

    def prune_admission_journals(self):
        if self.admission_journal_retention_seconds <= 0 and self.admission_journal_max_records_per_project <= 0:
            return
        try:
            journals = self.custom.list_cluster_custom_object(GROUP, VERSION, "admissionjournals")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        candidates = self.retention_candidates(
            journals.get("items", []),
            "observedAt",
            self.admission_journal_retention_seconds,
            self.admission_journal_max_records_per_project,
            lambda item: item.get("spec", {}).get("projectRef", ""),
        )
        deleted = 0
        for journal in candidates:
            name = journal["metadata"]["name"]
            try:
                self.custom.delete_cluster_custom_object(GROUP, VERSION, "admissionjournals", name)
                deleted += 1
            except ApiException as exc:
                if exc.status != 404:
                    raise
        if deleted:
            print(f"retention deleted admissionjournals={deleted}", flush=True)
            METRICS.record_retention("admissionjournals", deleted)

    def prune_self_service_audit_events(self):
        if self.self_service_audit_retention_seconds <= 0 and self.self_service_audit_max_records_per_namespace <= 0:
            return
        try:
            events = self.custom.list_cluster_custom_object(GROUP, VERSION, "selfserviceauditevents")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        candidates = self.retention_candidates(
            events.get("items", []),
            "timestamp",
            self.self_service_audit_retention_seconds,
            self.self_service_audit_max_records_per_namespace,
            lambda item: item.get("metadata", {}).get("namespace", ""),
        )
        deleted = 0
        for event in candidates:
            metadata = event.get("metadata", {})
            namespace = metadata.get("namespace")
            name = metadata.get("name")
            if not namespace or not name:
                continue
            try:
                self.custom.delete_namespaced_custom_object(
                    GROUP, VERSION, namespace, "selfserviceauditevents", name
                )
                deleted += 1
            except ApiException as exc:
                if exc.status != 404:
                    raise
        if deleted:
            print(f"retention deleted selfserviceauditevents={deleted}", flush=True)
            METRICS.record_retention("selfserviceauditevents", deleted)

    def owns_global_resources(self):
        return self.shard_index == self.global_shard_index

    def owns_namespace(self, namespace):
        if not namespace:
            return self.owns_global_resources()
        if self.namespace_allowlist:
            return namespace in self.namespace_allowlist
        return stable_shard(namespace, self.shard_total) == self.shard_index

    def owned_namespaced_items(self, collection):
        for item in collection.get("items", []):
            namespace = item.get("metadata", {}).get("namespace", "")
            if self.owns_namespace(namespace):
                yield item

    def reconcile_projects(self):
        projects = self.custom.list_cluster_custom_object(GROUP, VERSION, "projects")
        for project in projects.get("items", []):
            spec = project.get("spec", {})
            name = project["metadata"]["name"]
            tenant = spec.get("tenantId", name)
            tier = spec.get("tier", "shared")
            admins_group = spec.get("adminsGroup") or f"platform:{tenant}:admins"
            quotas = spec.get("quotas", {})
            network = spec.get("network", {})

            labels = {
                "tenant": tenant,
                "platform.privatecloud.local/project": name,
                "platform.privatecloud.local/tenant-tier": tier,
                "pod-security.kubernetes.io/enforce": "baseline",
                "pod-security.kubernetes.io/warn": "restricted",
                "pod-security.kubernetes.io/audit": "restricted",
            }

            ns_body = client.V1Namespace(
                metadata=client.V1ObjectMeta(name=tenant, labels=labels)
            )
            ensure_clustered(
                self.core.read_namespace,
                self.core.create_namespace,
                self.core.patch_namespace,
                tenant,
                ns_body,
            )

            rq_body = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(name="tenant-quota", namespace=tenant),
                spec=client.V1ResourceQuotaSpec(
                    hard={
                        "requests.cpu": str(quotas.get("cpu", "2")),
                        "requests.memory": str(quotas.get("memory", "2Gi")),
                        "limits.cpu": str(quotas.get("cpuLimit", quotas.get("cpu", "2"))),
                        "limits.memory": str(quotas.get("memoryLimit", quotas.get("memory", "2Gi"))),
                        "pods": str(quotas.get("pods", "20")),
                        "persistentvolumeclaims": str(quotas.get("volumes", "8")),
                    }
                ),
            )
            ensure_namespaced(
                self.core.read_namespaced_resource_quota,
                self.core.create_namespaced_resource_quota,
                self.core.patch_namespaced_resource_quota,
                "tenant-quota",
                tenant,
                rq_body,
            )

            object_quota_body = client.V1ResourceQuota(
                metadata=client.V1ObjectMeta(name="tenant-object-quota", namespace=tenant),
                spec=client.V1ResourceQuotaSpec(
                    hard={
                        "configmaps": "50",
                        "secrets": "50",
                        "services": "20",
                        "services.loadbalancers": str(network.get("allowedLoadBalancers", 0)),
                        "count/virtualmachines.kubevirt.io": str(quotas.get("vms", 10)),
                    }
                ),
            )
            ensure_namespaced(
                self.core.read_namespaced_resource_quota,
                self.core.create_namespaced_resource_quota,
                self.core.patch_namespaced_resource_quota,
                "tenant-object-quota",
                tenant,
                object_quota_body,
            )

            limit_body = client.V1LimitRange(
                metadata=client.V1ObjectMeta(name="tenant-limits", namespace=tenant),
                spec=client.V1LimitRangeSpec(
                    limits=[
                        client.V1LimitRangeItem(
                            type="Container",
                            default={"cpu": "500m", "memory": "512Mi"},
                            default_request={"cpu": "50m", "memory": "64Mi"},
                        )
                    ]
                ),
            )
            ensure_namespaced(
                self.core.read_namespaced_limit_range,
                self.core.create_namespaced_limit_range,
                self.core.patch_namespaced_limit_range,
                "tenant-limits",
                tenant,
                limit_body,
            )

            if network.get("defaultDeny", True):
                self.ensure_default_deny(tenant)
            self.ensure_dns_egress(tenant)
            self.ensure_cdi_importer_egress(tenant)
            self.ensure_tenant_rbac(tenant, admins_group)
            self.ensure_tenant_self_service_rbac(tenant, admins_group)

            self.custom.patch_cluster_custom_object_status(
                GROUP,
                VERSION,
                "projects",
                name,
                {
                    "status": {
                        "phase": "Ready",
                        "namespaces": [tenant],
                        "quotaUsage": self.project_quota_usage(name),
                    }
                },
            )

    def reconcile_capacity_cells(self):
        cells = self.custom.list_cluster_custom_object(GROUP, VERSION, "capacitycells")
        nodes = self.core.list_node().items
        for cell in cells.get("items", []):
            name = cell["metadata"]["name"]
            spec = cell.get("spec", {})
            selector = spec.get("nodeSelector", {})
            matched = [node for node in nodes if self.node_matches_selector(node, selector)]
            ready = [node for node in matched if self.node_is_ready(node)]

            cpu_m = 0
            memory_mi = 0
            pods = 0
            node_names = []
            for node in matched:
                node_names.append(node.metadata.name)
                allocatable = node.status.allocatable or {}
                cpu_m += cpu_to_millicores(allocatable.get("cpu", "0"))
                memory_mi += memory_to_mib(allocatable.get("memory", "0"))
                pods += int(allocatable.get("pods", "0"))

            phase = "Ready" if matched and len(ready) == len(matched) else "Degraded"
            if not matched:
                phase = "PendingNodes"
            reserved = self.capacity_cell_reservations(name)
            available_cpu_m = max(cpu_m - reserved["cpu"], 0)
            available_memory_mi = max(memory_mi - reserved["memory"], 0)
            self.custom.patch_cluster_custom_object_status(
                GROUP,
                VERSION,
                "capacitycells",
                name,
                {
                    "status": {
                        "phase": phase,
                        "nodeCount": len(matched),
                        "readyNodeCount": len(ready),
                        "allocatable": {
                            "cpu": f"{cpu_m}m",
                            "memory": f"{memory_mi}Mi",
                            "pods": str(pods),
                        },
                        "reserved": {
                            "cpu": cpu_millicores_to_text(reserved["cpu"]),
                            "memory": memory_mib_to_text(reserved["memory"]),
                            "claims": reserved["claims"],
                        },
                        "available": {
                            "cpu": cpu_millicores_to_text(available_cpu_m),
                            "memory": memory_mib_to_text(available_memory_mi),
                            "pods": str(pods),
                        },
                        "nodes": sorted(node_names),
                        "conditions": [
                            {
                                "type": "InventoryReady",
                                "status": "True" if phase == "Ready" else "False",
                                "reason": phase,
                                "message": f"{len(ready)}/{len(matched)} nodes Ready for capacity cell {name}",
                                "lastTransitionTime": utc_now(),
                            }
                        ],
                    }
                },
            )

    def capacity_cell_reservations(self, cell_name, exclude=None):
        reserved = {"cpu": 0, "memory": 0, "claims": 0}
        reservation_claim_keys = set()
        try:
            reservations = self.custom.list_cluster_custom_object(GROUP, VERSION, "capacityreservations")
            for reservation in reservations.get("items", []):
                spec = reservation.get("spec", {})
                status = reservation.get("status", {})
                key = self.reservation_claim_key(spec.get("claimRef", {}))
                if status.get("phase") != "Active":
                    continue
                if self.reservation_is_stale(reservation):
                    continue
                if spec.get("capacityCell") != cell_name:
                    continue
                if exclude and key == exclude:
                    continue
                if key:
                    reservation_claim_keys.add(key)
                resources = spec.get("resources", {})
                reserved["cpu"] += cpu_to_millicores(resources.get("cpu", "0"))
                reserved["memory"] += memory_to_mib(resources.get("memory", "0"))
                reserved["claims"] += 1
        except ApiException as exc:
            if exc.status != 404:
                raise

        for plural in ("virtualmachineclaims", "kubernetesclusterclaims"):
            claims = self.custom.list_cluster_custom_object(GROUP, VERSION, plural)
            for claim in claims.get("items", []):
                key = (
                    plural,
                    claim["metadata"].get("namespace", ""),
                    claim["metadata"]["name"],
                )
                if exclude and key == exclude:
                    continue
                if key in reservation_claim_keys:
                    continue
                admission = claim.get("status", {}).get("admission", {})
                if admission.get("phase") != "Admitted":
                    continue
                if admission.get("capacityCell") != cell_name:
                    continue
                resources = admission.get("estimatedResources", {})
                reserved["cpu"] += cpu_to_millicores(resources.get("cpu", "0"))
                reserved["memory"] += memory_to_mib(resources.get("memory", "0"))
                reserved["claims"] += 1
        return reserved

    def capacity_admission_lock_name(self, cell_name):
        return dns_label_name(f"capacity-admission-{cell_name}")

    def lease_time(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return parse_utc_datetime(value)

    def lease_timestamp(self, value):
        if not isinstance(value, datetime):
            value = self.lease_time(value) or datetime.now(timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")

    def try_acquire_capacity_admission_lock(self, cell_name):
        lock_name = self.capacity_admission_lock_name(cell_name)
        now = datetime.now(timezone.utc)
        try:
            lease = self.coordination.read_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise
            body = {
                "apiVersion": "coordination.k8s.io/v1",
                "kind": "Lease",
                "metadata": {
                    "name": lock_name,
                    "namespace": self.admission_lock_namespace,
                    "labels": {
                        "app": "provider-controller",
                        "platform.privatecloud.local/capacity-admission-lock": "true",
                        "platform.privatecloud.local/capacity-cell": cell_name,
                    },
                },
                "spec": {
                    "holderIdentity": self.identity,
                    "leaseDurationSeconds": self.admission_lock_duration_seconds,
                    "acquireTime": self.lease_timestamp(now),
                    "renewTime": self.lease_timestamp(now),
                    "leaseTransitions": 0,
                },
            }
            try:
                self.coordination.create_namespaced_lease(self.admission_lock_namespace, body)
                return True
            except ApiException as create_exc:
                if create_exc.status == 409:
                    return False
                raise

        spec = lease.spec
        holder = getattr(spec, "holder_identity", None) if spec else None
        is_holder = holder == self.identity
        renew_time = self.lease_time(
            (getattr(spec, "renew_time", None) if spec else None)
            or (getattr(spec, "acquire_time", None) if spec else None)
        )
        duration = (
            getattr(spec, "lease_duration_seconds", None)
            if spec and getattr(spec, "lease_duration_seconds", None)
            else self.admission_lock_duration_seconds
        )
        expired = not renew_time or (now - renew_time).total_seconds() > int(duration)
        if holder and not is_holder and not expired:
            return False

        transitions = (getattr(spec, "lease_transitions", None) if spec else None) or 0
        if not is_holder:
            transitions += 1
        acquire_time = getattr(spec, "acquire_time", None) if spec else None
        if not is_holder or not acquire_time:
            acquire_time = now
        body = {
            "metadata": {
                "name": lock_name,
                "namespace": self.admission_lock_namespace,
                "resourceVersion": lease.metadata.resource_version,
            },
            "spec": {
                "holderIdentity": self.identity,
                "leaseDurationSeconds": self.admission_lock_duration_seconds,
                "acquireTime": self.lease_timestamp(acquire_time),
                "renewTime": self.lease_timestamp(now),
                "leaseTransitions": transitions,
            },
        }
        try:
            self.coordination.patch_namespaced_lease(lock_name, self.admission_lock_namespace, body)
            return True
        except ApiException as exc:
            if exc.status == 409:
                return False
            raise

    def acquire_capacity_admission_lock(self, cell_name, plural, namespace, name):
        deadline = time.time() + self.admission_lock_timeout_seconds
        while True:
            if self.try_acquire_capacity_admission_lock(cell_name):
                return True
            if time.time() >= deadline:
                print(
                    f"capacity admission lock busy for cell={cell_name} claim={plural}/{namespace}/{name}",
                    flush=True,
                )
                return False
            time.sleep(self.admission_lock_poll_seconds)

    def release_capacity_admission_lock(self, cell_name):
        lock_name = self.capacity_admission_lock_name(cell_name)
        try:
            lease = self.coordination.read_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        spec = lease.spec
        holder = getattr(spec, "holder_identity", None) if spec else None
        if holder != self.identity:
            return
        try:
            self.coordination.delete_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def pending_admission_lock_status(self, cell_name, service_class_name=None):
        return {
            "phase": "Pending",
            "reason": "CapacityAdmissionLocked",
            "message": f"capacity cell {cell_name} admission lock is held by another controller; retrying",
            "capacityCell": cell_name,
            "serviceClass": service_class_name or "",
        }

    def project_quota_admission_lock_name(self, project_name):
        return dns_label_name(f"project-quota-admission-{project_name}")

    def try_acquire_project_quota_admission_lock(self, project_name):
        lock_name = self.project_quota_admission_lock_name(project_name)
        now = datetime.now(timezone.utc)
        try:
            lease = self.coordination.read_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise
            body = {
                "apiVersion": "coordination.k8s.io/v1",
                "kind": "Lease",
                "metadata": {
                    "name": lock_name,
                    "namespace": self.admission_lock_namespace,
                    "labels": {
                        "app": "provider-controller",
                        "platform.privatecloud.local/project-quota-admission-lock": "true",
                        "platform.privatecloud.local/project": project_name,
                    },
                },
                "spec": {
                    "holderIdentity": self.identity,
                    "leaseDurationSeconds": self.admission_lock_duration_seconds,
                    "acquireTime": self.lease_timestamp(now),
                    "renewTime": self.lease_timestamp(now),
                    "leaseTransitions": 0,
                },
            }
            try:
                self.coordination.create_namespaced_lease(self.admission_lock_namespace, body)
                return True
            except ApiException as create_exc:
                if create_exc.status == 409:
                    return False
                raise

        spec = lease.spec
        holder = getattr(spec, "holder_identity", None) if spec else None
        is_holder = holder == self.identity
        renew_time = self.lease_time(
            (getattr(spec, "renew_time", None) if spec else None)
            or (getattr(spec, "acquire_time", None) if spec else None)
        )
        duration = (
            getattr(spec, "lease_duration_seconds", None)
            if spec and getattr(spec, "lease_duration_seconds", None)
            else self.admission_lock_duration_seconds
        )
        expired = not renew_time or (now - renew_time).total_seconds() > int(duration)
        if holder and not is_holder and not expired:
            return False

        transitions = (getattr(spec, "lease_transitions", None) if spec else None) or 0
        if not is_holder:
            transitions += 1
        acquire_time = getattr(spec, "acquire_time", None) if spec else None
        if not is_holder or not acquire_time:
            acquire_time = now
        body = {
            "metadata": {
                "name": lock_name,
                "namespace": self.admission_lock_namespace,
                "resourceVersion": lease.metadata.resource_version,
            },
            "spec": {
                "holderIdentity": self.identity,
                "leaseDurationSeconds": self.admission_lock_duration_seconds,
                "acquireTime": self.lease_timestamp(acquire_time),
                "renewTime": self.lease_timestamp(now),
                "leaseTransitions": transitions,
            },
        }
        try:
            self.coordination.patch_namespaced_lease(lock_name, self.admission_lock_namespace, body)
            return True
        except ApiException as exc:
            if exc.status == 409:
                return False
            raise

    def acquire_project_quota_admission_lock(self, project_name, plural, namespace, name):
        deadline = time.time() + self.admission_lock_timeout_seconds
        while True:
            if self.try_acquire_project_quota_admission_lock(project_name):
                return True
            if time.time() >= deadline:
                print(
                    f"project quota admission lock busy for project={project_name} claim={plural}/{namespace}/{name}",
                    flush=True,
                )
                return False
            time.sleep(self.admission_lock_poll_seconds)

    def release_project_quota_admission_lock(self, project_name):
        lock_name = self.project_quota_admission_lock_name(project_name)
        try:
            lease = self.coordination.read_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        spec = lease.spec
        holder = getattr(spec, "holder_identity", None) if spec else None
        if holder != self.identity:
            return
        try:
            self.coordination.delete_namespaced_lease(lock_name, self.admission_lock_namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def pending_project_quota_lock_status(self, project_name):
        return {
            "phase": "Pending",
            "reason": "ProjectQuotaAdmissionLocked",
            "message": f"project {project_name} quota admission lock is held by another controller; retrying",
        }

    def claim_project_lock_target(self, spec, namespace):
        project, project_rejection = self.claim_project(spec, namespace)
        if project_rejection:
            return None, project_rejection
        return project["metadata"]["name"], None

    def should_publish_pending_lock(self, claim):
        return claim.get("status", {}).get("admission", {}).get("phase") != "Admitted"

    def current_admitted_generation(self, claim):
        admission = claim.get("status", {}).get("admission", {})
        if admission.get("phase") != "Admitted":
            return None
        try:
            observed = int(admission.get("observedGeneration", 0) or 0)
            generation = int(claim.get("metadata", {}).get("generation", 0) or 0)
        except (TypeError, ValueError):
            return None
        if observed and observed == generation:
            return copy.deepcopy(admission)
        return None

    def legacy_admitted_generation(self, plural, namespace, name, claim):
        admission = claim.get("status", {}).get("admission", {})
        if admission.get("phase") != "Admitted" or admission.get("observedGeneration"):
            return None
        if not self.backing_claim_exists(plural, namespace, name):
            return None
        return self.mark_admission_observed(admission, claim)

    def mark_admission_observed(self, admission, claim):
        observed = copy.deepcopy(admission)
        observed["observedGeneration"] = int(claim.get("metadata", {}).get("generation", 1) or 1)
        return observed

    def effective_workers_from_admission(self, admission):
        workers = {}
        for item in admission.get("effectiveWorkerReplicas", []) or []:
            name = item.get("name", "default")
            try:
                workers[name] = int(item.get("admitted", 0) or 0)
            except (TypeError, ValueError):
                workers[name] = 0
        return workers

    def vm_claim_lock_target(self, spec):
        service_class_name = spec.get("placement", {}).get("serviceClass") or f"{spec.get('class', 'tiny')}-vm"
        cell, service_class, rejection = self.resolve_capacity_cell(
            spec.get("placement", {}), "vm", service_class_name
        )
        if rejection:
            return None, None
        return cell["metadata"]["name"], service_class.get("name")

    def cluster_claim_lock_target(self, spec):
        service_class_name = (
            spec.get("placement", {}).get("serviceClass")
            or f"{spec.get('controlPlane', {}).get('class', 'tiny')}-tenant-kubernetes"
        )
        cell, service_class, rejection = self.resolve_capacity_cell(
            spec.get("placement", {}), "tenant-kubernetes", service_class_name
        )
        if rejection:
            return None, None
        return cell["metadata"]["name"], service_class.get("name")

    def reservation_claim_key(self, claim_ref):
        kind = claim_ref.get("kind")
        plural = {
            "VirtualMachineClaim": "virtualmachineclaims",
            "KubernetesClusterClaim": "kubernetesclusterclaims",
        }.get(kind)
        namespace = claim_ref.get("namespace")
        name = claim_ref.get("name")
        if not plural or not namespace or not name:
            return None
        return (plural, namespace, name)

    def reservation_name(self, plural, namespace, name):
        prefix = {
            "virtualmachineclaims": "vmc",
            "kubernetesclusterclaims": "kcc",
        }.get(plural, "claim")
        raw = f"{prefix}-{namespace}-{name}".lower()
        return dns_label_name(raw)

    def ensure_finalizer(self, plural, namespace, name, obj):
        finalizers = list(obj.get("metadata", {}).get("finalizers") or [])
        if FINALIZER in finalizers:
            return False
        finalizers.append(FINALIZER)
        self.custom.patch_namespaced_custom_object(
            GROUP,
            VERSION,
            namespace,
            plural,
            name,
            {"metadata": {"finalizers": finalizers}},
        )
        return True

    def remove_finalizer(self, plural, namespace, name, obj):
        finalizers = [item for item in obj.get("metadata", {}).get("finalizers") or [] if item != FINALIZER]
        self.custom.patch_namespaced_custom_object(
            GROUP,
            VERSION,
            namespace,
            plural,
            name,
            {"metadata": {"finalizers": finalizers}},
        )

    def reservation_is_stale(self, reservation):
        status = reservation.get("status", {})
        expires_at = parse_utc_datetime(status.get("expiresAt"))
        if expires_at:
            return expires_at < datetime.now(timezone.utc)
        heartbeat = parse_utc_datetime(status.get("lastHeartbeatTime"))
        ttl = int(status.get("reservationTTLSeconds") or self.reservation_ttl_seconds)
        if not heartbeat:
            return False
        return heartbeat + timedelta(seconds=ttl) < datetime.now(timezone.utc)

    def ensure_capacity_reservation(self, plural, namespace, name, claim, admission):
        resources = admission.get("estimatedResources", {})
        if admission.get("phase") != "Admitted" or not resources:
            self.delete_capacity_reservation(plural, namespace, name)
            return
        kind = {
            "virtualmachineclaims": "VirtualMachineClaim",
            "kubernetesclusterclaims": "KubernetesClusterClaim",
        }[plural]
        reservation_name = self.reservation_name(plural, namespace, name)
        body = {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "CapacityReservation",
            "metadata": {
                "name": reservation_name,
                "labels": {
                    "platform.privatecloud.local/managed-by": "provider-controller",
                    "platform.privatecloud.local/capacity-cell": admission.get("capacityCell", ""),
                    "platform.privatecloud.local/claim-namespace": namespace,
                    "platform.privatecloud.local/claim-name": name,
                },
            },
            "spec": {
                "claimRef": {
                    "apiGroup": GROUP,
                    "kind": kind,
                    "namespace": namespace,
                    "name": name,
                    "uid": claim["metadata"].get("uid", ""),
                },
                "capacityCell": admission.get("capacityCell"),
                "serviceClass": admission.get("serviceClass"),
                "resources": {
                    "cpu": resources.get("cpu", "0"),
                    "memory": resources.get("memory", "0"),
                },
            },
        }
        self.apply_cluster_object(GROUP, VERSION, "capacityreservations", reservation_name, body)
        now = datetime.now(timezone.utc).replace(microsecond=0)
        expires_at = now + timedelta(seconds=self.reservation_ttl_seconds)
        self.custom.patch_cluster_custom_object_status(
            GROUP,
            VERSION,
            "capacityreservations",
            reservation_name,
            {
                "status": {
                    "phase": "Active",
                    "observedGeneration": claim["metadata"].get("generation", 1),
                    "reservationTTLSeconds": self.reservation_ttl_seconds,
                    "lastHeartbeatTime": now.isoformat().replace("+00:00", "Z"),
                    "expiresAt": expires_at.isoformat().replace("+00:00", "Z"),
                    "conditions": [
                        {
                            "type": "Reserved",
                            "status": "True",
                            "reason": "ClaimAdmitted",
                            "message": f"{kind} {namespace}/{name} reserves capacity in {admission.get('capacityCell')}",
                            "lastTransitionTime": now.isoformat().replace("+00:00", "Z"),
                        }
                    ],
                }
            },
        )

    def delete_capacity_reservation(self, plural, namespace, name):
        reservation_name = self.reservation_name(plural, namespace, name)
        try:
            self.custom.delete_cluster_custom_object(GROUP, VERSION, "capacityreservations", reservation_name)
        except ApiException as exc:
            if exc.status not in (404,):
                raise

    def admission_claim_kind(self, plural):
        return {
            "virtualmachineclaims": "VirtualMachineClaim",
            "kubernetesclusterclaims": "KubernetesClusterClaim",
        }.get(plural)

    def admission_decision(self, admission):
        phase = admission.get("phase") or "Pending"
        if phase == "Admitted":
            return "Admitted"
        if phase == "Rejected":
            return "Rejected"
        return "Pending"

    def admission_journal_name(self, plural, namespace, name, claim, admission):
        prefix = {
            "virtualmachineclaims": "vmc",
            "kubernetesclusterclaims": "kcc",
        }.get(plural, "claim")
        metadata = claim.get("metadata", {})
        generation = int(metadata.get("generation", 1) or 1)
        claim_uid = metadata.get("uid", "")
        uid_suffix = hashlib.sha1(claim_uid.encode("utf-8")).hexdigest()[:8] if claim_uid else "nouid"
        decision = self.admission_decision(admission).lower()
        reason = admission.get("reason") or "unknown"
        return dns_label_name(f"adm-{prefix}-{namespace}-{name}-{uid_suffix}-g{generation}-{decision}-{reason}")

    def record_admission_journal(self, plural, namespace, name, claim, admission):
        kind = self.admission_claim_kind(plural)
        if not kind:
            return
        admission = copy.deepcopy(admission or {})
        decision = self.admission_decision(admission)
        metadata = claim.get("metadata", {})
        spec = claim.get("spec", {})
        generation = int(metadata.get("generation", 1) or 1)
        project_ref = spec.get("projectRef") or namespace
        journal_name = self.admission_journal_name(plural, namespace, name, claim, admission)
        resources = copy.deepcopy(admission.get("estimatedResources") or {})
        locks = {}
        if project_ref:
            locks["projectQuota"] = self.project_quota_admission_lock_name(project_ref)
        if admission.get("capacityCell"):
            locks["capacity"] = self.capacity_admission_lock_name(admission.get("capacityCell"))
        quota_snapshot = {}
        try:
            if project_ref:
                quota_snapshot = self.project_quota_usage(project_ref, (plural, namespace, name))
        except ApiException as exc:
            if exc.status != 404:
                raise
        body = {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "AdmissionJournal",
            "metadata": {
                "name": journal_name,
                "labels": {
                    "platform.privatecloud.local/managed-by": "provider-controller",
                    "platform.privatecloud.local/claim-namespace": namespace,
                    "platform.privatecloud.local/claim-name": name,
                    "platform.privatecloud.local/claim-uid": metadata.get("uid", ""),
                    "platform.privatecloud.local/project": project_ref,
                    "platform.privatecloud.local/decision": decision.lower(),
                    "platform.privatecloud.local/reason": dns_label_name(admission.get("reason") or "unknown"),
                },
            },
            "spec": {
                "claimRef": {
                    "apiGroup": GROUP,
                    "kind": kind,
                    "namespace": namespace,
                    "name": name,
                    "uid": metadata.get("uid", ""),
                    "generation": generation,
                },
                "projectRef": project_ref,
                "decision": decision,
                "reason": admission.get("reason") or "Unknown",
                "message": admission.get("message") or "",
                "capacityCell": admission.get("capacityCell") or "",
                "serviceClass": admission.get("serviceClass") or "",
                "resources": resources,
                "quotaSnapshot": quota_snapshot,
                "locks": locks,
                "controller": {
                    "identity": self.identity,
                    "shardIndex": self.shard_index,
                    "shardTotal": self.shard_total,
                    "ownsGlobal": self.owns_global_resources(),
                },
                "observedAt": utc_now(),
            },
        }
        try:
            self.custom.get_cluster_custom_object(GROUP, VERSION, "admissionjournals", journal_name)
            return
        except ApiException as exc:
            if exc.status != 404:
                raise
        try:
            self.custom.create_cluster_custom_object(GROUP, VERSION, "admissionjournals", body)
        except ApiException as exc:
            if exc.status == 404:
                print(
                    f"AdmissionJournal CRD not found while recording {plural}/{namespace}/{name}",
                    flush=True,
                )
                return
            if exc.status == 409:
                return
            raise

    def delete_namespaced_custom_if_exists(self, group, version, namespace, plural, name):
        try:
            self.custom.delete_namespaced_custom_object(group, version, namespace, plural, name)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def delete_service_if_exists(self, namespace, name):
        try:
            self.core.delete_namespaced_service(name, namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def delete_deployment_if_exists(self, namespace, name):
        try:
            self.apps.delete_namespaced_deployment(name, namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def delete_pdb_if_exists(self, namespace, name):
        try:
            self.policy.delete_namespaced_pod_disruption_budget(name, namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def delete_network_policy_if_exists(self, namespace, name):
        try:
            self.net.delete_namespaced_network_policy(name, namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise

    def cleanup_vm_claim(self, namespace, name):
        vm_name = f"claim-{name}"
        self.delete_namespaced_custom_if_exists("kubevirt.io", "v1", namespace, "virtualmachines", vm_name)
        self.delete_capacity_reservation("virtualmachineclaims", namespace, name)

    def cleanup_cluster_claim(self, namespace, name):
        cluster_name = f"claim-{name}"
        proxy_namespace = os.environ.get("TENANT_API_PROXY_NAMESPACE", "capk-system")
        proxy_name = dns_label_name(f"{namespace}-{cluster_name}-api")
        self.delete_deployment_if_exists(proxy_namespace, proxy_name)
        self.delete_pdb_if_exists(proxy_namespace, proxy_name)
        self.delete_service_if_exists(proxy_namespace, proxy_name)
        self.delete_service_if_exists(namespace, f"{cluster_name}-lb")
        self.delete_network_policy_if_exists(namespace, f"allow-capi-{cluster_name}")
        self.delete_namespaced_custom_if_exists(
            "cluster.x-k8s.io", "v1beta1", namespace, "machinedeployments", f"{cluster_name}-default"
        )
        self.delete_namespaced_custom_if_exists(
            "bootstrap.cluster.x-k8s.io", "v1beta1", namespace, "kubeadmconfigtemplates", f"{cluster_name}-default"
        )
        self.delete_namespaced_custom_if_exists(
            "infrastructure.cluster.x-k8s.io", "v1alpha1", namespace, "kubevirtmachinetemplates", f"{cluster_name}-default"
        )
        self.delete_namespaced_custom_if_exists(
            "controlplane.cluster.x-k8s.io",
            "v1beta1",
            namespace,
            "kubeadmcontrolplanes",
            f"{cluster_name}-control-plane",
        )
        self.delete_namespaced_custom_if_exists(
            "infrastructure.cluster.x-k8s.io",
            "v1alpha1",
            namespace,
            "kubevirtmachinetemplates",
            f"{cluster_name}-control-plane",
        )
        self.delete_namespaced_custom_if_exists(
            "infrastructure.cluster.x-k8s.io", "v1alpha1", namespace, "kubevirtclusters", cluster_name
        )
        self.delete_namespaced_custom_if_exists(
            "cluster.x-k8s.io", "v1beta1", namespace, "clusters", cluster_name
        )
        self.delete_capacity_reservation("kubernetesclusterclaims", namespace, name)

    def reconcile_capacity_reservations(self):
        try:
            reservations = self.custom.list_cluster_custom_object(GROUP, VERSION, "capacityreservations")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        for reservation in reservations.get("items", []):
            name = reservation["metadata"]["name"]
            claim_ref = reservation.get("spec", {}).get("claimRef", {})
            key = self.reservation_claim_key(claim_ref)
            if not key:
                self.custom.delete_cluster_custom_object(GROUP, VERSION, "capacityreservations", name)
                continue
            plural, namespace, claim_name = key
            if not self.owns_namespace(namespace):
                continue
            try:
                claim = self.custom.get_namespaced_custom_object(
                    GROUP, VERSION, namespace, plural, claim_name
                )
            except ApiException as exc:
                if exc.status == 404:
                    self.custom.delete_cluster_custom_object(GROUP, VERSION, "capacityreservations", name)
                    continue
                raise
            admission = claim.get("status", {}).get("admission", {})
            if admission.get("phase") != "Admitted":
                self.custom.delete_cluster_custom_object(GROUP, VERSION, "capacityreservations", name)
                continue
            self.ensure_capacity_reservation(plural, namespace, claim_name, claim, admission)

    def ensure_default_deny(self, namespace):
        body = client.V1NetworkPolicy(
            metadata=client.V1ObjectMeta(name="default-deny", namespace=namespace),
            spec=client.V1NetworkPolicySpec(
                pod_selector=client.V1LabelSelector(match_labels={}),
                policy_types=["Ingress", "Egress"],
            ),
        )
        ensure_namespaced(
            self.net.read_namespaced_network_policy,
            self.net.create_namespaced_network_policy,
            self.net.patch_namespaced_network_policy,
            "default-deny",
            namespace,
            body,
        )

    def node_matches_selector(self, node, selector):
        labels = node.metadata.labels or {}
        for key, value in selector.items():
            if labels.get(key) != value:
                return False
        return True

    def node_is_ready(self, node):
        for condition in node.status.conditions or []:
            if condition.type == "Ready":
                return condition.status == "True"
        return False

    def resolve_capacity_cell(self, placement, kind, fallback_service_class):
        placement = placement or {}
        requested_cell = placement.get("capacityCell")
        requested_class = placement.get("serviceClass") or fallback_service_class
        requested_domains = self.placement_failure_domain_constraints(placement)
        cells = self.custom.list_cluster_custom_object(GROUP, VERSION, "capacitycells").get("items", [])
        service_class_candidates = []
        candidates = []
        for cell in cells:
            if requested_cell and cell["metadata"]["name"] != requested_cell:
                continue
            service_class = self.find_service_class(cell, kind, requested_class)
            if not service_class:
                continue
            service_class_candidates.append((cell, service_class))
            if requested_domains and not self.capacity_cell_matches_failure_domains(cell, requested_domains):
                continue
            candidates.append((cell, service_class))
        if not candidates:
            if requested_domains and service_class_candidates:
                domain_summary = self.failure_domain_summary(requested_domains)
                message = (
                    f"no capacity cell provides {kind} service class {requested_class} "
                    f"with failure domains {domain_summary}"
                )
                if requested_cell:
                    message = (
                        f"capacity cell {requested_cell} does not match requested "
                        f"failure domains {domain_summary}"
                    )
                return None, None, self.rejected_admission(
                    "FailureDomainNotFound",
                    message,
                    requested_cell,
                    requested_class,
                )
            reason = "CapacityCellNotFound" if requested_cell else "ServiceClassNotFound"
            message = f"no Ready-capable capacity cell provides {kind} service class {requested_class}"
            if requested_cell:
                message = f"capacity cell {requested_cell} does not provide {kind} service class {requested_class}"
            return None, None, self.rejected_admission(reason, message, requested_cell, requested_class)

        ready_candidates = [
            (cell, service_class)
            for cell, service_class in candidates
            if cell.get("status", {}).get("phase") == "Ready"
        ]
        if not ready_candidates:
            cell, service_class = candidates[0]
            cell_name = cell["metadata"]["name"]
            phase = cell.get("status", {}).get("phase")
            return None, None, self.rejected_admission(
                "CapacityCellNotReady",
                f"capacity cell {cell_name} is {phase or 'Pending'}",
                cell_name,
                service_class.get("name"),
            )

        if requested_cell:
            cell, service_class = ready_candidates[0]
        else:
            cell, service_class = max(ready_candidates, key=self.capacity_cell_candidate_score)
        return cell, service_class, None

    def placement_failure_domain_constraints(self, placement):
        domains = placement.get("failureDomains") or {}
        if not isinstance(domains, dict):
            return {}
        return {
            key: str(domains[key])
            for key in FAILURE_DOMAIN_KEYS
            if domains.get(key) not in (None, "")
        }

    def capacity_cell_failure_domain(self, cell, key):
        spec = cell.get("spec", {})
        domains = spec.get("failureDomains") or {}
        value = domains.get(key)
        if value is None and key in ("region", "site"):
            value = spec.get(key)
        return str(value) if value is not None else None

    def capacity_cell_matches_failure_domains(self, cell, requested_domains):
        for key, expected in requested_domains.items():
            if self.capacity_cell_failure_domain(cell, key) != expected:
                return False
        return True

    def failure_domain_summary(self, domains):
        return ",".join(f"{key}={domains[key]}" for key in FAILURE_DOMAIN_KEYS if key in domains)

    def capacity_cell_candidate_score(self, candidate):
        cell, _ = candidate
        available = self.cell_available(cell)
        ready_nodes = int(cell.get("status", {}).get("readyNodeCount", 0) or 0)
        reserved_claims = int(cell.get("status", {}).get("reserved", {}).get("claims", 0) or 0)
        return (available["cpu"], available["memory"], ready_nodes, -reserved_claims, cell["metadata"]["name"])

    def find_service_class(self, cell, kind, requested_name):
        classes = cell.get("spec", {}).get("serviceClasses", [])
        default_match = None
        for service_class in classes:
            if service_class.get("kind") != kind:
                continue
            if service_class.get("name") == requested_name:
                return service_class
            if service_class.get("default"):
                default_match = service_class
        return default_match if not requested_name else None

    def rejected_admission(self, reason, message, capacity_cell=None, service_class=None):
        admission = {
            "phase": "Rejected",
            "reason": reason,
            "message": message,
        }
        if capacity_cell:
            admission["capacityCell"] = capacity_cell
        if service_class:
            admission["serviceClass"] = service_class
        return admission

    def base_admission(self, cell, service_class, reason="CapacityAccepted", message="request fits capacity cell policy"):
        return {
            "phase": "Admitted",
            "reason": reason,
            "message": message,
            "capacityCell": cell["metadata"]["name"],
            "serviceClass": service_class.get("name"),
        }

    def claim_project(self, spec, namespace):
        project_name = spec.get("projectRef")
        if not project_name:
            return None, self.rejected_admission(
                "ProjectRequired",
                "claim must reference a Project",
            )
        try:
            project = self.custom.get_cluster_custom_object(GROUP, VERSION, "projects", project_name)
        except ApiException as exc:
            if exc.status == 404:
                return None, self.rejected_admission(
                    "ProjectNotFound",
                    f"project {project_name} does not exist",
                )
            raise
        tenant_namespace = project.get("spec", {}).get("tenantId", project_name)
        if tenant_namespace != namespace:
            return None, self.rejected_admission(
                "ProjectNamespaceMismatch",
                f"project {project_name} is bound to namespace {tenant_namespace}, not {namespace}",
            )
        return project, None

    def project_quota_usage(self, project_name, exclude=None):
        usage = {"cpu": 0, "memory": 0, "vms": 0, "tenantClusters": 0}
        reservation_claim_keys = set()
        try:
            reservations = self.custom.list_cluster_custom_object(GROUP, VERSION, "capacityreservations")
            for reservation in reservations.get("items", []):
                if reservation.get("status", {}).get("phase") != "Active":
                    continue
                if self.reservation_is_stale(reservation):
                    continue
                spec = reservation.get("spec", {})
                key = self.reservation_claim_key(spec.get("claimRef", {}))
                if not key:
                    continue
                reservation_claim_keys.add(key)
                if exclude and key == exclude:
                    continue
                plural, namespace, claim_name = key
                try:
                    claim = self.custom.get_namespaced_custom_object(
                        GROUP, VERSION, namespace, plural, claim_name
                    )
                except ApiException as exc:
                    if exc.status == 404:
                        continue
                    raise
                if claim.get("spec", {}).get("projectRef") != project_name:
                    continue
                resources = spec.get("resources", {})
                usage["cpu"] += cpu_to_millicores(resources.get("cpu", "0"))
                usage["memory"] += memory_to_mib(resources.get("memory", "0"))
                if plural == "virtualmachineclaims":
                    usage["vms"] += 1
                elif plural == "kubernetesclusterclaims":
                    usage["tenantClusters"] += 1
        except ApiException as exc:
            if exc.status != 404:
                raise

        for plural, count_key in (
            ("virtualmachineclaims", "vms"),
            ("kubernetesclusterclaims", "tenantClusters"),
        ):
            claims = self.custom.list_cluster_custom_object(GROUP, VERSION, plural)
            for claim in claims.get("items", []):
                key = (
                    plural,
                    claim["metadata"].get("namespace", ""),
                    claim["metadata"]["name"],
                )
                if exclude and key == exclude:
                    continue
                if key in reservation_claim_keys:
                    continue
                if claim.get("spec", {}).get("projectRef") != project_name:
                    continue
                admission = claim.get("status", {}).get("admission", {})
                if admission.get("phase") != "Admitted" and not self.backing_claim_exists(plural, key[1], key[2]):
                    continue
                resources = admission.get("estimatedResources", {})
                usage["cpu"] += cpu_to_millicores(resources.get("cpu", "0"))
                usage["memory"] += memory_to_mib(resources.get("memory", "0"))
                usage[count_key] += 1
        return {
            "cpu": cpu_millicores_to_text(usage["cpu"]),
            "memory": memory_mib_to_text(usage["memory"]),
            "vms": usage["vms"],
            "tenantClusters": usage["tenantClusters"],
        }

    def project_quota_admission(self, project, exclude, requested_cpu, requested_memory, count_key):
        spec = project.get("spec", {})
        project_name = project["metadata"]["name"]
        quotas = spec.get("quotas", {})
        usage = self.project_quota_usage(project_name, exclude)
        quota_cpu = cpu_to_millicores(quotas.get("cpu", "0"))
        quota_memory = memory_to_mib(quotas.get("memory", "0"))
        quota_count = int(quotas.get(count_key, 0))
        used_cpu = cpu_to_millicores(usage.get("cpu", "0"))
        used_memory = memory_to_mib(usage.get("memory", "0"))
        used_count = int(usage.get(count_key, 0) or 0)
        if requested_cpu + used_cpu > quota_cpu:
            return self.rejected_admission(
                "ProjectQuotaExceeded",
                f"project {project_name} CPU quota would be exceeded",
            )
        if requested_memory + used_memory > quota_memory:
            return self.rejected_admission(
                "ProjectQuotaExceeded",
                f"project {project_name} memory quota would be exceeded",
            )
        if used_count + 1 > quota_count:
            return self.rejected_admission(
                "ProjectQuotaExceeded",
                f"project {project_name} {count_key} quota would be exceeded",
            )
        return None

    def current_claim_quota_footprint(self, key):
        footprint = {"cpu": 0, "memory": 0, "vms": 0, "tenantClusters": 0}
        if not key:
            return footprint
        plural, namespace, name = key
        for reservation in self.custom.list_cluster_custom_object(GROUP, VERSION, "capacityreservations").get("items", []):
            if reservation.get("status", {}).get("phase") != "Active" or self.reservation_is_stale(reservation):
                continue
            if self.reservation_claim_key(reservation.get("spec", {}).get("claimRef", {})) != key:
                continue
            resources = reservation.get("spec", {}).get("resources", {})
            footprint["cpu"] = cpu_to_millicores(resources.get("cpu", "0"))
            footprint["memory"] = memory_to_mib(resources.get("memory", "0"))
            footprint["vms" if plural == "virtualmachineclaims" else "tenantClusters"] = 1
            return footprint
        try:
            claim = self.custom.get_namespaced_custom_object(GROUP, VERSION, namespace, plural, name)
        except ApiException as exc:
            if exc.status == 404:
                return footprint
            raise
        if not self.backing_claim_exists(plural, namespace, name):
            admission = claim.get("status", {}).get("admission", {})
            if admission.get("phase") != "Admitted":
                return footprint
        resources = claim.get("status", {}).get("admission", {}).get("estimatedResources", {})
        footprint["cpu"] = cpu_to_millicores(resources.get("cpu", "0"))
        footprint["memory"] = memory_to_mib(resources.get("memory", "0"))
        footprint["vms" if plural == "virtualmachineclaims" else "tenantClusters"] = 1
        return footprint

    def backing_claim_exists(self, plural, namespace, name):
        if plural == "virtualmachineclaims":
            try:
                self.custom.get_namespaced_custom_object(
                    "kubevirt.io", "v1", namespace, "virtualmachines", f"claim-{name}"
                )
                return True
            except ApiException as exc:
                if exc.status == 404:
                    return False
                raise
        if plural == "kubernetesclusterclaims":
            try:
                self.custom.get_namespaced_custom_object(
                    "cluster.x-k8s.io", "v1beta1", namespace, "clusters", f"claim-{name}"
                )
                return True
            except ApiException as exc:
                if exc.status == 404:
                    return False
                raise
        return False

    def cell_allocatable(self, cell):
        allocatable = cell.get("status", {}).get("allocatable", {})
        return {
            "cpu": cpu_to_millicores(allocatable.get("cpu", "0")),
            "memory": memory_to_mib(allocatable.get("memory", "0")),
        }

    def cell_available(self, cell):
        available = cell.get("status", {}).get("available", {})
        if available:
            return {
                "cpu": cpu_to_millicores(available.get("cpu", "0")),
                "memory": memory_to_mib(available.get("memory", "0")),
            }
        allocatable = self.cell_allocatable(cell)
        reserved = cell.get("status", {}).get("reserved", {})
        return {
            "cpu": max(0, allocatable["cpu"] - cpu_to_millicores(reserved.get("cpu", "0"))),
            "memory": max(0, allocatable["memory"] - memory_to_mib(reserved.get("memory", "0"))),
        }

    def cell_cpu_overcommit(self, cell):
        try:
            return float(cell.get("spec", {}).get("limits", {}).get("overcommitCPU", "1.0"))
        except (TypeError, ValueError):
            return 1.0

    def admit_vm_claim(self, spec, namespace, name):
        project, project_rejection = self.claim_project(spec, namespace)
        if project_rejection:
            return False, project_rejection
        resolved_image, image_rejection = self.resolve_vm_image(project["metadata"]["name"], spec.get("image", {}))
        if image_rejection:
            return False, image_rejection
        service_class_name = spec.get("placement", {}).get("serviceClass") or f"{spec.get('class', 'tiny')}-vm"
        cell, service_class, rejection = self.resolve_capacity_cell(
            spec.get("placement", {}), "vm", service_class_name
        )
        if rejection:
            return False, rejection
        resources = spec.get("resources", {})
        requested_cpu = int(resources.get("cpu", 1)) * 1000
        requested_memory = memory_to_mib(resources.get("memory", "256Mi"))
        allocatable = self.cell_allocatable(cell)
        reserved = self.capacity_cell_reservations(
            cell["metadata"]["name"],
            ("virtualmachineclaims", namespace, name),
        )
        cpu_limit = int(allocatable["cpu"] * self.cell_cpu_overcommit(cell))
        if requested_cpu + reserved["cpu"] > cpu_limit or requested_memory + reserved["memory"] > allocatable["memory"]:
            return False, self.rejected_admission(
                "InsufficientCapacity",
                "requested VM resources exceed selected capacity cell available resources",
                cell["metadata"]["name"],
                service_class.get("name"),
            )
        quota_rejection = self.project_quota_admission(
            project,
            ("virtualmachineclaims", namespace, name),
            requested_cpu,
            requested_memory,
            "vms",
        )
        if quota_rejection:
            return False, quota_rejection
        admission = self.base_admission(cell, service_class)
        admission["image"] = {
            "name": spec.get("image", {}).get("name"),
            "resolvedRef": resolved_image,
        }
        admission["estimatedResources"] = {
            "cpu": cpu_millicores_to_text(requested_cpu),
            "memory": memory_mib_to_text(requested_memory),
        }
        return True, admission

    def resolve_vm_image(self, project_name, image_spec):
        image_name = image_spec.get("name")
        if not image_name:
            return None, self.rejected_admission(
                "ImageRequired",
                "VM claim must reference an image catalog entry",
            )
        if image_spec.get("source", "catalog") != "catalog":
            return None, self.rejected_admission(
                "ImageSourceNotAllowed",
                "VM claims must use provider image catalog entries",
            )
        try:
            image = self.custom.get_cluster_custom_object(GROUP, VERSION, "images", image_name)
        except ApiException as exc:
            if exc.status == 404:
                return None, self.rejected_admission(
                    "ImageNotFound",
                    f"image catalog entry {image_name} does not exist",
                )
            raise
        status = image.get("status", {})
        if status.get("phase") != "Ready":
            return None, self.rejected_admission(
                "ImageNotReady",
                f"image catalog entry {image_name} is not Ready",
            )
        spec = image.get("spec", {})
        visibility = spec.get("visibility", "private")
        allowed = spec.get("allowedProjects", []) or []
        if visibility not in ("public",) and project_name not in allowed:
            return None, self.rejected_admission(
                "ImageAccessDenied",
                f"project {project_name} cannot use image {image_name}",
            )
        source = spec.get("source", {})
        if source.get("type") != "registry" or not source.get("registryRef"):
            return None, self.rejected_admission(
                "ImageSourceUnsupported",
                f"image {image_name} does not expose a registry source for VM containerDisk",
            )
        return source["registryRef"], None

    def admit_cluster_claim(self, spec, namespace, name):
        project, project_rejection = self.claim_project(spec, namespace)
        if project_rejection:
            return False, project_rejection, {}
        service_class_name = (
            spec.get("placement", {}).get("serviceClass")
            or f"{spec.get('controlPlane', {}).get('class', 'tiny')}-tenant-kubernetes"
        )
        cell, service_class, rejection = self.resolve_capacity_cell(
            spec.get("placement", {}), "tenant-kubernetes", service_class_name
        )
        if rejection:
            return False, rejection, {}

        control_plane = spec.get("controlPlane", {})
        cp_replicas = int(control_plane.get("replicas", 1))
        class_min_cp = service_class.get("minControlPlaneReplicas")
        if class_min_cp is not None and cp_replicas < int(class_min_cp):
            return False, self.rejected_admission(
                "ControlPlaneReplicaClassMismatch",
                (
                    f"service class {service_class.get('name')} requires at least "
                    f"{class_min_cp} control-plane replicas"
                ),
                cell["metadata"]["name"],
                service_class.get("name"),
            ), {}
        class_max_cp = service_class.get("maxControlPlaneReplicas")
        if class_max_cp is not None and cp_replicas > int(class_max_cp):
            return False, self.rejected_admission(
                "ControlPlaneReplicaClassMismatch",
                (
                    f"service class {service_class.get('name')} allows at most "
                    f"{class_max_cp} control-plane replicas"
                ),
                cell["metadata"]["name"],
                service_class.get("name"),
            ), {}
        limits = cell.get("spec", {}).get("limits", {})
        max_cp = int(limits.get("maxControlPlaneReplicas", cp_replicas))
        if cp_replicas > max_cp:
            return False, self.rejected_admission(
                "ControlPlaneReplicaLimitExceeded",
                f"requested control-plane replicas {cp_replicas} exceed capacity cell limit {max_cp}",
                cell["metadata"]["name"],
                service_class.get("name"),
            ), {}

        max_workers = int(limits.get("maxTenantClusterWorkersPerPool", 0))
        max_lab_workers = int(os.environ.get("MAX_TENANT_CLUSTER_WORKERS_PER_POOL", str(max_workers)))
        max_workers = min(max_workers, max_lab_workers)
        class_max = service_class.get("maxReplicas")
        if class_max is not None:
            max_workers = min(max_workers, int(class_max))

        effective_workers = {}
        worker_status = []
        capped = False
        for worker in spec.get("workers", []):
            worker_name = worker.get("name", "default")
            requested = int(worker.get("replicas", 0))
            admitted = min(requested, max_workers)
            capped = capped or requested != admitted
            effective_workers[worker_name] = admitted
            worker_status.append({"name": worker_name, "requested": requested, "admitted": admitted})

        requested_cpu = cp_replicas * self.cluster_class(control_plane.get("class", "tiny")).get("cpu", 2) * 1000
        requested_memory = cp_replicas * memory_to_mib(
            self.cluster_class(control_plane.get("class", "tiny")).get("memory", "2Gi")
        )
        for worker in spec.get("workers", []):
            admitted = effective_workers.get(worker.get("name", "default"), 0)
            worker_class = self.cluster_class(worker.get("class", "tiny"))
            requested_cpu += admitted * worker_class.get("cpu", 2) * 1000
            requested_memory += admitted * memory_to_mib(worker_class.get("memory", "2Gi"))

        allocatable = self.cell_allocatable(cell)
        reserved = self.capacity_cell_reservations(
            cell["metadata"]["name"],
            ("kubernetesclusterclaims", namespace, name),
        )
        cpu_limit = int(allocatable["cpu"] * self.cell_cpu_overcommit(cell))
        if requested_cpu + reserved["cpu"] > cpu_limit or requested_memory + reserved["memory"] > allocatable["memory"]:
            return False, self.rejected_admission(
                "InsufficientCapacity",
                "effective tenant cluster footprint exceeds selected capacity cell available resources",
                cell["metadata"]["name"],
                service_class.get("name"),
            ), {}
        quota_rejection = self.project_quota_admission(
            project,
            ("kubernetesclusterclaims", namespace, name),
            requested_cpu,
            requested_memory,
            "tenantClusters",
        )
        if quota_rejection:
            return False, quota_rejection, {}

        reason = "WorkerReplicasCapped" if capped else "CapacityAccepted"
        message = (
            f"worker pools capped to {max_workers} replicas per pool in this capacity cell"
            if capped
            else "request fits capacity cell policy"
        )
        admission = self.base_admission(cell, service_class, reason, message)
        admission["effectiveControlPlaneReplicas"] = cp_replicas
        admission["effectiveWorkerReplicas"] = worker_status
        admission["estimatedResources"] = {
            "cpu": cpu_millicores_to_text(requested_cpu),
            "memory": memory_mib_to_text(requested_memory),
        }
        return True, admission, effective_workers

    def ensure_dns_egress(self, namespace):
        body = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {"name": "allow-dns", "namespace": namespace},
            "spec": {
                "podSelector": {},
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [
                            {
                                "namespaceSelector": {
                                    "matchLabels": {
                                        "kubernetes.io/metadata.name": "kube-system"
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "UDP", "port": 53},
                            {"protocol": "TCP", "port": 53},
                        ],
                    }
                ],
            },
        }
        try:
            self.custom.get_namespaced_custom_object(
                "networking.k8s.io", "v1", namespace, "networkpolicies", "allow-dns"
            )
            self.custom.patch_namespaced_custom_object(
                "networking.k8s.io",
                "v1",
                namespace,
                "networkpolicies",
                "allow-dns",
                body,
            )
        except ApiException as exc:
            if exc.status != 404:
                raise
            self.custom.create_namespaced_custom_object(
                "networking.k8s.io", "v1", namespace, "networkpolicies", body
            )

    def ensure_cdi_importer_egress(self, namespace):
        body = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": "allow-cdi-importer-egress",
                "namespace": namespace,
                "labels": {"platform.privatecloud.local/managed-by": "provider-controller"},
            },
            "spec": {
                "podSelector": {"matchLabels": {"cdi.kubevirt.io": "importer"}},
                "policyTypes": ["Egress"],
                "egress": [
                    {
                        "to": [{"ipBlock": {"cidr": "0.0.0.0/0"}}],
                        "ports": [
                            {"protocol": "TCP", "port": 443},
                            {"protocol": "TCP", "port": 80},
                        ],
                    }
                ],
            },
        }
        self.apply_namespaced_object(
            "networking.k8s.io",
            "v1",
            namespace,
            "networkpolicies",
            "allow-cdi-importer-egress",
            body,
        )

    def ensure_tenant_rbac(self, namespace, admins_group):
        role_body = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {"name": "tenant-admin", "namespace": namespace},
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": [
                        "pods",
                        "pods/log",
                        "pods/exec",
                        "services",
                        "configmaps",
                        "secrets",
                        "persistentvolumeclaims",
                        "events",
                    ],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
                {
                    "apiGroups": ["apps", "batch", "cdi.kubevirt.io"],
                    "resources": ["*"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
                {
                    "apiGroups": ["kubevirt.io"],
                    "resources": [
                        "virtualmachines",
                        "virtualmachineinstances",
                        "virtualmachineinstancepresets",
                        "virtualmachineinstancereplicasets",
                    ],
                    "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"],
                },
                {
                    "apiGroups": ["subresources.kubevirt.io"],
                    "resources": [
                        "virtualmachines/start",
                        "virtualmachines/stop",
                        "virtualmachines/restart",
                        "virtualmachineinstances/console",
                        "virtualmachineinstances/vnc",
                    ],
                    "verbs": ["get", "update"],
                },
            ],
        }
        binding_body = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {"name": "tenant-admins", "namespace": namespace},
            "subjects": [
                {
                    "kind": "Group",
                    "name": admins_group,
                    "apiGroup": "rbac.authorization.k8s.io",
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": "tenant-admin",
                "apiGroup": "rbac.authorization.k8s.io",
            },
        }
        self.apply_namespaced_object("rbac.authorization.k8s.io", "v1", namespace, "roles", "tenant-admin", role_body)
        self.apply_namespaced_object(
            "rbac.authorization.k8s.io",
            "v1",
            namespace,
            "rolebindings",
            "tenant-admins",
            binding_body,
        )

    def ensure_tenant_self_service_rbac(self, namespace, admins_group):
        binding_body = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "tenant-self-service",
                "namespace": namespace,
                "labels": {"platform.privatecloud.local/managed-by": "provider-controller"},
            },
            "subjects": [
                {
                    "kind": "Group",
                    "name": admins_group,
                    "apiGroup": "rbac.authorization.k8s.io",
                }
            ],
            "roleRef": {
                "kind": "ClusterRole",
                "name": "platform-tenant-self-service",
                "apiGroup": "rbac.authorization.k8s.io",
            },
        }
        self.apply_namespaced_object(
            "rbac.authorization.k8s.io",
            "v1",
            namespace,
            "rolebindings",
            "tenant-self-service",
            binding_body,
        )

    def reconcile_vm_claims(self):
        claims = self.custom.list_cluster_custom_object(GROUP, VERSION, "virtualmachineclaims")
        for claim in self.owned_namespaced_items(claims):
            ns = claim["metadata"]["namespace"]
            name = claim["metadata"]["name"]
            spec = claim.get("spec", {})
            vm_name = f"claim-{name}"
            if claim.get("metadata", {}).get("deletionTimestamp"):
                self.cleanup_vm_claim(ns, name)
                if FINALIZER in (claim.get("metadata", {}).get("finalizers") or []):
                    self.remove_finalizer("virtualmachineclaims", ns, name, claim)
                continue
            self.ensure_finalizer("virtualmachineclaims", ns, name, claim)
            admission = self.current_admitted_generation(claim) or self.legacy_admitted_generation(
                "virtualmachineclaims", ns, name, claim
            )
            if admission:
                self.record_admission_journal("virtualmachineclaims", ns, name, claim, admission)
                self.ensure_capacity_reservation("virtualmachineclaims", ns, name, claim, admission)
            else:
                project_lock, project_lock_rejection = self.claim_project_lock_target(spec, ns)
                if project_lock_rejection:
                    self.delete_capacity_reservation("virtualmachineclaims", ns, name)
                    self.record_admission_journal("virtualmachineclaims", ns, name, claim, project_lock_rejection)
                    self.custom.patch_namespaced_custom_object_status(
                        GROUP,
                        VERSION,
                        ns,
                        "virtualmachineclaims",
                        name,
                        {"status": {"phase": "Rejected", "admission": project_lock_rejection}},
                    )
                    continue
                project_lock_acquired = False
                if project_lock:
                    project_lock_acquired = self.acquire_project_quota_admission_lock(
                        project_lock, "virtualmachineclaims", ns, name
                    )
                    if not project_lock_acquired:
                        if self.should_publish_pending_lock(claim):
                            pending = self.pending_project_quota_lock_status(project_lock)
                            self.record_admission_journal("virtualmachineclaims", ns, name, claim, pending)
                            self.custom.patch_namespaced_custom_object_status(
                                GROUP,
                                VERSION,
                                ns,
                                "virtualmachineclaims",
                                name,
                                {
                                    "status": {
                                        "phase": "PendingAdmission",
                                        "admission": pending,
                                    }
                                },
                            )
                        continue
                try:
                    lock_cell, lock_service_class = self.vm_claim_lock_target(spec)
                    lock_acquired = False
                    if lock_cell:
                        lock_acquired = self.acquire_capacity_admission_lock(
                            lock_cell, "virtualmachineclaims", ns, name
                        )
                        if not lock_acquired:
                            if self.should_publish_pending_lock(claim):
                                pending = self.pending_admission_lock_status(lock_cell, lock_service_class)
                                self.record_admission_journal("virtualmachineclaims", ns, name, claim, pending)
                                self.custom.patch_namespaced_custom_object_status(
                                    GROUP,
                                    VERSION,
                                    ns,
                                    "virtualmachineclaims",
                                    name,
                                    {
                                        "status": {
                                            "phase": "PendingAdmission",
                                            "admission": pending,
                                        }
                                    },
                                )
                            continue
                    try:
                        admitted, admission = self.admit_vm_claim(spec, ns, name)
                        if not admitted:
                            self.delete_capacity_reservation("virtualmachineclaims", ns, name)
                            self.record_admission_journal("virtualmachineclaims", ns, name, claim, admission)
                            self.custom.patch_namespaced_custom_object_status(
                                GROUP,
                                VERSION,
                                ns,
                                "virtualmachineclaims",
                                name,
                                {"status": {"phase": "Rejected", "admission": admission}},
                            )
                            continue
                        admission = self.mark_admission_observed(admission, claim)
                        self.record_admission_journal("virtualmachineclaims", ns, name, claim, admission)
                        self.ensure_capacity_reservation("virtualmachineclaims", ns, name, claim, admission)
                    finally:
                        if lock_acquired:
                            self.release_capacity_admission_lock(lock_cell)
                finally:
                    if project_lock_acquired:
                        self.release_project_quota_admission_lock(project_lock)
            vm_body = self.render_vm(vm_name, ns, spec, claim, admission)
            self.apply_namespaced_object("kubevirt.io", "v1", ns, "virtualmachines", vm_name, vm_body)

            phase = "Provisioning"
            ip = None
            try:
                vmi = self.custom.get_namespaced_custom_object("kubevirt.io", "v1", ns, "virtualmachineinstances", vm_name)
                phase = vmi.get("status", {}).get("phase", phase)
                ip = vmi.get("status", {}).get("interfaces", [{}])[0].get("ipAddress")
                conditions = vmi.get("status", {}).get("conditions", [])
                if any(c.get("type") == "Ready" and c.get("status") == "True" for c in conditions):
                    phase = "Ready"
            except ApiException as exc:
                if exc.status != 404:
                    raise

            status = {"phase": phase, "vmName": vm_name, "admission": admission}
            if ip:
                status["ip"] = ip
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "virtualmachineclaims",
                name,
                {"status": status},
            )

    def reconcile_images(self):
        images = self.custom.list_cluster_custom_object(GROUP, VERSION, "images")
        for image in images.get("items", []):
            name = image["metadata"]["name"]
            spec = image.get("spec", {})
            source = spec.get("source", {})
            source_ref = source.get("registryRef") or source.get("url") or source.get("type", "unknown")
            phase = "Ready" if source_ref != "unknown" else "PendingSource"
            status = {
                "phase": phase,
                "conditions": [
                    {
                        "type": "CatalogEntryAccepted",
                        "status": "True" if phase == "Ready" else "False",
                        "reason": phase,
                        "message": f"image catalog source={source_ref}",
                        "lastTransitionTime": utc_now(),
                    }
                ],
            }
            if source.get("checksum"):
                status["digest"] = source["checksum"]
            self.custom.patch_cluster_custom_object_status(
                GROUP,
                VERSION,
                "images",
                name,
                {"status": status},
            )

    def product_plan_phase(self, plan):
        spec = plan.get("spec", {})
        lifecycle = spec.get("lifecycle", {})
        state = lifecycle.get("state", "Draft")
        now = datetime.now(timezone.utc)
        publish_at = parse_utc_datetime(lifecycle.get("publishAt"))
        retire_at = parse_utc_datetime(lifecycle.get("retireAt"))
        if state == "Retired" or (retire_at and retire_at <= now):
            return "Retired", False, "PlanRetired"
        if state != "Published":
            return "Draft", False, "PlanDraft"
        if publish_at and publish_at > now:
            return "Scheduled", False, "PublishWindowPending"
        return "Published", True, "PlanPublished"

    def reconcile_product_plans(self):
        try:
            plans = self.custom.list_cluster_custom_object(GROUP, VERSION, "productplans")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        for plan in plans.get("items", []):
            name = plan["metadata"]["name"]
            spec = plan.get("spec", {})
            service = spec.get("service", {})
            phase, published, reason = self.product_plan_phase(plan)
            message = (
                f"product plan {name} is published for {service.get('kind', 'unknown')}"
                if published
                else f"product plan {name} is not available for new subscriptions"
            )
            self.custom.patch_cluster_custom_object_status(
                GROUP,
                VERSION,
                "productplans",
                name,
                {
                    "status": {
                        "phase": phase,
                        "observedGeneration": plan.get("metadata", {}).get("generation", 0),
                        "published": published,
                        "serviceKind": service.get("kind", ""),
                        "serviceClass": service.get("serviceClass", ""),
                        "conditions": [
                            {
                                "type": "Published",
                                "status": "True" if published else "False",
                                "reason": reason,
                                "message": message,
                                "lastTransitionTime": utc_now(),
                            }
                        ],
                    }
                },
            )

    def order_subscription_name(self, order, spec):
        if spec.get("subscriptionRef"):
            return dns_label_name(spec["subscriptionRef"])
        return dns_label_name(f"sub-{order['metadata']['name']}")

    def order_condition(self, ready, reason, message):
        return {
            "type": "Ready",
            "status": "True" if ready else "False",
            "reason": reason,
            "message": message,
            "lastTransitionTime": utc_now(),
        }

    def patch_order_status(self, namespace, name, status):
        self.custom.patch_namespaced_custom_object_status(
            GROUP,
            VERSION,
            namespace,
            "orders",
            name,
            {"status": status},
        )

    def order_subscription_body(self, order, subscription_name):
        metadata = order["metadata"]
        spec = order.get("spec", {})
        project_ref = spec.get("projectRef", metadata.get("namespace", ""))
        plan_ref = spec.get("planRef", "")
        subscription_spec = {
            "projectRef": project_ref,
            "planRef": plan_ref,
            "displayName": spec.get("displayName") or f"Subscription for order {metadata['name']}",
            "state": "Active",
            "autoRenew": True,
            "requestedBy": spec.get("requestedBy") or "order-controller",
            "orderRef": metadata["name"],
            "parameters": copy.deepcopy(spec.get("parameters") or {}),
        }
        if spec.get("billingAccountRef"):
            subscription_spec["billingAccountRef"] = spec["billingAccountRef"]
        return {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "Subscription",
            "metadata": {
                "name": subscription_name,
                "namespace": metadata["namespace"],
                "labels": {
                    "platform.privatecloud.local/managed-by": "provider-controller",
                    "platform.privatecloud.local/order": metadata["name"],
                    "platform.privatecloud.local/project": project_ref,
                    "platform.privatecloud.local/product-plan": plan_ref,
                },
                "ownerReferences": [self.owner_ref("Order", order)],
            },
            "spec": subscription_spec,
        }

    def patch_subscription_spec(self, namespace, name, spec_patch):
        self.custom.patch_namespaced_custom_object(
            GROUP,
            VERSION,
            namespace,
            "subscriptions",
            name,
            {"spec": spec_patch},
        )

    def reconcile_orders(self):
        try:
            orders = self.custom.list_cluster_custom_object(GROUP, VERSION, "orders")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        for order in self.owned_namespaced_items(orders):
            metadata = order["metadata"]
            ns = metadata["namespace"]
            name = metadata["name"]
            spec = order.get("spec", {})
            existing_status = order.get("status", {})
            generation = metadata.get("generation", 0)
            if (
                existing_status.get("phase") in ("Succeeded", "Rejected", "Cancelled")
                and existing_status.get("observedGeneration") == generation
            ):
                continue
            project, project_rejection = self.claim_project(spec, ns)
            action = spec.get("action", "CreateSubscription")
            state = spec.get("state", "Submitted")
            plan_ref = spec.get("planRef", "")
            idempotency_key = spec.get("idempotencyKey", "")
            subscription_name = self.order_subscription_name(order, spec)
            status = {
                "phase": "Pending",
                "observedGeneration": metadata.get("generation", 0),
                "idempotencyKey": idempotency_key,
                "planRef": plan_ref,
                "subscriptionName": subscription_name,
                "targetKind": "Subscription",
                "targetName": subscription_name,
                "submittedAt": metadata.get("creationTimestamp") or utc_now(),
                "conditions": [],
            }

            def finish(phase, ready, reason, message, completed=False):
                status["phase"] = phase
                status["reason"] = reason
                status["message"] = message
                if completed:
                    status["completedAt"] = utc_now()
                status["conditions"] = [self.order_condition(ready, reason, message)]
                self.patch_order_status(ns, name, status)

            def schedule_gate():
                schedule = spec.get("schedule") or {}
                if not isinstance(schedule, dict):
                    finish("Rejected", False, "InvalidSchedule", "order schedule must be an object", True)
                    return True
                not_before_raw = schedule.get("notBefore")
                expires_at_raw = schedule.get("expiresAt")
                not_before = parse_utc_datetime(not_before_raw)
                expires_at = parse_utc_datetime(expires_at_raw)
                if not_before_raw and not not_before:
                    finish("Rejected", False, "InvalidSchedule", "order schedule.notBefore must be RFC3339 time", True)
                    return True
                if expires_at_raw and not expires_at:
                    finish("Rejected", False, "InvalidSchedule", "order schedule.expiresAt must be RFC3339 time", True)
                    return True
                if not_before:
                    status["notBefore"] = not_before.replace(microsecond=0).isoformat().replace("+00:00", "Z")
                if expires_at:
                    status["expiresAt"] = expires_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
                now = datetime.now(timezone.utc)
                if not_before and expires_at and expires_at <= not_before:
                    finish(
                        "Rejected",
                        False,
                        "OrderWindowInvalid",
                        "order schedule.expiresAt must be after schedule.notBefore",
                        True,
                    )
                    return True
                if expires_at and expires_at <= now:
                    finish(
                        "Rejected",
                        False,
                        "OrderWindowExpired",
                        f"order {name} expired before its scheduled execution window",
                        True,
                    )
                    return True
                if not_before and not_before > now:
                    finish(
                        "Scheduled",
                        False,
                        "OrderWindowPending",
                        f"order {name} is scheduled for {status['notBefore']}",
                    )
                    return True
                return False

            if project_rejection:
                finish(
                    "Rejected",
                    False,
                    project_rejection.get("reason", "ProjectRejected"),
                    project_rejection.get("message", "order project validation failed"),
                    True,
                )
                continue
            if state == "Cancelled":
                finish("Cancelled", False, "OrderCancelled", f"order {name} is cancelled", True)
                continue
            if state == "Rejected":
                finish("Rejected", False, "OrderRejected", f"order {name} is rejected", True)
                continue
            if action not in (
                "CreateSubscription",
                "ChangeSubscription",
                "CancelSubscription",
                "RenewSubscription",
                "SuspendSubscription",
                "ResumeSubscription",
            ):
                finish(
                    "Rejected",
                    False,
                    "UnsupportedAction",
                    f"order action {action} is not supported by the current controller",
                    True,
                )
                continue
            policy = spec.get("policy") or {}
            decision = policy.get("decision", "Allowed")
            if decision == "Blocked":
                finish(
                    "Rejected",
                    False,
                    "PolicyBlocked",
                    policy.get("reason") or "order policy decision blocked provisioning",
                    True,
                )
                continue
            if decision == "ManualReview":
                finish(
                    "WaitingApproval",
                    False,
                    "ManualReviewRequired",
                    policy.get("reason") or "order requires manual review before provisioning",
                )
                continue
            approval = spec.get("approval") or {}
            if approval.get("required") and state != "Approved":
                finish(
                    "WaitingApproval",
                    False,
                    "ApprovalRequired",
                    "order requires approval before provisioning",
                )
                continue

            def load_plan():
                try:
                    return self.custom.get_cluster_custom_object(GROUP, VERSION, "productplans", plan_ref)
                except ApiException as exc:
                    if exc.status != 404:
                        raise
                    return None

            plan = load_plan()
            if not plan:
                finish("Rejected", False, "ProductPlanNotFound", f"product plan {plan_ref} does not exist", True)
                continue
            plan_phase, published, reason = self.product_plan_phase(plan)
            status["planPhase"] = plan_phase

            if action == "CreateSubscription" and not published:
                finish("Rejected", False, reason, f"product plan {plan_ref} is {plan_phase}", True)
                continue

            if action != "CreateSubscription":
                try:
                    subscription = self.custom.get_namespaced_custom_object(
                        GROUP, VERSION, ns, "subscriptions", subscription_name
                    )
                except ApiException as exc:
                    if exc.status != 404:
                        raise
                    finish(
                        "Rejected",
                        False,
                        "SubscriptionNotFound",
                        f"subscription {subscription_name} does not exist",
                        True,
                    )
                    continue
                sub_spec = subscription.get("spec", {})
                sub_status = subscription.get("status", {})
                sub_phase = sub_status.get("phase", "Pending")
                if sub_spec.get("projectRef") != spec.get("projectRef"):
                    finish(
                        "Rejected",
                        False,
                        "SubscriptionProjectMismatch",
                        f"subscription {subscription_name} does not belong to project {spec.get('projectRef')}",
                        True,
                    )
                    continue
                if action in (
                    "CancelSubscription",
                    "RenewSubscription",
                    "SuspendSubscription",
                    "ResumeSubscription",
                ) and sub_spec.get("planRef") != plan_ref:
                    finish(
                        "Rejected",
                        False,
                        "SubscriptionPlanMismatch",
                        f"subscription {subscription_name} is on plan {sub_spec.get('planRef')} not {plan_ref}",
                        True,
                    )
                    continue

                if schedule_gate():
                    continue

                if action == "SuspendSubscription":
                    if sub_spec.get("state") == "Cancelled":
                        finish(
                            "Rejected",
                            False,
                            "SubscriptionCancelled",
                            f"subscription {subscription_name} is cancelled and cannot be suspended",
                            True,
                        )
                        continue
                    if sub_spec.get("state") != "Suspended":
                        self.patch_subscription_spec(ns, subscription_name, {"state": "Suspended"})
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionSuspended",
                            f"order {name} accepted suspension for subscription {subscription_name}",
                            True,
                        )
                        continue
                    if sub_phase == "Suspended":
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionSuspended",
                            f"order {name} suspended subscription {subscription_name}",
                            True,
                        )
                    else:
                        finish(
                            "Provisioning",
                            False,
                            "WaitingForSubscription",
                            f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                        )
                    continue

                if action == "ResumeSubscription":
                    if sub_spec.get("state") == "Cancelled":
                        finish(
                            "Rejected",
                            False,
                            "SubscriptionCancelled",
                            f"subscription {subscription_name} is cancelled and cannot be resumed in place",
                            True,
                        )
                        continue
                    if sub_spec.get("state") != "Active":
                        self.patch_subscription_spec(ns, subscription_name, {"state": "Active"})
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionResumed",
                            f"order {name} accepted resume for subscription {subscription_name}",
                            True,
                        )
                        continue
                    if sub_phase == "Active":
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionResumed",
                            f"order {name} resumed subscription {subscription_name}",
                            True,
                        )
                    else:
                        finish(
                            "Provisioning",
                            False,
                            "WaitingForSubscription",
                            f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                        )
                    continue

                if action == "CancelSubscription":
                    if sub_spec.get("state") != "Cancelled":
                        self.patch_subscription_spec(ns, subscription_name, {"state": "Cancelled"})
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionCancelled",
                            f"order {name} accepted cancellation for subscription {subscription_name}",
                            True,
                        )
                        continue
                    if sub_phase == "Cancelled":
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionCancelled",
                            f"order {name} cancelled subscription {subscription_name}",
                            True,
                        )
                    else:
                        finish(
                            "Provisioning",
                            False,
                            "WaitingForSubscription",
                            f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                        )
                    continue

                if action == "RenewSubscription":
                    if sub_spec.get("state") == "Cancelled":
                        finish(
                            "Rejected",
                            False,
                            "SubscriptionCancelled",
                            f"subscription {subscription_name} is cancelled and cannot be renewed in place",
                            True,
                        )
                        continue
                    desired_spec = {"state": "Active", "autoRenew": True}
                    if sub_spec.get("state") != "Active" or sub_spec.get("autoRenew") is not True:
                        self.patch_subscription_spec(ns, subscription_name, desired_spec)
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionRenewed",
                            f"order {name} accepted renewal for subscription {subscription_name}",
                            True,
                        )
                        continue
                    if sub_phase == "Active":
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionRenewed",
                            f"order {name} renewed subscription {subscription_name}",
                            True,
                        )
                    else:
                        finish(
                            "Provisioning",
                            False,
                            "WaitingForSubscription",
                            f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                        )
                    continue

                if action == "ChangeSubscription":
                    if not published:
                        finish("Rejected", False, reason, f"product plan {plan_ref} is {plan_phase}", True)
                        continue
                    if sub_spec.get("state") == "Cancelled":
                        finish(
                            "Rejected",
                            False,
                            "SubscriptionCancelled",
                            f"subscription {subscription_name} is cancelled and cannot change plan",
                            True,
                        )
                        continue
                    desired_spec = {"planRef": plan_ref, "state": "Active"}
                    if spec.get("billingAccountRef"):
                        desired_spec["billingAccountRef"] = spec["billingAccountRef"]
                    if spec.get("parameters") is not None:
                        desired_spec["parameters"] = copy.deepcopy(spec.get("parameters") or {})
                    if sub_spec.get("planRef") != plan_ref or sub_spec.get("state") != "Active":
                        self.patch_subscription_spec(ns, subscription_name, desired_spec)
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionChanged",
                            f"order {name} accepted plan change for subscription {subscription_name} to plan {plan_ref}",
                            True,
                        )
                        continue
                    if sub_phase == "Active" and sub_status.get("planRef") == plan_ref:
                        finish(
                            "Succeeded",
                            True,
                            "SubscriptionChanged",
                            f"order {name} changed subscription {subscription_name} to plan {plan_ref}",
                            True,
                        )
                    else:
                        finish(
                            "Provisioning",
                            False,
                            "WaitingForSubscription",
                            f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                        )
                    continue

            if schedule_gate():
                continue

            body = self.order_subscription_body(order, subscription_name)
            try:
                subscription = self.custom.get_namespaced_custom_object(
                    GROUP, VERSION, ns, "subscriptions", subscription_name
                )
                sub_spec = subscription.get("spec", {})
                if sub_spec.get("orderRef") not in (None, "", name):
                    finish(
                        "Rejected",
                        False,
                        "IdempotencyConflict",
                        f"subscription {subscription_name} is owned by another order",
                        True,
                    )
                    continue
                if sub_spec.get("projectRef") != spec.get("projectRef") or sub_spec.get("planRef") != plan_ref:
                    finish(
                        "Rejected",
                        False,
                        "IdempotencyConflict",
                        f"subscription {subscription_name} does not match order project or plan",
                        True,
                    )
                    continue
            except ApiException as exc:
                if exc.status != 404:
                    raise
                subscription = self.custom.create_namespaced_custom_object(
                    GROUP, VERSION, ns, "subscriptions", body
                )

            sub_status = subscription.get("status", {})
            sub_phase = sub_status.get("phase", "Pending")
            if sub_phase == "Active":
                finish(
                    "Succeeded",
                    True,
                    "SubscriptionActive",
                    f"order {name} provisioned subscription {subscription_name}",
                    True,
                )
            else:
                finish(
                    "Provisioning",
                    False,
                    "WaitingForSubscription",
                    f"order {name} is waiting for subscription {subscription_name} phase {sub_phase}",
                )

    def reconcile_subscriptions(self):
        try:
            subscriptions = self.custom.list_cluster_custom_object(GROUP, VERSION, "subscriptions")
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        for subscription in self.owned_namespaced_items(subscriptions):
            ns = subscription["metadata"]["namespace"]
            name = subscription["metadata"]["name"]
            spec = subscription.get("spec", {})
            project, project_rejection = self.claim_project(spec, ns)
            plan_ref = spec.get("planRef", "")
            state = spec.get("state", "Active")
            status = {
                "phase": "Pending",
                "observedGeneration": subscription.get("metadata", {}).get("generation", 0),
                "planRef": plan_ref,
                "conditions": [],
            }
            if project_rejection:
                status["phase"] = "Rejected"
                status["conditions"].append(
                    {
                        "type": "Ready",
                        "status": "False",
                        "reason": project_rejection.get("reason", "ProjectRejected"),
                        "message": project_rejection.get("message", "subscription project validation failed"),
                        "lastTransitionTime": utc_now(),
                    }
                )
            else:
                try:
                    plan = self.custom.get_cluster_custom_object(GROUP, VERSION, "productplans", plan_ref)
                except ApiException as exc:
                    if exc.status != 404:
                        raise
                    plan = None
                if not plan:
                    status["phase"] = "PlanUnavailable"
                    status["conditions"].append(
                        {
                            "type": "Ready",
                            "status": "False",
                            "reason": "ProductPlanNotFound",
                            "message": f"product plan {plan_ref} does not exist",
                            "lastTransitionTime": utc_now(),
                        }
                    )
                else:
                    plan_spec = plan.get("spec", {})
                    service = plan_spec.get("service", {})
                    plan_phase, published, reason = self.product_plan_phase(plan)
                    status.update(
                        {
                            "planGeneration": plan.get("metadata", {}).get("generation", 0),
                            "planPhase": plan_phase,
                            "serviceKind": service.get("kind", ""),
                            "serviceClass": service.get("serviceClass", ""),
                            "effectiveQuota": plan_spec.get("quotaProfile", {}),
                        }
                    )
                    if state == "Cancelled":
                        phase = "Cancelled"
                        ready = False
                        condition_reason = "SubscriptionCancelled"
                        message = f"subscription {name} is cancelled"
                    elif state == "Suspended":
                        phase = "Suspended"
                        ready = False
                        condition_reason = "SubscriptionSuspended"
                        message = f"subscription {name} is suspended"
                    elif not published:
                        phase = "PlanUnavailable"
                        ready = False
                        condition_reason = reason
                        message = f"product plan {plan_ref} is {plan_phase}"
                    else:
                        phase = "Active"
                        ready = True
                        condition_reason = "SubscriptionActive"
                        message = (
                            f"subscription {name} is active for project "
                            f"{project['metadata']['name']} on plan {plan_ref}"
                        )
                    status["phase"] = phase
                    status["conditions"].append(
                        {
                            "type": "Ready",
                            "status": "True" if ready else "False",
                            "reason": condition_reason,
                            "message": message,
                            "lastTransitionTime": utc_now(),
                        }
                    )
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "subscriptions",
                name,
                {"status": status},
            )

    def reconcile_volumes(self):
        volumes = self.custom.list_cluster_custom_object(GROUP, VERSION, "volumes")
        for volume in self.owned_namespaced_items(volumes):
            ns = volume["metadata"]["namespace"]
            name = volume["metadata"]["name"]
            spec = volume.get("spec", {})
            pvc_name = f"claim-{name}"
            storage_class = self.volume_storage_class(spec.get("class", "standard"))
            access_mode = spec.get("accessMode", "ReadWriteOnce")
            size = spec.get("size", "1Gi")
            owner = self.owner_ref("Volume", volume)

            pvc = client.V1PersistentVolumeClaim(
                metadata=client.V1ObjectMeta(
                    name=pvc_name,
                    namespace=ns,
                    labels={
                        "platform.privatecloud.local/managed-by": "provider-controller",
                        "platform.privatecloud.local/claim": name,
                        "platform.privatecloud.local/project": spec.get("projectRef", ""),
                    },
                    owner_references=[owner],
                ),
                spec=client.V1PersistentVolumeClaimSpec(
                    access_modes=[access_mode],
                    storage_class_name=storage_class,
                    resources=client.V1VolumeResourceRequirements(
                        requests={"storage": size}
                    ),
                ),
            )
            ensure_namespaced(
                self.core.read_namespaced_persistent_volume_claim,
                self.core.create_namespaced_persistent_volume_claim,
                self.core.patch_namespaced_persistent_volume_claim,
                pvc_name,
                ns,
                pvc,
            )
            phase = "Provisioning"
            capacity = None
            try:
                current = self.core.read_namespaced_persistent_volume_claim(pvc_name, ns)
                phase = current.status.phase or phase
                capacity = (current.status.capacity or {}).get("storage")
            except ApiException as exc:
                if exc.status != 404:
                    raise
            status = {
                "phase": phase,
                "pvcName": pvc_name,
                "storageClass": storage_class,
            }
            if capacity:
                status["capacity"] = capacity
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "volumes",
                name,
                {"status": status},
            )

    def reconcile_networks(self):
        networks = self.custom.list_cluster_custom_object(GROUP, VERSION, "networks")
        for network in self.owned_namespaced_items(networks):
            ns = network["metadata"]["namespace"]
            name = network["metadata"]["name"]
            spec = network.get("spec", {})
            policy_name = f"network-{name}-isolation"
            pod_selector = client.V1LabelSelector(
                match_labels={"platform.privatecloud.local/network": name}
            )
            ingress = []
            egress = []
            if spec.get("egress", {}).get("allowInternet", False):
                egress.append(
                    client.V1NetworkPolicyEgressRule(
                        to=[client.V1NetworkPolicyPeer(ip_block=client.V1IPBlock(cidr="0.0.0.0/0"))]
                    )
                )
            body = client.V1NetworkPolicy(
                metadata=client.V1ObjectMeta(
                    name=policy_name,
                    namespace=ns,
                    labels={
                        "platform.privatecloud.local/managed-by": "provider-controller",
                        "platform.privatecloud.local/network": name,
                    },
                    owner_references=[self.owner_ref("Network", network)],
                ),
                spec=client.V1NetworkPolicySpec(
                    pod_selector=pod_selector,
                    policy_types=["Ingress", "Egress"],
                    ingress=ingress,
                    egress=egress,
                ),
            )
            ensure_namespaced(
                self.net.read_namespaced_network_policy,
                self.net.create_namespaced_network_policy,
                self.net.patch_namespaced_network_policy,
                policy_name,
                ns,
                body,
            )
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "networks",
                name,
                {
                    "status": {
                        "phase": "Ready",
                        "networkId": policy_name,
                        "allocatedCIDR": spec.get("cidr", ""),
                        "conditions": [
                            {
                                "type": "IsolationPolicyReady",
                                "status": "True",
                                "reason": "NetworkPolicyCreated",
                                "message": f"network isolation policy {policy_name} reconciled",
                            }
                        ],
                    }
                },
            )

    def reconcile_firewall_rules(self):
        rules = self.custom.list_cluster_custom_object(GROUP, VERSION, "firewallrules")
        for rule in self.owned_namespaced_items(rules):
            ns = rule["metadata"]["namespace"]
            name = rule["metadata"]["name"]
            spec = rule.get("spec", {})
            policy_name = f"firewall-{name}"
            action = spec.get("action", "Allow")
            direction = spec.get("direction", "Ingress")
            if action != "Allow":
                self.custom.patch_namespaced_custom_object_status(
                    GROUP,
                    VERSION,
                    ns,
                    "firewallrules",
                    name,
                    {
                        "status": {
                            "phase": "Unsupported",
                            "policyName": policy_name,
                            "observedGeneration": rule["metadata"].get("generation", 1),
                            "conditions": [
                                {
                                    "type": "PolicyReady",
                                    "status": "False",
                                    "reason": "DenyRequiresCiliumPolicy",
                                    "message": "Kubernetes NetworkPolicy supports allow rules only; deny rules require the production Cilium policy controller",
                                }
                            ],
                        }
                    },
                )
                continue

            ingress = []
            egress = []
            rendered_rules = [self.render_network_policy_rule(item, direction) for item in spec.get("rules", [])]
            if direction == "Ingress":
                ingress = rendered_rules
                policy_types = ["Ingress"]
            else:
                egress = rendered_rules
                policy_types = ["Egress"]
            body = {
                "apiVersion": "networking.k8s.io/v1",
                "kind": "NetworkPolicy",
                "metadata": {
                    "name": policy_name,
                    "namespace": ns,
                    "labels": {
                        "platform.privatecloud.local/managed-by": "provider-controller",
                        "platform.privatecloud.local/firewall-rule": name,
                    },
                    "ownerReferences": [self.owner_ref("FirewallRule", rule)],
                },
                "spec": {
                    "podSelector": {},
                    "policyTypes": policy_types,
                    "ingress": ingress,
                    "egress": egress,
                },
            }
            self.apply_namespaced_object(
                "networking.k8s.io",
                "v1",
                ns,
                "networkpolicies",
                policy_name,
                body,
            )
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "firewallrules",
                name,
                {
                    "status": {
                        "phase": "Ready",
                        "policyName": policy_name,
                        "observedGeneration": rule["metadata"].get("generation", 1),
                        "conditions": [
                            {
                                "type": "PolicyReady",
                                "status": "True",
                                "reason": "NetworkPolicyCreated",
                                "message": f"allow rule rendered as NetworkPolicy {policy_name}",
                            }
                        ],
                    }
                },
            )

    def reconcile_backup_plans(self):
        plans = self.custom.list_cluster_custom_object(GROUP, VERSION, "backupplans")
        for plan in self.owned_namespaced_items(plans):
            ns = plan["metadata"]["namespace"]
            name = plan["metadata"]["name"]
            spec = plan.get("spec", {})
            target = spec.get("target", {})
            target_kind = target.get("kind", "")
            retention = spec.get("retention", {})
            retention_limit = max(1, int(retention.get("daily", 1) or 1))
            if target_kind != "VirtualMachineClaim":
                self.custom.patch_namespaced_custom_object_status(
                    GROUP,
                    VERSION,
                    ns,
                    "backupplans",
                    name,
                    {
                        "status": {
                            "phase": "Accepted",
                            "recoveryPoints": 0,
                            "conditions": [
                                {
                                    "type": "BackendReady",
                                    "status": "False",
                                    "reason": "UnsupportedTarget",
                                    "message": f"lab backup backend currently supports VirtualMachineClaim targets, got {target_kind}",
                                }
                            ],
                        }
                    },
                )
                continue
            target_vms = self.resolve_backup_plan_vms(ns, target.get("selector", {}))
            if not target_vms:
                self.custom.patch_namespaced_custom_object_status(
                    GROUP,
                    VERSION,
                    ns,
                    "backupplans",
                    name,
                    {
                        "status": {
                            "phase": "Degraded",
                            "recoveryPoints": 0,
                            "conditions": [
                                {
                                    "type": "TargetResolved",
                                    "status": "False",
                                    "reason": "TargetNotFound",
                                    "message": "no Ready VirtualMachineClaim/backing VM matched the backup selector",
                                }
                            ],
                        }
                    },
                )
                continue
            snapshots = self.ensure_vm_snapshots_for_backup_plan(plan, target_vms, retention_limit)
            ready_snapshots = [
                snap for snap in snapshots
                if snap.get("status", {}).get("readyToUse") is True
            ]
            failed_snapshots = [
                snap for snap in snapshots
                if snap.get("status", {}).get("phase") in ("Failed", "Error")
            ]
            latest_ready = max(
                [snap.get("status", {}).get("creationTime", "") for snap in ready_snapshots],
                default="",
            )
            if ready_snapshots:
                phase = "Protected"
                reason = "SnapshotReady"
                message = f"{len(ready_snapshots)} KubeVirt VM snapshot recovery point(s) are ready"
                backend_ready = "True"
            elif failed_snapshots:
                phase = "Degraded"
                reason = "SnapshotFailed"
                message = "one or more KubeVirt VM snapshots failed"
                backend_ready = "False"
            else:
                phase = "Running"
                reason = "SnapshotPending"
                message = "KubeVirt VM snapshot recovery point is being created"
                backend_ready = "True"
            status_body = {
                "phase": phase,
                "lastRun": utc_now(),
                "recoveryPoints": len(ready_snapshots),
                "conditions": [
                    {
                        "type": "BackendReady",
                        "status": backend_ready,
                        "reason": "KubeVirtSnapshotBackend",
                        "message": "KubeVirt VirtualMachineSnapshot backend is active for VM claim backups in this lab",
                    },
                    {
                        "type": "LastRunReady",
                        "status": "True" if ready_snapshots else "False",
                        "reason": reason,
                        "message": message,
                    }
                ],
            }
            if latest_ready:
                status_body["lastSuccess"] = latest_ready
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "backupplans",
                name,
                {"status": status_body},
            )

    def labels_match(self, selector, labels):
        if not selector:
            return False
        return all(labels.get(key) == value for key, value in selector.items())

    def resolve_backup_plan_vms(self, namespace, selector):
        claims = self.custom.list_namespaced_custom_object(GROUP, VERSION, namespace, "virtualmachineclaims")
        result = []
        for claim in claims.get("items", []):
            status = claim.get("status", {})
            vm_name = status.get("vmName")
            if status.get("phase") != "Ready" or not vm_name:
                continue
            claim_labels = claim.get("metadata", {}).get("labels", {}) or {}
            implicit_labels = {"platform.privatecloud.local/claim": claim["metadata"]["name"]}
            try:
                vm = self.custom.get_namespaced_custom_object("kubevirt.io", "v1", namespace, "virtualmachines", vm_name)
            except ApiException as exc:
                if exc.status == 404:
                    continue
                raise
            vm_labels = vm.get("metadata", {}).get("labels", {}) or {}
            if (
                self.labels_match(selector, claim_labels)
                or self.labels_match(selector, implicit_labels)
                or self.labels_match(selector, vm_labels)
            ):
                result.append({"claim": claim, "vm": vm})
        return result

    def ensure_vm_snapshots_for_backup_plan(self, plan, targets, retention_limit):
        namespace = plan["metadata"]["namespace"]
        plan_name = plan["metadata"]["name"]
        snapshots = self.list_backup_snapshots(namespace, plan_name)
        for snap in snapshots:
            vm_name = self.backup_snapshot_source_vm(snap)
            if vm_name:
                self.ensure_backup_snapshot_labels(namespace, plan_name, snap, vm_name)
        existing_by_vm = {
            self.backup_snapshot_source_vm(snap): snap
            for snap in snapshots
        }
        for target in targets:
            vm_name = target["vm"]["metadata"]["name"]
            if vm_name in existing_by_vm:
                continue
            snapshot_name = dns_label_name(f"bkp-{plan_name}-{vm_name}", 63)
            body = {
                "apiVersion": "snapshot.kubevirt.io/v1beta1",
                "kind": "VirtualMachineSnapshot",
                "metadata": {
                    "name": snapshot_name,
                    "namespace": namespace,
                    "labels": {
                        "platform.privatecloud.local/managed-by": "provider-controller",
                        "platform.privatecloud.local/backupplan": plan_name,
                        "platform.privatecloud.local/source-vm": vm_name,
                    },
                    "ownerReferences": [self.owner_ref("BackupPlan", plan)],
                },
                "spec": {
                    "source": {
                        "apiGroup": "kubevirt.io",
                        "kind": "VirtualMachine",
                        "name": vm_name,
                    },
                    "deletionPolicy": "Delete",
                    "failureDeadline": "5m",
                },
            }
            try:
                self.custom.create_namespaced_custom_object(
                    "snapshot.kubevirt.io",
                    "v1beta1",
                    namespace,
                    "virtualmachinesnapshots",
                    body,
                )
            except ApiException as exc:
                if exc.status != 409:
                    raise
        snapshots = self.list_backup_snapshots(namespace, plan_name)
        snapshots.sort(
            key=lambda snap: snap.get("status", {}).get("creationTime")
            or snap.get("metadata", {}).get("creationTimestamp", ""),
            reverse=True,
        )
        for old in snapshots[retention_limit:]:
            self.custom.delete_namespaced_custom_object(
                "snapshot.kubevirt.io",
                "v1beta1",
                namespace,
                "virtualmachinesnapshots",
                old["metadata"]["name"],
            )
        return self.list_backup_snapshots(namespace, plan_name)

    def list_backup_snapshots(self, namespace, plan_name):
        snapshots = self.custom.list_namespaced_custom_object(
            "snapshot.kubevirt.io",
            "v1beta1",
            namespace,
            "virtualmachinesnapshots",
        )
        return [
            snap for snap in snapshots.get("items", [])
            if (
                snap.get("metadata", {}).get("labels", {}).get("platform.privatecloud.local/backupplan") == plan_name
                or self.backup_snapshot_owned_by_plan(snap, plan_name)
            )
        ]

    def backup_snapshot_owned_by_plan(self, snapshot, plan_name):
        for owner in snapshot.get("metadata", {}).get("ownerReferences", []) or []:
            if owner.get("kind") == "BackupPlan" and owner.get("name") == plan_name:
                return True
        return False

    def backup_snapshot_source_vm(self, snapshot):
        labels = snapshot.get("metadata", {}).get("labels", {}) or {}
        return labels.get("platform.privatecloud.local/source-vm") or snapshot.get("spec", {}).get("source", {}).get("name")

    def ensure_backup_snapshot_labels(self, namespace, plan_name, snapshot, vm_name):
        labels = snapshot.get("metadata", {}).get("labels", {}) or {}
        desired = {
            "platform.privatecloud.local/managed-by": "provider-controller",
            "platform.privatecloud.local/backupplan": plan_name,
            "platform.privatecloud.local/source-vm": vm_name,
        }
        if all(labels.get(key) == value for key, value in desired.items()):
            return
        self.custom.patch_namespaced_custom_object(
            "snapshot.kubevirt.io",
            "v1beta1",
            namespace,
            "virtualmachinesnapshots",
            snapshot["metadata"]["name"],
            {"metadata": {"labels": desired}},
        )

    def reconcile_restore_requests(self):
        requests = self.custom.list_cluster_custom_object(GROUP, VERSION, "restorerequests")
        for request in self.owned_namespaced_items(requests):
            ns = request["metadata"]["namespace"]
            name = request["metadata"]["name"]
            spec = request.get("spec", {})
            source = spec.get("source", {})
            target = spec.get("target", {})
            target_kind = target.get("kind", "")
            target_mode = target.get("mode", "Copy")
            target_name = target.get("name", "")
            restore_name = dns_label_name(f"restore-{name}", 63)
            if target_kind != "VirtualMachineClaim" or target_mode != "Copy":
                self.patch_restore_request_status(
                    ns,
                    name,
                    request,
                    {
                        "phase": "Rejected",
                        "restoreName": restore_name,
                        "restoredVMName": target_name,
                        "conditions": [
                            {
                                "type": "Accepted",
                                "status": "False",
                                "reason": "UnsupportedTarget",
                                "message": "lab restore backend currently supports VirtualMachineClaim targets with mode Copy",
                            }
                        ],
                    },
                )
                continue
            if not target_name:
                self.patch_restore_request_status(
                    ns,
                    name,
                    request,
                    {
                        "phase": "Rejected",
                        "restoreName": restore_name,
                        "conditions": [
                            {
                                "type": "Accepted",
                                "status": "False",
                                "reason": "MissingTargetName",
                                "message": "target.name is required for copy restore",
                            }
                        ],
                    },
                )
                continue
            source_snapshot = self.resolve_restore_snapshot(ns, source)
            if not source_snapshot:
                self.patch_restore_request_status(
                    ns,
                    name,
                    request,
                    {
                        "phase": "Pending",
                        "restoreName": restore_name,
                        "restoredVMName": target_name,
                        "conditions": [
                            {
                                "type": "SourceReady",
                                "status": "False",
                                "reason": "RecoveryPointNotReady",
                                "message": "no ready KubeVirt VirtualMachineSnapshot recovery point matched the restore source",
                            }
                        ],
                    },
                )
                continue
            snapshot_name = source_snapshot["metadata"]["name"]
            if not self.restore_target_available(ns, target_name, name):
                self.patch_restore_request_status(
                    ns,
                    name,
                    request,
                    {
                        "phase": "Rejected",
                        "restoreName": restore_name,
                        "restoredVMName": target_name,
                        "sourceSnapshot": snapshot_name,
                        "conditions": [
                            {
                                "type": "Accepted",
                                "status": "False",
                                "reason": "TargetAlreadyExists",
                                "message": f"target VM {target_name} already exists and is not owned by restore request {name}",
                            }
                        ],
                    },
                )
                continue
            restore = self.ensure_vm_restore(request, snapshot_name, restore_name, target_name)
            restore_status = restore.get("status", {})
            if restore_status.get("complete") is True:
                phase = "Succeeded"
                condition_status = "True"
                reason = "RestoreComplete"
                message = f"KubeVirt restore {restore_name} completed"
            elif any(cond.get("type") == "Failure" and cond.get("status") == "True" for cond in restore_status.get("conditions", [])):
                phase = "Degraded"
                condition_status = "False"
                reason = "RestoreFailed"
                message = f"KubeVirt restore {restore_name} reported failure"
            else:
                phase = "Running"
                condition_status = "False"
                reason = "RestoreRunning"
                message = f"KubeVirt restore {restore_name} is running"
            self.ensure_restored_vm_labels(ns, target_name, name)
            status_body = {
                "phase": phase,
                "restoreName": restore_name,
                "restoredVMName": target_name,
                "sourceSnapshot": snapshot_name,
                "observedGeneration": request["metadata"].get("generation", 1),
                "conditions": [
                    {
                        "type": "RestoreComplete",
                        "status": condition_status,
                        "reason": reason,
                        "message": message,
                    }
                ],
            }
            if restore_status.get("restoreTime"):
                status_body["completedAt"] = restore_status.get("restoreTime")
            self.patch_restore_request_status(ns, name, request, status_body)

    def resolve_restore_snapshot(self, namespace, source):
        recovery_point = source.get("recoveryPointRef")
        if recovery_point:
            try:
                snapshot = self.custom.get_namespaced_custom_object(
                    "snapshot.kubevirt.io",
                    "v1beta1",
                    namespace,
                    "virtualmachinesnapshots",
                    recovery_point,
                )
            except ApiException as exc:
                if exc.status == 404:
                    return None
                raise
            return snapshot if snapshot.get("status", {}).get("readyToUse") is True else None
        plan_name = source.get("backupPlanRef")
        if not plan_name:
            return None
        snapshots = [
            snap for snap in self.list_backup_snapshots(namespace, plan_name)
            if snap.get("status", {}).get("readyToUse") is True
        ]
        snapshots.sort(
            key=lambda snap: snap.get("status", {}).get("creationTime")
            or snap.get("metadata", {}).get("creationTimestamp", ""),
            reverse=True,
        )
        return snapshots[0] if snapshots else None

    def restore_target_available(self, namespace, target_name, request_name):
        try:
            claim = self.custom.get_namespaced_custom_object(GROUP, VERSION, namespace, "virtualmachineclaims", target_name)
            if claim:
                return False
        except ApiException as exc:
            if exc.status != 404:
                raise
        try:
            vm = self.custom.get_namespaced_custom_object("kubevirt.io", "v1", namespace, "virtualmachines", target_name)
        except ApiException as exc:
            if exc.status == 404:
                return True
            raise
        labels = vm.get("metadata", {}).get("labels", {}) or {}
        return labels.get("platform.privatecloud.local/restore-request") == request_name

    def ensure_vm_restore(self, request, snapshot_name, restore_name, target_name):
        namespace = request["metadata"]["namespace"]
        labels = {
            "platform.privatecloud.local/managed-by": "provider-controller",
            "platform.privatecloud.local/restore-request": request["metadata"]["name"],
            "platform.privatecloud.local/source-snapshot": snapshot_name,
        }
        body = {
            "apiVersion": "snapshot.kubevirt.io/v1beta1",
            "kind": "VirtualMachineRestore",
            "metadata": {
                "name": restore_name,
                "namespace": namespace,
                "labels": labels,
                "ownerReferences": [self.owner_ref("RestoreRequest", request)],
            },
            "spec": {
                "virtualMachineSnapshotName": snapshot_name,
                "target": {
                    "apiGroup": "kubevirt.io",
                    "kind": "VirtualMachine",
                    "name": target_name,
                },
                "volumeRestorePolicy": "PrefixTargetName",
                "volumeOwnershipPolicy": "None",
                "patches": [
                    json.dumps({"op": "add", "path": "/metadata/labels/platform.privatecloud.local~1restore-request", "value": request["metadata"]["name"]}),
                    json.dumps({"op": "add", "path": "/metadata/labels/platform.privatecloud.local~1restored-from", "value": snapshot_name}),
                    json.dumps({"op": "add", "path": "/metadata/labels/platform.privatecloud.local~1claim", "value": target_name}),
                    json.dumps({"op": "add", "path": "/metadata/labels/platform.privatecloud.local~1managed-by", "value": "provider-restore"}),
                    json.dumps({"op": "add", "path": "/spec/template/metadata/labels/kubevirt.io~1domain", "value": target_name}),
                ],
            },
        }
        try:
            return self.custom.create_namespaced_custom_object(
                "snapshot.kubevirt.io",
                "v1beta1",
                namespace,
                "virtualmachinerestores",
                body,
            )
        except ApiException as exc:
            if exc.status != 409:
                raise
            return self.custom.get_namespaced_custom_object(
                "snapshot.kubevirt.io",
                "v1beta1",
                namespace,
                "virtualmachinerestores",
                restore_name,
            )

    def ensure_restored_vm_labels(self, namespace, target_name, request_name):
        try:
            self.custom.patch_namespaced_custom_object(
                "kubevirt.io",
                "v1",
                namespace,
                "virtualmachines",
                target_name,
                {
                    "metadata": {
                        "labels": {
                            "platform.privatecloud.local/managed-by": "provider-restore",
                            "platform.privatecloud.local/restore-request": request_name,
                        }
                    }
                },
            )
        except ApiException as exc:
            if exc.status != 404:
                raise

    def patch_restore_request_status(self, namespace, name, request, status):
        status.setdefault("observedGeneration", request["metadata"].get("generation", 1))
        self.custom.patch_namespaced_custom_object_status(
            GROUP,
            VERSION,
            namespace,
            "restorerequests",
            name,
            {"status": status},
        )

    def reconcile_access_grants(self):
        grants = self.custom.list_cluster_custom_object(GROUP, VERSION, "accessgrants")
        for grant in self.owned_namespaced_items(grants):
            ns = grant["metadata"]["namespace"]
            name = grant["metadata"]["name"]
            spec = grant.get("spec", {})
            role = spec.get("role", "viewer")
            subject = spec.get("subject", {})
            role_name = self.ensure_access_role(ns, role)
            binding_name = f"accessgrant-{name}"
            binding = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "RoleBinding",
                "metadata": {
                    "name": binding_name,
                    "namespace": ns,
                    "labels": {
                        "platform.privatecloud.local/managed-by": "provider-controller",
                        "platform.privatecloud.local/accessgrant": name,
                    },
                    "ownerReferences": [self.owner_ref("AccessGrant", grant)],
                },
                "subjects": [
                    {
                        "kind": subject.get("kind", "Group"),
                        "name": subject.get("name", ""),
                        "apiGroup": "rbac.authorization.k8s.io",
                    }
                ],
                "roleRef": {
                    "kind": "Role",
                    "name": role_name,
                    "apiGroup": "rbac.authorization.k8s.io",
                },
            }
            self.apply_namespaced_object(
                "rbac.authorization.k8s.io",
                "v1",
                ns,
                "rolebindings",
                binding_name,
                binding,
            )
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "accessgrants",
                name,
                {
                    "status": {
                        "phase": "Ready",
                        "observedGeneration": grant["metadata"].get("generation", 1),
                        "conditions": [
                            {
                                "type": "BindingReady",
                                "status": "True",
                                "reason": "RoleBindingCreated",
                                "message": f"access grant rendered as RoleBinding {binding_name}",
                            }
                        ],
                    }
                },
            )

    def render_vm(self, vm_name, namespace, spec, claim, admission=None):
        resources = spec.get("resources", {})
        availability = spec.get("availability", {})
        admission = admission or {}
        container_image = (
            admission.get("image", {}).get("resolvedRef")
            or "quay.io/kubevirt/cirros-container-disk-demo:latest"
        )
        owner = {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "VirtualMachineClaim",
            "name": claim["metadata"]["name"],
            "uid": claim["metadata"]["uid"],
            "controller": True,
            "blockOwnerDeletion": False,
        }
        return {
            "apiVersion": "kubevirt.io/v1",
            "kind": "VirtualMachine",
            "metadata": {
                "name": vm_name,
                "namespace": namespace,
                "labels": {
                    "platform.privatecloud.local/managed-by": "provider-controller",
                    "platform.privatecloud.local/claim": claim["metadata"]["name"],
                },
                "ownerReferences": [owner],
            },
            "spec": {
                "runStrategy": availability.get("runStrategy", "Always"),
                "template": {
                    "metadata": {"labels": {"kubevirt.io/domain": vm_name}},
                    "spec": {
                        "domain": {
                            "cpu": {"cores": int(resources.get("cpu", 1))},
                            "resources": {
                                "requests": {"memory": resources.get("memory", "256Mi")}
                            },
                            "devices": {
                                "disks": [
                                    {"name": "containerdisk", "disk": {"bus": "virtio"}},
                                    {"name": "cloudinitdisk", "disk": {"bus": "virtio"}},
                                ],
                                "interfaces": [{"name": "default", "masquerade": {}}],
                            },
                        },
                        "networks": [{"name": "default", "pod": {}}],
                        "volumes": [
                            {
                                "name": "containerdisk",
                                "containerDisk": {"image": container_image},
                            },
                            {
                                "name": "cloudinitdisk",
                                "cloudInitNoCloud": {
                                    "userData": "#cloud-config\npassword: demo\nchpasswd:\n  expire: false\n"
                                },
                            },
                        ],
                    },
                },
            },
        }

    def reconcile_cluster_claims(self):
        claims = self.custom.list_cluster_custom_object(GROUP, VERSION, "kubernetesclusterclaims")
        for claim in self.owned_namespaced_items(claims):
            ns = claim["metadata"]["namespace"]
            name = claim["metadata"]["name"]
            spec = claim.get("spec", {})
            cluster_name = f"claim-{name}"
            if claim.get("metadata", {}).get("deletionTimestamp"):
                self.cleanup_cluster_claim(ns, name)
                if FINALIZER in (claim.get("metadata", {}).get("finalizers") or []):
                    self.remove_finalizer("kubernetesclusterclaims", ns, name, claim)
                continue
            self.ensure_finalizer("kubernetesclusterclaims", ns, name, claim)
            admission = self.current_admitted_generation(claim) or self.legacy_admitted_generation(
                "kubernetesclusterclaims", ns, name, claim
            )
            if admission:
                effective_workers = self.effective_workers_from_admission(admission)
                self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, admission)
                self.ensure_capacity_reservation("kubernetesclusterclaims", ns, name, claim, admission)
            else:
                project_lock, project_lock_rejection = self.claim_project_lock_target(spec, ns)
                if project_lock_rejection:
                    self.delete_capacity_reservation("kubernetesclusterclaims", ns, name)
                    self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, project_lock_rejection)
                    self.custom.patch_namespaced_custom_object_status(
                        GROUP,
                        VERSION,
                        ns,
                        "kubernetesclusterclaims",
                        name,
                        {"status": {"phase": "Rejected", "admission": project_lock_rejection}},
                    )
                    continue
                project_lock_acquired = False
                if project_lock:
                    project_lock_acquired = self.acquire_project_quota_admission_lock(
                        project_lock, "kubernetesclusterclaims", ns, name
                    )
                    if not project_lock_acquired:
                        if self.should_publish_pending_lock(claim):
                            pending = self.pending_project_quota_lock_status(project_lock)
                            self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, pending)
                            self.custom.patch_namespaced_custom_object_status(
                                GROUP,
                                VERSION,
                                ns,
                                "kubernetesclusterclaims",
                                name,
                                {
                                    "status": {
                                        "phase": "PendingAdmission",
                                        "admission": pending,
                                    }
                                },
                            )
                        continue
                try:
                    lock_cell, lock_service_class = self.cluster_claim_lock_target(spec)
                    lock_acquired = False
                    if lock_cell:
                        lock_acquired = self.acquire_capacity_admission_lock(
                            lock_cell, "kubernetesclusterclaims", ns, name
                        )
                        if not lock_acquired:
                            if self.should_publish_pending_lock(claim):
                                pending = self.pending_admission_lock_status(lock_cell, lock_service_class)
                                self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, pending)
                                self.custom.patch_namespaced_custom_object_status(
                                    GROUP,
                                    VERSION,
                                    ns,
                                    "kubernetesclusterclaims",
                                    name,
                                    {
                                        "status": {
                                            "phase": "PendingAdmission",
                                            "admission": pending,
                                        }
                                    },
                                )
                            continue
                    try:
                        admitted, admission, effective_workers = self.admit_cluster_claim(spec, ns, name)
                        if not admitted:
                            self.delete_capacity_reservation("kubernetesclusterclaims", ns, name)
                            self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, admission)
                            self.custom.patch_namespaced_custom_object_status(
                                GROUP,
                                VERSION,
                                ns,
                                "kubernetesclusterclaims",
                                name,
                                {"status": {"phase": "Rejected", "admission": admission}},
                            )
                            continue
                        admission = self.mark_admission_observed(admission, claim)
                        self.record_admission_journal("kubernetesclusterclaims", ns, name, claim, admission)
                        self.ensure_capacity_reservation("kubernetesclusterclaims", ns, name, claim, admission)
                    finally:
                        if lock_acquired:
                            self.release_capacity_admission_lock(lock_cell)
                finally:
                    if project_lock_acquired:
                        self.release_project_quota_admission_lock(project_lock)
            try:
                self.ensure_tenant_cluster_access(ns, cluster_name)
                for group, version, plural, object_name, body in self.render_tenant_cluster(
                    cluster_name, ns, claim, effective_workers
                ):
                    self.apply_namespaced_object(group, version, ns, plural, object_name, body)
                self.ensure_tenant_cluster_internal_service(ns, f"{cluster_name}-lb")
                proxy_namespace, proxy_name = self.ensure_tenant_cluster_api_proxy(ns, cluster_name)

                phase = "Provisioning"
                api_endpoint = None
                capi_cluster = self.custom.get_namespaced_custom_object(
                    "cluster.x-k8s.io", "v1beta1", ns, "clusters", cluster_name
                )
                status = capi_cluster.get("status", {})
                if status.get("phase") in ("Failed", "Deleting"):
                    phase = status["phase"]
                service_endpoint = self.tenant_cluster_service_endpoint(proxy_namespace, proxy_name)
                endpoint = status.get("controlPlaneEndpoint", {})
                if service_endpoint:
                    api_endpoint = service_endpoint
                    self.ensure_capi_control_plane_endpoint(ns, cluster_name, service_endpoint)
                    self.ensure_capi_kubeconfig_endpoint(
                        ns, f"{cluster_name}-kubeconfig", service_endpoint
                    )
                elif endpoint.get("host"):
                    api_endpoint = f"{endpoint.get('host')}:{endpoint.get('port', 6443)}"
                if any(
                    condition.get("type") == "Ready" and condition.get("status") == "True"
                    for condition in status.get("conditions", [])
                ):
                    phase = "Ready"
                candidate_endpoint = api_endpoint
                api_reachable = self.kube_api_reachable(candidate_endpoint)
                previous_status = claim.get("status", {})
                previous_condition = next(
                    (
                        condition
                        for condition in previous_status.get("conditions", [])
                        if condition.get("type") == "EndpointReachable"
                    ),
                    {},
                )
                try:
                    previous_failure_count = int(previous_status.get("endpointFailureCount", 0) or 0)
                except (TypeError, ValueError):
                    previous_failure_count = 0
                failure_count = 0
                endpoint_grace = False
                if api_reachable:
                    effective_reachable = True
                elif candidate_endpoint:
                    failure_count = previous_failure_count + 1
                    had_recent_endpoint = (
                        previous_status.get("apiEndpoint") == candidate_endpoint
                        or previous_status.get("lastKnownApiEndpoint") == candidate_endpoint
                        or previous_condition.get("status") == "True"
                    )
                    endpoint_grace = (
                        had_recent_endpoint
                        and failure_count < self.tenant_api_readyz_failure_threshold
                    )
                    effective_reachable = endpoint_grace
                else:
                    effective_reachable = False
                if phase == "Ready" and not effective_reachable:
                    phase = "Degraded"
                    api_endpoint = None
                endpoint_status = "True" if effective_reachable else "False"
                if api_reachable:
                    endpoint_reason = "ReadyzOK"
                elif endpoint_grace:
                    endpoint_reason = "ReadyzTransientFailure"
                else:
                    endpoint_reason = "ReadyzFailed" if candidate_endpoint else "EndpointPending"
                transition_time = utc_now()
                if (
                    previous_condition.get("status") == endpoint_status
                    and previous_condition.get("reason") == endpoint_reason
                    and previous_condition.get("lastTransitionTime")
                ):
                    transition_time = previous_condition["lastTransitionTime"]
                endpoint_condition = {
                    "type": "EndpointReachable",
                    "status": endpoint_status,
                    "reason": endpoint_reason,
                    "message": (
                        f"tenant Kubernetes API /readyz succeeded through {candidate_endpoint}"
                        if api_reachable
                        else (
                            f"tenant Kubernetes API /readyz transient failure {failure_count}/{self.tenant_api_readyz_failure_threshold} through {candidate_endpoint}; keeping last known endpoint"
                            if endpoint_grace
                            else (
                            f"tenant Kubernetes API /readyz failed through {candidate_endpoint}"
                            if candidate_endpoint
                            else "tenant Kubernetes API endpoint is not allocated yet"
                            )
                        )
                    ),
                    "lastTransitionTime": transition_time,
                }

                claim_status = {
                    "phase": phase,
                    "kubeconfigSecret": f"{cluster_name}-kubeconfig",
                    "admission": admission,
                    "apiEndpoint": api_endpoint,
                    "endpointReachable": effective_reachable,
                    "endpointProbeReachable": api_reachable,
                    "endpointFailureCount": failure_count,
                    "conditions": [endpoint_condition],
                }
                if candidate_endpoint:
                    claim_status["lastKnownApiEndpoint"] = candidate_endpoint
            except ApiException as exc:
                if exc.status == 404:
                    claim_status = {
                        "phase": "PendingClusterAPI",
                        "admission": admission,
                        "apiEndpoint": None,
                        "endpointReachable": False,
                        "conditions": [
                            {
                                "type": "EndpointReachable",
                                "status": "False",
                                "reason": "ClusterAPIPending",
                                "message": "Cluster API backing Cluster is not created yet",
                                "lastTransitionTime": utc_now(),
                            }
                        ],
                    }
                else:
                    raise
            self.custom.patch_namespaced_custom_object_status(
                GROUP,
                VERSION,
                ns,
                "kubernetesclusterclaims",
                name,
                {"status": claim_status},
            )

    def ensure_tenant_cluster_access(self, namespace, cluster_name):
        api_client_cidrs = [
            cidr.strip()
            for cidr in os.environ.get("TENANT_API_ALLOWED_CLIENT_CIDRS", "172.28.10.0/24").split(",")
            if cidr.strip()
        ]
        ingress_rules = [
            {
                "from": [
                    {
                        "namespaceSelector": {
                            "matchExpressions": [
                                {
                                    "key": "kubernetes.io/metadata.name",
                                    "operator": "In",
                                    "values": [
                                                "capk-system",
                                                "capi-system",
                                                "capi-kubeadm-bootstrap-system",
                                                "capi-kubeadm-control-plane-system",
                                                "platform-system",
                                            ],
                                        }
                                    ]
                        }
                    }
                ],
                "ports": [
                    {"protocol": "TCP", "port": 22},
                    {"protocol": "TCP", "port": 6443},
                ],
            },
            {
                "from": [
                    {
                        "podSelector": {
                            "matchLabels": {
                                "cluster.x-k8s.io/cluster-name": cluster_name,
                            }
                        }
                    }
                ],
                "ports": [
                    {"protocol": "TCP", "port": 6443},
                ],
            },
        ]
        if api_client_cidrs:
            ingress_rules.append(
                {
                    "from": [{"ipBlock": {"cidr": cidr}} for cidr in api_client_cidrs],
                    "ports": [
                        {"protocol": "TCP", "port": 6443},
                    ],
                }
            )
        body = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"allow-capi-{cluster_name}",
                "namespace": namespace,
                "labels": {
                    "platform.privatecloud.local/managed-by": "provider-controller",
                    "platform.privatecloud.local/cluster": cluster_name,
                },
            },
            "spec": {
                "podSelector": {
                    "matchLabels": {
                        "cluster.x-k8s.io/cluster-name": cluster_name,
                    }
                },
                "policyTypes": ["Ingress", "Egress"],
                "ingress": ingress_rules,
                "egress": [
                    {
                        "to": [
                            {
                                "podSelector": {
                                    "matchLabels": {
                                        "cluster.x-k8s.io/cluster-name": cluster_name,
                                    }
                                }
                            }
                        ],
                        "ports": [
                            {"protocol": "TCP", "port": 6443},
                        ],
                    },
                    {
                        "to": [{"ipBlock": {"cidr": "0.0.0.0/0"}}],
                        "ports": [
                            {"protocol": "TCP", "port": 443},
                            {"protocol": "TCP", "port": 80},
                            {"protocol": "TCP", "port": 6443},
                        ],
                    }
                ],
            },
        }
        self.apply_namespaced_object(
            "networking.k8s.io",
            "v1",
            namespace,
            "networkpolicies",
            f"allow-capi-{cluster_name}",
            body,
        )

    def tcp_reachable(self, host, port, timeout=2.0):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def kube_api_reachable(self, endpoint, timeout=4.0):
        if not endpoint:
            return False
        host, _, port_text = endpoint.partition(":")
        try:
            port = int(port_text or "6443")
            raw_sock = socket.create_connection((host, port), timeout=timeout)
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with context.wrap_socket(raw_sock, server_hostname=host) as tls_sock:
                tls_sock.settimeout(timeout)
                request = f"GET /readyz HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
                tls_sock.sendall(request.encode("ascii"))
                chunks = []
                while True:
                    chunk = tls_sock.recv(1024)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    if sum(len(item) for item in chunks) >= 4096:
                        break
            response = b"".join(chunks)
            headers, _, body = response.partition(b"\r\n\r\n")
            status_line = headers.splitlines()[0] if headers else b""
            return status_line.startswith((b"HTTP/1.0 200", b"HTTP/1.1 200")) and b"ok" in body.lower()
        except OSError:
            return False
        except ssl.SSLError:
            return False

    def tenant_cluster_service_endpoint(self, namespace, service_name):
        try:
            service = self.core.read_namespaced_service(service_name, namespace)
        except ApiException as exc:
            if exc.status == 404:
                return None
            raise
        ingress = service.status.load_balancer.ingress if service.status and service.status.load_balancer else None
        if not ingress:
            return None
        first = ingress[0]
        host = first.ip or first.hostname
        if not host:
            return None
        port = 6443
        for item in service.spec.ports or []:
            if item.port:
                port = item.port
                break
        return f"{host}:{port}"

    def ready_node_names(self):
        nodes = self.core.list_node().items
        return sorted(node.metadata.name for node in nodes if self.node_is_ready(node))

    def tenant_cluster_vmi_nodes(self, tenant_namespace, cluster_name):
        try:
            vmis = self.custom.list_namespaced_custom_object(
                "kubevirt.io",
                "v1",
                tenant_namespace,
                "virtualmachineinstances",
                label_selector=f"cluster.x-k8s.io/cluster-name={cluster_name}",
            )
        except ApiException as exc:
            if exc.status == 404:
                return []
            raise
        nodes = []
        for vmi in vmis.get("items", []):
            node_name = vmi.get("status", {}).get("nodeName")
            if node_name:
                nodes.append(node_name)
        return sorted(set(nodes))

    def ensure_tenant_cluster_api_proxy(self, tenant_namespace, cluster_name):
        proxy_namespace = os.environ.get("TENANT_API_PROXY_NAMESPACE", "capk-system")
        proxy_name = dns_label_name(f"{tenant_namespace}-{cluster_name}-api")
        labels = {
            "app": "tenant-api-proxy",
            "platform.privatecloud.local/managed-by": "provider-controller",
            "platform.privatecloud.local/tenant-namespace": tenant_namespace,
            "platform.privatecloud.local/cluster": cluster_name,
        }
        target = f"{cluster_name}-lb.{tenant_namespace}.svc.cluster.local"
        configured_proxy_nodes = [
            node.strip()
            for node in os.environ.get("TENANT_API_PROXY_NODE_HOSTNAMES", "").split(",")
            if node.strip()
        ]
        ready_nodes = self.ready_node_names()
        tenant_vmi_nodes = self.tenant_cluster_vmi_nodes(tenant_namespace, cluster_name)
        proxy_node_pool = configured_proxy_nodes or ready_nodes
        proxy_node_names = [node for node in proxy_node_pool if node not in tenant_vmi_nodes]
        if not proxy_node_names:
            proxy_node_names = proxy_node_pool
        proxy_replicas = max(1, min(self.tenant_api_proxy_max_replicas, len(proxy_node_names) or 1))
        proxy_code = r"""
import socket
import sys
import threading

target_host = sys.argv[1]
target_port = int(sys.argv[2])


def close(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


def pipe(source, destination):
    try:
        while True:
            data = source.recv(65536)
            if not data:
                break
            destination.sendall(data)
    except OSError:
        pass
    finally:
        close(source)
        close(destination)


def handle(client):
    try:
        upstream = socket.create_connection((target_host, target_port), timeout=10)
    except OSError:
        close(client)
        return
    threading.Thread(target=pipe, args=(client, upstream), daemon=True).start()
    threading.Thread(target=pipe, args=(upstream, client), daemon=True).start()


listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind(("0.0.0.0", 6443))
listener.listen(128)
print(f"forwarding 0.0.0.0:6443 to {target_host}:{target_port}", flush=True)
while True:
    client, _ = listener.accept()
    threading.Thread(target=handle, args=(client,), daemon=True).start()
""".strip()
        pod_spec = {
            "topologySpreadConstraints": [
                {
                    "maxSkew": 1,
                    "topologyKey": "kubernetes.io/hostname",
                    "whenUnsatisfiable": "ScheduleAnyway",
                    "labelSelector": {"matchLabels": labels},
                }
            ],
            "containers": [
                {
                    "name": "tcp-proxy",
                    "image": os.environ.get("TENANT_API_PROXY_IMAGE", "python:3.12-slim"),
                    "command": ["python", "-u", "-c", proxy_code, target, "6443"],
                    "args": [],
                    "ports": [{"name": "https", "containerPort": 6443}],
                    "securityContext": {
                        "allowPrivilegeEscalation": False,
                        "capabilities": {"drop": ["ALL"]},
                    },
                    "resources": {
                        "requests": {"cpu": "10m", "memory": "32Mi"},
                        "limits": {"cpu": "100m", "memory": "128Mi"},
                    },
                }
            ],
        }
        if proxy_node_names:
            pod_spec["affinity"] = {
                "nodeAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": {
                        "nodeSelectorTerms": [
                            {
                                "matchExpressions": [
                                    {
                                        "key": "kubernetes.io/hostname",
                                        "operator": "In",
                                        "values": proxy_node_names,
                                    }
                                ]
                            }
                        ]
                    }
                },
                "podAntiAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": [
                        {
                            "labelSelector": {"matchLabels": labels},
                            "topologyKey": "kubernetes.io/hostname",
                        }
                    ]
                },
            }
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": proxy_name,
                "namespace": proxy_namespace,
                "labels": labels,
            },
            "spec": {
                "replicas": proxy_replicas,
                "selector": {"matchLabels": labels},
                "strategy": {
                    "type": "RollingUpdate",
                    "rollingUpdate": {"maxSurge": 0, "maxUnavailable": 1},
                },
                "template": {
                    "metadata": {"labels": labels},
                    "spec": pod_spec,
                },
            },
        }
        ensure_namespaced(
            self.apps.read_namespaced_deployment,
            self.apps.create_namespaced_deployment,
            self.apps.patch_namespaced_deployment,
            proxy_name,
            proxy_namespace,
            deployment,
        )
        pdb = {
            "apiVersion": "policy/v1",
            "kind": "PodDisruptionBudget",
            "metadata": {
                "name": proxy_name,
                "namespace": proxy_namespace,
                "labels": labels,
            },
            "spec": {
                "minAvailable": 1,
                "selector": {"matchLabels": labels},
            },
        }
        ensure_namespaced(
            self.policy.read_namespaced_pod_disruption_budget,
            self.policy.create_namespaced_pod_disruption_budget,
            self.policy.patch_namespaced_pod_disruption_budget,
            proxy_name,
            proxy_namespace,
            pdb,
        )
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": proxy_name,
                "namespace": proxy_namespace,
                "labels": {
                    **labels,
                    "platform.privatecloud.local/routed-endpoint": "tenant-kubernetes-api",
                }
            },
            "spec": {
                "type": "LoadBalancer",
                "externalTrafficPolicy": "Cluster",
                "selector": labels,
                "ports": [
                    {"name": "https", "port": 6443, "targetPort": "https", "protocol": "TCP"}
                ],
            },
        }
        ensure_namespaced(
            self.core.read_namespaced_service,
            self.core.create_namespaced_service,
            self.core.patch_namespaced_service,
            proxy_name,
            proxy_namespace,
            service,
        )
        return proxy_namespace, proxy_name

    def ensure_tenant_cluster_internal_service(self, namespace, service_name):
        try:
            service = self.core.read_namespaced_service(service_name, namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        if service.spec.type == "ClusterIP":
            return
        body = {
            "spec": {
                "type": "ClusterIP",
                "externalTrafficPolicy": None,
            }
        }
        self.core.patch_namespaced_service(service_name, namespace, body)

    def ensure_capi_control_plane_endpoint(self, namespace, cluster_name, api_endpoint):
        if not api_endpoint or ":" not in api_endpoint:
            return
        host, port_text = api_endpoint.rsplit(":", 1)
        try:
            port = int(port_text)
        except ValueError:
            port = 6443
        try:
            cluster = self.custom.get_namespaced_custom_object(
                "cluster.x-k8s.io", "v1beta1", namespace, "clusters", cluster_name
            )
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        current = cluster.get("spec", {}).get("controlPlaneEndpoint", {})
        if current.get("host") == host and int(current.get("port", 6443) or 6443) == port:
            return
        self.custom.patch_namespaced_custom_object(
            "cluster.x-k8s.io",
            "v1beta1",
            namespace,
            "clusters",
            cluster_name,
            {"spec": {"controlPlaneEndpoint": {"host": host, "port": port}}},
        )

    def ensure_capi_kubeconfig_endpoint(self, namespace, secret_name, api_endpoint):
        if not api_endpoint:
            return
        server = f"https://{api_endpoint}"
        try:
            secret = self.core.read_namespaced_secret(secret_name, namespace)
        except ApiException as exc:
            if exc.status == 404:
                return
            raise
        data = secret.data or {}
        encoded_value = data.get("value")
        if not encoded_value:
            return
        kubeconfig = base64.b64decode(encoded_value).decode("utf-8")
        lines = []
        changed = False
        inserted_insecure = False
        insecure_enabled = self.tenant_api_kubeconfig_insecure_skip_tls_verify
        for line in kubeconfig.splitlines():
            if insecure_enabled and line.strip().startswith("certificate-authority-data:"):
                changed = True
                continue
            if insecure_enabled and line.strip().startswith("insecure-skip-tls-verify:"):
                indent = line[: len(line) - len(line.lstrip())]
                replacement = f"{indent}insecure-skip-tls-verify: true"
                if line != replacement:
                    changed = True
                lines.append(replacement)
                inserted_insecure = True
                continue
            if line.strip().startswith("server: "):
                indent = line[: len(line) - len(line.lstrip())]
                if insecure_enabled and not inserted_insecure:
                    lines.append(f"{indent}insecure-skip-tls-verify: true")
                    inserted_insecure = True
                    changed = True
                replacement = f"{indent}server: {server}"
                if line != replacement:
                    changed = True
                lines.append(replacement)
                continue
            lines.append(line)
        if not changed:
            return
        new_kubeconfig = "\n".join(lines)
        if kubeconfig.endswith("\n"):
            new_kubeconfig += "\n"
        self.core.patch_namespaced_secret(
            secret_name,
            namespace,
            {"data": {"value": base64.b64encode(new_kubeconfig.encode("utf-8")).decode("ascii")}},
        )

    def render_tenant_cluster(self, cluster_name, namespace, claim, effective_workers=None):
        spec = claim.get("spec", {})
        effective_workers = effective_workers or {}
        network = spec.get("network", {})
        control_plane = spec.get("controlPlane", {})
        workers = spec.get("workers", [])
        version = spec.get("version", "v1.32.1")
        pod_cidr = network.get("podCIDR", "10.243.0.0/16")
        service_cidr = network.get("serviceCIDR", "10.95.0.0/16")
        cp_replicas = int(control_plane.get("replicas", 1))
        image = spec.get("image", {}).get(
            "name",
            os.environ.get("CAPK_NODE_IMAGE", "quay.io/capk/ubuntu-2404-container-disk:v1.32.1"),
        )
        cp_class = self.cluster_class(control_plane.get("class", "tiny"))
        kubeadm_init_timeouts = {
            "controlPlaneComponentHealthCheck": os.environ.get(
                "TENANT_KUBEADM_CONTROL_PLANE_HEALTH_CHECK_TIMEOUT", "10m0s"
            ),
            "kubeletHealthCheck": os.environ.get("TENANT_KUBEADM_KUBELET_HEALTH_CHECK_TIMEOUT", "6m0s"),
            "kubernetesAPICall": os.environ.get("TENANT_KUBEADM_API_CALL_TIMEOUT", "2m0s"),
        }
        kubeadm_join_timeouts = {
            "discovery": os.environ.get("TENANT_KUBEADM_DISCOVERY_TIMEOUT", "10m0s"),
            "tlsBootstrap": os.environ.get("TENANT_KUBEADM_TLS_BOOTSTRAP_TIMEOUT", "10m0s"),
            "kubernetesAPICall": os.environ.get("TENANT_KUBEADM_API_CALL_TIMEOUT", "2m0s"),
        }
        owner = {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": "KubernetesClusterClaim",
            "name": claim["metadata"]["name"],
            "uid": claim["metadata"]["uid"],
            "controller": True,
            "blockOwnerDeletion": False,
        }

        cluster = {
            "apiVersion": "cluster.x-k8s.io/v1beta1",
            "kind": "Cluster",
            "metadata": self.managed_metadata(cluster_name, namespace, owner),
            "spec": {
                "clusterNetwork": {
                    "pods": {"cidrBlocks": [pod_cidr]},
                    "services": {"cidrBlocks": [service_cidr]},
                },
                "infrastructureRef": {
                    "apiVersion": "infrastructure.cluster.x-k8s.io/v1alpha1",
                    "kind": "KubevirtCluster",
                    "name": cluster_name,
                    "namespace": namespace,
                },
                "controlPlaneRef": {
                    "apiVersion": "controlplane.cluster.x-k8s.io/v1beta1",
                    "kind": "KubeadmControlPlane",
                    "name": f"{cluster_name}-control-plane",
                    "namespace": namespace,
                },
            },
        }
        kubevirt_cluster = {
            "apiVersion": "infrastructure.cluster.x-k8s.io/v1alpha1",
            "kind": "KubevirtCluster",
            "metadata": self.managed_metadata(cluster_name, namespace),
            "spec": {"controlPlaneServiceTemplate": {"spec": {"type": "ClusterIP"}}},
        }
        cp_template = self.render_kubevirt_machine_template(
            f"{cluster_name}-control-plane", namespace, owner, image, cp_class
        )
        kcp = {
            "apiVersion": "controlplane.cluster.x-k8s.io/v1beta1",
            "kind": "KubeadmControlPlane",
            "metadata": self.managed_metadata(f"{cluster_name}-control-plane", namespace),
            "spec": {
                "replicas": cp_replicas,
                "version": version,
                "machineTemplate": {
                    "infrastructureRef": {
                        "apiVersion": "infrastructure.cluster.x-k8s.io/v1alpha1",
                        "kind": "KubevirtMachineTemplate",
                        "name": f"{cluster_name}-control-plane",
                        "namespace": namespace,
                    }
                },
                "kubeadmConfigSpec": {
                    "clusterConfiguration": {
                        "networking": {
                            "dnsDomain": f"{cluster_name}.{namespace}.local",
                            "podSubnet": pod_cidr,
                            "serviceSubnet": service_cidr,
                        }
                    },
                    "initConfiguration": {
                        "nodeRegistration": {"criSocket": "unix:///var/run/containerd/containerd.sock"},
                        "timeouts": kubeadm_init_timeouts,
                    },
                    "joinConfiguration": {
                        "nodeRegistration": {"criSocket": "unix:///var/run/containerd/containerd.sock"},
                        "timeouts": kubeadm_join_timeouts,
                    },
                },
            },
        }

        objects = [
            ("cluster.x-k8s.io", "v1beta1", "clusters", cluster_name, cluster),
            ("infrastructure.cluster.x-k8s.io", "v1alpha1", "kubevirtclusters", cluster_name, kubevirt_cluster),
            (
                "infrastructure.cluster.x-k8s.io",
                "v1alpha1",
                "kubevirtmachinetemplates",
                f"{cluster_name}-control-plane",
                cp_template,
            ),
            (
                "controlplane.cluster.x-k8s.io",
                "v1beta1",
                "kubeadmcontrolplanes",
                f"{cluster_name}-control-plane",
                kcp,
            ),
        ]

        for worker in workers:
            worker_name = worker.get("name", "default")
            md_name = f"{cluster_name}-{worker_name}"
            worker_class = self.cluster_class(worker.get("class", "tiny"))
            requested_replicas = int(worker.get("replicas", 0))
            max_lab_replicas = int(os.environ.get("MAX_TENANT_CLUSTER_WORKERS_PER_POOL", "0"))
            worker_replicas = min(effective_workers.get(worker_name, requested_replicas), max_lab_replicas)
            if requested_replicas != worker_replicas:
                print(
                    f"capping {namespace}/{cluster_name}/{worker_name} workers "
                    f"from {requested_replicas} to {worker_replicas}; "
                    "raise MAX_TENANT_CLUSTER_WORKERS_PER_POOL for larger cells",
                    flush=True,
                )
            objects.append(
                (
                    "infrastructure.cluster.x-k8s.io",
                    "v1alpha1",
                    "kubevirtmachinetemplates",
                    md_name,
                    self.render_kubevirt_machine_template(md_name, namespace, owner, image, worker_class),
                )
            )
            objects.append(
                (
                    "bootstrap.cluster.x-k8s.io",
                    "v1beta1",
                    "kubeadmconfigtemplates",
                    md_name,
                    {
                        "apiVersion": "bootstrap.cluster.x-k8s.io/v1beta1",
                        "kind": "KubeadmConfigTemplate",
                        "metadata": self.managed_metadata(md_name, namespace),
                        "spec": {
                            "template": {
                                "spec": {
                                    "joinConfiguration": {
                                        "nodeRegistration": {
                                            "criSocket": "unix:///var/run/containerd/containerd.sock"
                                        },
                                        "timeouts": kubeadm_join_timeouts,
                                    }
                                }
                            }
                        },
                    },
                )
            )
            objects.append(
                (
                    "cluster.x-k8s.io",
                    "v1beta1",
                    "machinedeployments",
                    md_name,
                    {
                        "apiVersion": "cluster.x-k8s.io/v1beta1",
                        "kind": "MachineDeployment",
                        "metadata": self.managed_metadata(md_name, namespace),
                        "spec": {
                            "clusterName": cluster_name,
                            "replicas": worker_replicas,
                            "selector": {"matchLabels": {}},
                            "template": {
                                "spec": {
                                    "clusterName": cluster_name,
                                    "version": version,
                                    "bootstrap": {
                                        "configRef": {
                                            "apiVersion": "bootstrap.cluster.x-k8s.io/v1beta1",
                                            "kind": "KubeadmConfigTemplate",
                                            "name": md_name,
                                            "namespace": namespace,
                                        }
                                    },
                                    "infrastructureRef": {
                                        "apiVersion": "infrastructure.cluster.x-k8s.io/v1alpha1",
                                        "kind": "KubevirtMachineTemplate",
                                        "name": md_name,
                                        "namespace": namespace,
                                    },
                                }
                            },
                        },
                    },
                )
            )
        return objects

    def cluster_class(self, class_name):
        classes = {
            "tiny": {"cpu": 2, "memory": "2Gi"},
            "small": {"cpu": 2, "memory": "4Gi"},
            "medium": {"cpu": 4, "memory": "8Gi"},
            "large": {"cpu": 8, "memory": "16Gi"},
        }
        return classes.get(class_name, classes["tiny"])

    def volume_storage_class(self, class_name):
        return {
            "standard": "longhorn",
            "replicated": "longhorn",
            "fast": "longhorn",
            "archive": "longhorn",
        }.get(class_name, "longhorn")

    def render_network_policy_rule(self, item, direction):
        ports = []
        protocol = item.get("protocol", "TCP")
        if protocol != "Any":
            for port in item.get("ports", []):
                ports.append({"protocol": protocol, "port": int(port)})
        peers = []
        for cidr in item.get("cidrs", []):
            peers.append({"ipBlock": {"cidr": cidr}})
        if item.get("peerSelector"):
            peers.append({"podSelector": {"matchLabels": item.get("peerSelector", {})}})
        if not peers:
            peers = [{"ipBlock": {"cidr": "0.0.0.0/0"}}]
        rule = {"ports": ports} if ports else {}
        if direction == "Ingress":
            rule["from"] = peers
        else:
            rule["to"] = peers
        return rule

    def ensure_access_role(self, namespace, role):
        role_name = f"platform-{role}"
        if role in ("admin", "break-glass"):
            return "tenant-admin"
        verbs = ["get", "list", "watch"]
        resources = ["pods", "services", "configmaps", "secrets", "persistentvolumeclaims", "events"]
        if role == "operator":
            verbs = ["get", "list", "watch", "create", "update", "patch", "delete"]
        body = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": role_name,
                "namespace": namespace,
                "labels": {"platform.privatecloud.local/managed-by": "provider-controller"},
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": resources,
                    "verbs": verbs,
                },
                {
                    "apiGroups": ["platform.privatecloud.local"],
                    "resources": [
                        "virtualmachineclaims",
                        "kubernetesclusterclaims",
                        "orders",
                        "volumes",
                        "networks",
                        "firewallrules",
                        "backupplans",
                        "restorerequests",
                        "accessgrants",
                    ],
                    "verbs": ["get", "list", "watch"],
                },
            ],
        }
        self.apply_namespaced_object("rbac.authorization.k8s.io", "v1", namespace, "roles", role_name, body)
        return role_name

    def owner_ref(self, kind, obj):
        return {
            "apiVersion": f"{GROUP}/{VERSION}",
            "kind": kind,
            "name": obj["metadata"]["name"],
            "uid": obj["metadata"]["uid"],
            "controller": True,
            "blockOwnerDeletion": False,
        }

    def managed_metadata(self, name, namespace, owner=None):
        metadata = {
            "name": name,
            "namespace": namespace,
            "labels": {
                "platform.privatecloud.local/managed-by": "provider-controller",
            },
        }
        if owner:
            metadata["labels"]["platform.privatecloud.local/claim"] = owner["name"]
            metadata["ownerReferences"] = [owner]
        return metadata

    def render_kubevirt_machine_template(self, name, namespace, owner, image, size):
        root_disk_name = "rootdisk"
        root_storage_class = os.environ.get("CAPK_NODE_ROOT_STORAGE_CLASS", "longhorn")
        root_disk_size = os.environ.get("CAPK_NODE_ROOT_DISK_SIZE", "12Gi")
        registry_url = image if image.startswith("docker://") else f"docker://{image}"
        return {
            "apiVersion": "infrastructure.cluster.x-k8s.io/v1alpha1",
            "kind": "KubevirtMachineTemplate",
            "metadata": self.managed_metadata(name, namespace),
            "spec": {
                "template": {
                    "spec": {
                        "virtualMachineBootstrapCheck": {"checkStrategy": "ssh"},
                        "virtualMachineTemplate": {
                            "metadata": {"namespace": namespace},
                            "spec": {
                                "runStrategy": "Always",
                                "dataVolumeTemplates": [
                                    {
                                        "metadata": {"name": root_disk_name},
                                        "spec": {
                                            "source": {
                                                "registry": {
                                                    "url": registry_url,
                                                    "pullMethod": "pod",
                                                }
                                            },
                                            "storage": {
                                                "storageClassName": root_storage_class,
                                                "accessModes": ["ReadWriteOnce"],
                                                "volumeMode": "Filesystem",
                                                "resources": {
                                                    "requests": {"storage": root_disk_size}
                                                },
                                            },
                                        },
                                    }
                                ],
                                "template": {
                                    "spec": {
                                        "domain": {
                                            "cpu": {"cores": size["cpu"]},
                                            "memory": {"guest": size["memory"]},
                                            "devices": {
                                                "networkInterfaceMultiqueue": True,
                                                "interfaces": [
                                                    {
                                                        "name": "default",
                                                        "masquerade": {},
                                                        "ports": [
                                                            {"name": "ssh", "port": 22},
                                                            {"name": "apiserver", "port": 6443},
                                                        ],
                                                    }
                                                ],
                                                "disks": [
                                                    {
                                                        "name": root_disk_name,
                                                        "bootOrder": 1,
                                                        "disk": {"bus": "virtio"},
                                                    }
                                                ],
                                            },
                                        },
                                        "evictionStrategy": "External",
                                        "networks": [{"name": "default", "pod": {}}],
                                        "volumes": [
                                            {
                                                "name": root_disk_name,
                                                "dataVolume": {"name": root_disk_name},
                                            }
                                        ],
                                    }
                                },
                            },
                        },
                    }
                }
            },
        }

    def apply_namespaced_object(self, group, version, namespace, plural, name, body):
        try:
            self.custom.get_namespaced_custom_object(group, version, namespace, plural, name)
            try:
                self.custom.patch_namespaced_custom_object(group, version, namespace, plural, name, body)
            except ApiException as exc:
                if (
                    plural == "kubevirtmachinetemplates"
                    and exc.status == 403
                    and "immutable" in getattr(exc, "body", "")
                ):
                    print(
                        f"leaving immutable {namespace}/{plural}/{name} unchanged; "
                        "new clusters will use the current template",
                        flush=True,
                    )
                    return
                raise
        except ApiException as exc:
            if exc.status != 404:
                raise
            self.custom.create_namespaced_custom_object(group, version, namespace, plural, body)

    def apply_cluster_object(self, group, version, plural, name, body):
        try:
            self.custom.get_cluster_custom_object(group, version, plural, name)
            self.custom.patch_cluster_custom_object(group, version, plural, name, body)
        except ApiException as exc:
            if exc.status != 404:
                raise
            self.custom.create_cluster_custom_object(group, version, plural, body)


class LeaderElector:
    def __init__(self, namespace, lease_name, identity, duration_seconds=45):
        self.api = client.CoordinationV1Api()
        self.namespace = namespace
        self.lease_name = lease_name
        self.identity = identity
        self.duration_seconds = duration_seconds

    def try_acquire_or_renew(self):
        now = datetime.now(timezone.utc)
        try:
            lease = self.api.read_namespaced_lease(self.lease_name, self.namespace)
        except ApiException as exc:
            if exc.status != 404:
                raise
            return self.create_lease(now)

        spec = lease.spec
        holder = getattr(spec, "holder_identity", None) if spec else None
        is_holder = holder == self.identity
        expired = self.lease_expired(spec, now)
        if not is_holder and not expired:
            return False

        transitions = (getattr(spec, "lease_transitions", None) if spec else None) or 0
        if not is_holder:
            transitions += 1
        acquire_time = getattr(spec, "acquire_time", None) if spec else None
        if not is_holder or not acquire_time:
            acquire_time = now

        body = {
            "metadata": {
                "name": self.lease_name,
                "namespace": self.namespace,
                "resourceVersion": lease.metadata.resource_version,
            },
            "spec": {
                "holderIdentity": self.identity,
                "leaseDurationSeconds": self.duration_seconds,
                "acquireTime": self.timestamp(acquire_time),
                "renewTime": self.timestamp(now),
                "leaseTransitions": transitions,
            },
        }
        try:
            self.api.patch_namespaced_lease(self.lease_name, self.namespace, body)
            return True
        except ApiException as exc:
            if exc.status == 409:
                return False
            raise

    def create_lease(self, now):
        body = {
            "apiVersion": "coordination.k8s.io/v1",
            "kind": "Lease",
            "metadata": {
                "name": self.lease_name,
                "namespace": self.namespace,
                "labels": {"app": "provider-controller"},
            },
            "spec": {
                "holderIdentity": self.identity,
                "leaseDurationSeconds": self.duration_seconds,
                "acquireTime": self.timestamp(now),
                "renewTime": self.timestamp(now),
                "leaseTransitions": 0,
            },
        }
        try:
            self.api.create_namespaced_lease(self.namespace, body)
            return True
        except ApiException as exc:
            if exc.status == 409:
                return False
            raise

    def lease_expired(self, spec, now):
        if not spec:
            return True
        renew_time = getattr(spec, "renew_time", None) or getattr(spec, "acquire_time", None)
        renew_time = self.as_datetime(renew_time)
        if not renew_time:
            return True
        return (now - renew_time).total_seconds() > self.duration_seconds

    def as_datetime(self, value):
        if not value:
            return None
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        text = str(value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def timestamp(self, value):
        if not isinstance(value, datetime):
            value = self.as_datetime(value) or datetime.now(timezone.utc)
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def main():
    load_config()
    controller = ProviderController()
    interval = int(os.environ.get("RECONCILE_INTERVAL_SECONDS", "20"))
    identity = controller.identity
    namespace = os.environ.get("POD_NAMESPACE", "platform-system")
    lease_name = os.environ.get("LEADER_ELECTION_LEASE_NAME", "provider-controller")
    if "LEADER_ELECTION_LEASE_NAME" not in os.environ and controller.shard_total > 1:
        lease_name = f"{lease_name}-shard-{controller.shard_index}"
    lease_duration = int(os.environ.get("LEADER_ELECTION_LEASE_DURATION_SECONDS", "45"))
    metrics_port = int(os.environ.get("METRICS_PORT", "8080"))
    METRICS.set_identity(identity)
    start_metrics_server(metrics_port)
    elector = LeaderElector(namespace, lease_name, identity, lease_duration)
    while True:
        try:
            is_leader = elector.try_acquire_or_renew()
            METRICS.set_leader(is_leader)
            if is_leader:
                started = time.time()
                try:
                    controller.run_once()
                    METRICS.record_reconcile("success", time.time() - started)
                except Exception as exc:
                    METRICS.record_reconcile("error", time.time() - started)
                    print(f"reconcile error: {exc}", flush=True)
            else:
                METRICS.record_reconcile("standby", 0.0)
        except Exception as exc:
            METRICS.set_leader(False)
            METRICS.record_reconcile("error", 0.0)
            print(f"leader election error: {exc}", flush=True)
        time.sleep(interval)


if __name__ == "__main__":
    main()
