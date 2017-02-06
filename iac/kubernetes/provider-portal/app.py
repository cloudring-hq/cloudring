#!/usr/bin/env python3
import base64
import ipaddress
import hashlib
import hmac
import json
import os
import re
import ssl
import copy
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


GROUP = "platform.privatecloud.local"
VERSION = "v1alpha1"
AUDIT_PLURAL = "selfserviceauditevents"
TOKEN_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/token"
CA_PATH = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
DNS_LABEL_RE = re.compile(r"^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$")
RESOURCE_RE = re.compile(r"^[0-9]+(Mi|Gi)$")
CPU_RESOURCE_RE = re.compile(r"^([0-9]+m|[0-9]+)$")
PROJECT_TIERS = {"shared", "dedicated-node-pool", "dedicated-cluster", "dedicated-cell"}
VM_CLASS_NAMES = {"tiny", "small", "medium", "large", "gpu", "custom"}
KCC_CONTROL_PLANE_CLASS_NAMES = {"tiny", "small", "medium", "large"}
KCC_WORKER_CLASS_NAMES = {"tiny", "small", "medium", "large", "gpu"}
RUN_STRATEGIES = {"Always", "Manual", "Halted"}
CONTROL_PLANE_REPLICAS = {1, 3, 5}
FAILURE_DOMAIN_KEYS = {"region", "site", "zone", "rack", "network", "storage"}
VOLUME_CLASSES = {"standard", "fast", "replicated", "archive"}
VOLUME_ACCESS_MODES = {"ReadWriteOnce", "ReadWriteMany", "ReadOnlyMany"}
VOLUME_SOURCES = {"empty", "image", "snapshot", "backup"}
VOLUME_RECLAIM_POLICIES = {"Delete", "Retain", "Snapshot"}
NETWORK_TYPES = {"isolated", "routed", "public", "provider"}
FIREWALL_DIRECTIONS = {"Ingress", "Egress"}
FIREWALL_ACTIONS = {"Allow", "Deny"}
FIREWALL_PROTOCOLS = {"TCP", "UDP", "ICMP", "Any"}
ACCESS_SUBJECT_KINDS = {"User", "Group", "ServiceAccount"}
ACCESS_PROVIDERS = {"oidc", "local", "external"}
ACCESS_ROLES = {"viewer", "operator", "admin", "break-glass"}
ACCESS_TARGET_KINDS = {"Project", "VirtualMachineClaim", "KubernetesClusterClaim", "Console", "Kubeconfig"}
PRODUCT_CATEGORIES = {"compute", "kubernetes", "storage", "network", "platform"}
PRODUCT_VISIBILITY = {"public", "project", "private"}
PRODUCT_LIFECYCLE_STATES = {"Draft", "Published", "Retired"}
PRODUCT_SERVICE_KINDS = {"VirtualMachineClaim", "KubernetesClusterClaim", "Volume", "Network"}
PRODUCT_BILLING_MODES = {"free", "quota", "metered", "external"}
SUBSCRIPTION_STATES = {"Active", "Suspended", "Cancelled"}
ORDER_ACTIONS = {
    "CreateSubscription",
    "ChangeSubscription",
    "CancelSubscription",
    "RenewSubscription",
    "SuspendSubscription",
    "ResumeSubscription",
}
ORDER_STATES = {"Submitted", "Approved", "Rejected", "Cancelled"}
ORDER_POLICY_DECISIONS = {"Allowed", "Blocked", "ManualReview"}
WRITE_ENABLED = os.environ.get("ENABLE_WRITE_API", "true").lower() in ("1", "true", "yes", "on")
WRITE_AUTH_MODE = os.environ.get("PORTAL_WRITE_AUTH_MODE", "static").lower()
WRITE_TOKENS_JSON = os.environ.get("PORTAL_WRITE_TOKENS_JSON", "{}")
JWT_ISSUER = os.environ.get("PORTAL_JWT_ISSUER", "https://issuer.platform.local")
JWT_AUDIENCE = os.environ.get("PORTAL_JWT_AUDIENCE", "platform-portal")
JWT_HS256_SECRET = os.environ.get("PORTAL_JWT_HS256_SECRET", "")
JWT_JWKS_URI = os.environ.get("PORTAL_JWT_JWKS_URI", "")
JWT_JWKS_JSON = os.environ.get("PORTAL_JWT_JWKS_JSON", "")
JWT_ALLOWED_ALGORITHMS_RAW = os.environ.get("PORTAL_JWT_ALLOWED_ALGORITHMS", "")
JWT_ALLOWED_ALGORITHMS = {
    item.strip()
    for item in JWT_ALLOWED_ALGORITHMS_RAW.split(",")
    if item.strip()
}
if not JWT_ALLOWED_ALGORITHMS:
    JWT_ALLOWED_ALGORITHMS = {"RS256"} if WRITE_AUTH_MODE == "oidc-jwks" else {"HS256"}
JWT_JWKS_CACHE_TTL_SECONDS = float(os.environ.get("PORTAL_JWT_JWKS_CACHE_TTL_SECONDS", "300"))
JWT_SUBJECT_CLAIM = os.environ.get("PORTAL_JWT_SUBJECT_CLAIM", "sub")
JWT_GROUPS_CLAIM = os.environ.get("PORTAL_JWT_GROUPS_CLAIM", "groups")
JWT_NAMESPACES_CLAIM = os.environ.get("PORTAL_JWT_NAMESPACES_CLAIM", "platform_namespaces")
JWT_CLOCK_SKEW_SECONDS = int(os.environ.get("PORTAL_JWT_CLOCK_SKEW_SECONDS", "60"))
JWT_AUTH_MODES = {"jwt", "oidc", "oidc-jwks"}
PLATFORM_ADMIN_GROUP = os.environ.get("PORTAL_PLATFORM_ADMIN_GROUP", "platform:admins")
PROJECT_AUDIT_NAMESPACE = os.environ.get("PORTAL_PROJECT_AUDIT_NAMESPACE", "platform-system")
TENANT_ADMIN_GROUP_TEMPLATE = os.environ.get(
    "PORTAL_TENANT_ADMIN_GROUP_TEMPLATE",
    "platform:{namespace}:admins",
)
SUMMARY_CACHE_TTL_SECONDS = float(os.environ.get("SUMMARY_CACHE_TTL_SECONDS", "30"))
SUMMARY_CACHE_STALE_SECONDS = float(os.environ.get("SUMMARY_CACHE_STALE_SECONDS", "60"))
SUMMARY_FORCE_FRESH_GRACE_SECONDS = float(os.environ.get("SUMMARY_FORCE_FRESH_GRACE_SECONDS", "20"))
SUMMARY_MAX_EVENTS = int(os.environ.get("SUMMARY_MAX_EVENTS", "50"))
SUMMARY_MAX_AUDIT_EVENTS = int(os.environ.get("SUMMARY_MAX_AUDIT_EVENTS", "200"))
SUMMARY_MAX_ADMISSION_JOURNALS = int(os.environ.get("SUMMARY_MAX_ADMISSION_JOURNALS", "50"))
SUMMARY_EVENT_LIST_LIMIT = int(os.environ.get("SUMMARY_EVENT_LIST_LIMIT", str(max(200, SUMMARY_MAX_EVENTS * 4))))
SUMMARY_AUDIT_LIST_LIMIT = int(os.environ.get("SUMMARY_AUDIT_LIST_LIMIT", str(max(500, SUMMARY_MAX_AUDIT_EVENTS * 10))))
SUMMARY_ADMISSION_LIST_LIMIT = int(
    os.environ.get("SUMMARY_ADMISSION_LIST_LIMIT", str(max(500, SUMMARY_MAX_ADMISSION_JOURNALS * 5)))
)
SUMMARY_POD_LIST_LIMIT = int(os.environ.get("SUMMARY_POD_LIST_LIMIT", "500"))
WRITE_RATE_LIMIT_WINDOW_SECONDS = float(os.environ.get("PORTAL_WRITE_RATE_LIMIT_WINDOW_SECONDS", "10"))
WRITE_RATE_LIMIT_MAX_REQUESTS = int(os.environ.get("PORTAL_WRITE_RATE_LIMIT_MAX_REQUESTS", "8"))
WRITE_RATE_LIMIT_SCOPE = os.environ.get("PORTAL_WRITE_RATE_LIMIT_SCOPE", "local").lower()
WRITE_RATE_LIMIT_NAMESPACE = os.environ.get("PORTAL_WRITE_RATE_LIMIT_NAMESPACE", "platform-system")
WRITE_RATE_LIMIT_LEASE_PREFIX = os.environ.get("PORTAL_WRITE_RATE_LIMIT_LEASE_PREFIX", "portal-write-rate")


def load_static_write_tokens():
    if WRITE_AUTH_MODE in ("disabled", "none", "off"):
        return {}
    try:
        tokens = json.loads(WRITE_TOKENS_JSON or "{}")
    except json.JSONDecodeError as exc:
        print(f"invalid PORTAL_WRITE_TOKENS_JSON: {exc}", flush=True)
        return {}
    if not isinstance(tokens, dict):
        print("PORTAL_WRITE_TOKENS_JSON must be a JSON object", flush=True)
        return {}
    return tokens


STATIC_WRITE_TOKENS = load_static_write_tokens()


METRICS_LOCK = threading.Lock()
METRICS = {
    "summary_requests": {},
    "summary_cache": {"hit": 0, "miss": 0, "stale": 0},
    "summary_response_bytes": {},
    "summary_refresh_errors": 0,
    "summary_refresh_seconds_sum": 0.0,
    "summary_refresh_seconds_count": 0,
    "write_requests": {},
}


INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Platform Console</title>
  <style>
    :root {
      --bg: #f7f8fb;
      --panel: #ffffff;
      --panel-2: #f9fafc;
      --text: #172033;
      --muted: #667085;
      --line: #d9dee8;
      --line-soft: #ebeff5;
      --accent: #1769e0;
      --green: #178a5b;
      --yellow: #9a6700;
      --red: #c03744;
      --shadow: 0 8px 24px rgba(21, 31, 49, 0.07);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--text); letter-spacing: 0; }
    .shell { min-height: 100vh; display: grid; grid-template-columns: 240px 1fr; }
    .sidebar { background: #111827; color: #e5e7eb; padding: 22px 16px; display: flex; flex-direction: column; gap: 24px; }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 17px; }
    .mark { width: 28px; height: 28px; border-radius: 6px; background: linear-gradient(135deg, #52b6ff, #1f7aec); display: grid; place-items: center; color: white; font-size: 13px; }
    nav { display: grid; gap: 4px; }
    .nav-item { width: 100%; border: 0; background: transparent; padding: 9px 10px; border-radius: 6px; color: #b9c2d0; font-size: 14px; display: flex; align-items: center; gap: 10px; text-align: left; font-weight: 650; cursor: pointer; }
    .nav-item:hover { background: #182233; color: #fff; }
    .nav-item.active { background: #1f2937; color: #fff; }
    .nav-dot { width: 7px; height: 7px; border-radius: 999px; background: currentColor; opacity: .8; }
    .sidebar-foot { margin-top: auto; color: #98a2b3; font-size: 12px; line-height: 1.5; border-top: 1px solid #283241; padding-top: 16px; }
    main { min-width: 0; }
    .topbar { height: 64px; background: rgba(255,255,255,.92); border-bottom: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; padding: 0 28px; position: sticky; top: 0; z-index: 3; backdrop-filter: blur(12px); }
    .title { font-size: 18px; font-weight: 700; }
    .top-actions { display: flex; align-items: center; gap: 10px; }
    .status { display: inline-flex; align-items: center; gap: 8px; color: var(--green); font-weight: 650; font-size: 13px; }
    .status::before { content: ""; width: 8px; height: 8px; border-radius: 999px; background: var(--green); }
    button { border: 1px solid var(--line); background: var(--panel); color: var(--text); border-radius: 6px; padding: 8px 12px; font-weight: 650; font-size: 13px; cursor: pointer; }
    button:hover { border-color: #b9c2d0; }
    button.primary { background: var(--accent); border-color: var(--accent); color: #fff; }
    button.danger { border-color: #f0a7af; color: var(--red); }
    button:disabled { opacity: .55; cursor: not-allowed; }
    .content { padding: 24px 28px 32px; display: grid; gap: 18px; }
    .toolbar { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 6px; box-shadow: var(--shadow); padding: 12px 14px; display: grid; grid-template-columns: minmax(160px, 220px) minmax(180px, 1fr) auto; gap: 10px; align-items: end; }
    .toolbar .field { gap: 4px; }
    .toolbar .field label { color: var(--muted); font-size: 11px; font-weight: 650; text-transform: uppercase; }
    .status-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .metric { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 6px; padding: 16px; box-shadow: var(--shadow); min-height: 92px; }
    .metric label { color: var(--muted); font-size: 12px; font-weight: 650; text-transform: uppercase; }
    .metric strong { display: block; margin-top: 8px; font-size: 26px; line-height: 1; }
    .metric span { display: block; margin-top: 8px; color: var(--muted); font-size: 13px; }
    .grid { display: grid; grid-template-columns: 1.6fr .9fr; gap: 18px; align-items: start; }
    .panel { background: var(--panel); border: 1px solid var(--line-soft); border-radius: 6px; box-shadow: var(--shadow); overflow: hidden; }
    .panel-head { display: flex; justify-content: space-between; align-items: center; padding: 15px 16px; border-bottom: 1px solid var(--line-soft); }
    .panel-head h2 { margin: 0; font-size: 15px; }
    .panel-head small { color: var(--muted); font-size: 12px; }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th { text-align: left; color: var(--muted); font-size: 11px; text-transform: uppercase; padding: 10px 14px; background: var(--panel-2); border-bottom: 1px solid var(--line-soft); }
    td { padding: 11px 14px; border-bottom: 1px solid var(--line-soft); vertical-align: middle; }
    td:last-child { width: 82px; text-align: right; }
    tr:last-child td { border-bottom: none; }
    .pill { display: inline-flex; align-items: center; gap: 6px; border-radius: 999px; padding: 4px 8px; font-size: 12px; font-weight: 650; background: #eef6f2; color: var(--green); }
    .pill.warn { background: #fff7e6; color: var(--yellow); }
    .pill.bad { background: #fff0f2; color: var(--red); }
    .bar { height: 8px; background: #edf1f7; border-radius: 999px; overflow: hidden; min-width: 90px; }
    .bar > i { display: block; height: 100%; background: var(--accent); border-radius: inherit; }
    .quota { display: grid; gap: 12px; padding: 14px 16px; }
    .quota-row { display: grid; grid-template-columns: 92px 1fr 80px; align-items: center; gap: 10px; font-size: 13px; }
    .events { display: grid; gap: 10px; padding: 14px 16px; }
    .event { border-left: 3px solid var(--accent); padding: 8px 0 8px 10px; }
    .event strong { display: block; font-size: 13px; }
    .event span { display: block; color: var(--muted); font-size: 12px; margin-top: 3px; }
    .empty { color: var(--muted); font-size: 13px; padding: 16px; }
    .actions { padding: 14px 16px 16px; display: grid; gap: 14px; }
    .actions-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
    .action-tabs { display: inline-flex; gap: 4px; padding: 3px; border: 1px solid var(--line); border-radius: 6px; background: var(--panel-2); }
    .action-tabs button { border: 0; background: transparent; padding: 6px 10px; }
    .action-tabs button.active { background: #fff; box-shadow: 0 1px 4px rgba(21, 31, 49, .08); }
    .actions[data-mode="tenant"] form[data-action-scope="admin"], .actions[data-mode="admin"] form[data-action-scope="tenant"] { display: none; }
    .form-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; align-items: end; }
    .form-grid { border-top: 1px solid var(--line-soft); padding-top: 14px; }
    .actions-head + .form-grid { border-top: 0; padding-top: 0; }
    .field { display: grid; gap: 5px; min-width: 0; }
    .field label { color: var(--muted); font-size: 11px; font-weight: 650; text-transform: uppercase; }
    input, select { width: 100%; min-width: 0; border: 1px solid var(--line); border-radius: 6px; padding: 8px 9px; color: var(--text); background: #fff; font: inherit; font-size: 13px; }
    .token-field { width: min(240px, 32vw); }
    .token-field label { display: none; }
    .form-actions { display: flex; gap: 8px; align-items: center; }
    .toast { color: var(--muted); font-size: 12px; min-height: 18px; }
    .toast.good { color: var(--green); }
    .toast.bad { color: var(--red); }
    .error { border: 1px solid #ffd0d5; color: var(--red); background: #fff8f9; padding: 12px 14px; border-radius: 6px; display: none; }
    .modal-backdrop { position: fixed; inset: 0; z-index: 20; display: none; align-items: center; justify-content: center; background: rgba(17, 24, 39, .48); padding: 18px; }
    .modal-backdrop.open { display: flex; }
    .modal { width: min(420px, 100%); background: #fff; border: 1px solid var(--line); border-radius: 6px; box-shadow: 0 18px 54px rgba(21, 31, 49, .22); padding: 18px; display: grid; gap: 14px; }
    .modal h2 { margin: 0; font-size: 17px; }
    .modal p { margin: 0; color: var(--muted); font-size: 13px; line-height: 1.5; }
    .modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
    button.confirm-danger { background: var(--red); border-color: var(--red); color: #fff; }
    @media (max-width: 980px) {
      .shell { grid-template-columns: 1fr; }
      .sidebar { position: static; display: grid; grid-template-columns: auto minmax(0, 1fr); align-items: center; gap: 12px; overflow: hidden; padding: 14px; }
      .brand span { display: none; }
      nav { grid-auto-flow: column; grid-auto-columns: max-content; overflow-x: auto; min-width: 0; padding-bottom: 2px; }
      .nav-item { white-space: nowrap; }
      .sidebar-foot { display: none; }
      .topbar { height: auto; min-height: 64px; gap: 10px; align-items: flex-start; padding: 14px 18px; }
      .top-actions { flex-wrap: wrap; justify-content: flex-end; }
      .token-field { width: 180px; }
      .toolbar { grid-template-columns: 1fr; }
      .status-grid, .grid { grid-template-columns: 1fr; }
      .form-grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand"><div class="mark">PC</div><span>Platform Console</span></div>
      <nav>
        <button class="nav-item active" type="button" data-view="Overview" data-kind="all"><span class="nav-dot"></span>Overview</button>
        <button class="nav-item" type="button" data-view="Projects" data-kind="Project"><span class="nav-dot"></span>Projects</button>
        <button class="nav-item" type="button" data-view="Catalog" data-kind="Product Plan"><span class="nav-dot"></span>Catalog</button>
        <button class="nav-item" type="button" data-view="Virtual Machines" data-kind="VM"><span class="nav-dot"></span>Virtual Machines</button>
        <button class="nav-item" type="button" data-view="Kubernetes" data-kind="Kubernetes"><span class="nav-dot"></span>Kubernetes</button>
        <button class="nav-item" type="button" data-view="Capacity" data-kind="Capacity"><span class="nav-dot"></span>Capacity</button>
        <button class="nav-item" type="button" data-view="Access" data-kind="Access"><span class="nav-dot"></span>Access</button>
        <button class="nav-item" type="button" data-view="Audit" data-kind="Audit"><span class="nav-dot"></span>Audit</button>
      </nav>
      <div class="sidebar-foot">Provider self-service surface<br/>Backed by platform.privatecloud.local APIs</div>
    </aside>
    <main>
      <header class="topbar">
        <div><div class="title" id="page-title">Provider Overview</div></div>
        <div class="top-actions">
          <div class="field token-field"><label>Write Token</label><input id="write-token" type="password" autocomplete="off" placeholder="Write token" /></div>
          <span class="status" id="overall-status">Loading</span>
          <button id="refresh">Refresh</button>
        </div>
      </header>
      <section class="content">
        <div class="error" id="error"></div>
        <section class="toolbar" aria-label="Console filters">
          <div class="field"><label>Tenant</label><select id="tenant-filter"><option value="">All tenants</option></select></div>
          <div class="field"><label>Search</label><input id="resource-search" placeholder="Name, kind, endpoint" /></div>
          <button id="clear-filters" type="button">Clear</button>
        </section>
        <div class="status-grid">
          <div class="metric"><label>Projects</label><strong id="m-projects">-</strong><span id="m-projects-sub">tenant boundaries</span></div>
          <div class="metric"><label>VM Claims</label><strong id="m-vms">-</strong><span id="m-vms-sub">self-service workloads</span></div>
          <div class="metric"><label>Tenant K8s</label><strong id="m-kcc">-</strong><span id="m-kcc-sub">routed API endpoints</span></div>
          <div class="metric"><label>Capacity</label><strong id="m-capacity">-</strong><span id="m-capacity-sub">reserved CPU</span></div>
        </div>
        <div class="grid">
          <section class="panel">
            <div class="panel-head"><h2>Tenant Resources</h2><small id="resource-count">-</small></div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Tenant</th><th>Kind</th><th>Name</th><th>Phase</th><th>Endpoint / IP</th><th>Footprint</th><th></th></tr></thead>
                <tbody id="resources"></tbody>
              </table>
            </div>
          </section>
          <section class="panel">
            <div class="panel-head"><h2>Project Quota</h2><small>live usage</small></div>
            <div class="quota" id="quotas"></div>
          </section>
        </div>
        <section class="panel">
          <div class="panel-head"><h2>Self-Service Actions</h2><small id="write-status">claim API</small></div>
          <div class="actions" id="actions" data-mode="tenant">
            <div class="actions-head">
              <div class="action-tabs" role="tablist" aria-label="Action group">
                <button type="button" class="active" data-action-mode="tenant">Tenant Requests</button>
                <button type="button" data-action-mode="admin">Admin Setup</button>
              </div>
              <span class="toast" id="action-mode-status">Tenant self-service</span>
            </div>
            <form id="project-form" class="form-grid" data-action-scope="admin">
              <div class="field"><label>Project</label><input name="name" value="portal-project" /></div>
              <div class="field"><label>Display Name</label><input name="displayName" value="Portal Project" /></div>
              <div class="field"><label>Admins Group</label><input name="adminsGroup" value="platform:portal-project:admins" /></div>
              <div class="field"><label>Tier</label><select name="tier"><option>shared</option></select></div>
              <div class="field"><label>CPU Quota</label><input name="cpu" value="2000m" /></div>
              <div class="field"><label>Memory Quota</label><input name="memory" value="2Gi" /></div>
              <div class="field"><label>VMs</label><input name="vms" type="number" min="0" max="10000" value="5" /></div>
              <div class="field"><label>K8s Clusters</label><input name="tenantClusters" type="number" min="0" max="10000" value="2" /></div>
              <div class="field"><label>Volumes</label><input name="volumes" type="number" min="0" max="100000" value="8" /></div>
              <div class="field"><label>Internet Egress</label><select name="allowInternetEgress"><option value="false">Disabled</option><option value="true">Enabled</option></select></div>
              <div class="form-actions"><button class="primary" type="submit">Create Project</button><span class="toast" id="project-toast"></span></div>
            </form>
            <form id="plan-form" class="form-grid" data-action-scope="admin">
              <div class="field"><label>Plan</label><input name="name" value="portal-vm-basic" /></div>
              <div class="field"><label>Display Name</label><input name="displayName" value="Basic VM" /></div>
              <div class="field"><label>Category</label><select name="category"><option>compute</option><option>kubernetes</option><option>storage</option><option>network</option><option>platform</option></select></div>
              <div class="field"><label>State</label><select name="state"><option>Published</option><option>Draft</option><option>Retired</option></select></div>
              <div class="field"><label>Service</label><select name="serviceKind"><option>VirtualMachineClaim</option><option>KubernetesClusterClaim</option><option>Volume</option><option>Network</option></select></div>
              <div class="field"><label>Service Class</label><input name="serviceClass" value="tiny-vm" /></div>
              <div class="field"><label>Billing</label><select name="billingMode"><option>free</option><option>quota</option></select></div>
              <div class="field"><label>CPU</label><input name="cpu" value="1000m" /></div>
              <div class="field"><label>Memory</label><input name="memory" value="1Gi" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create Plan</button><span class="toast" id="plan-toast"></span></div>
            </form>
            <form id="subscription-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-subscription" /></div>
              <div class="field"><label>Plan</label><select name="planRef" id="subscription-plan"></select></div>
              <div class="field"><label>State</label><select name="state"><option>Active</option><option>Suspended</option><option>Cancelled</option></select></div>
              <div class="field"><label>Auto Renew</label><select name="autoRenew"><option value="true">Enabled</option><option value="false">Disabled</option></select></div>
              <div class="form-actions"><button class="primary" type="submit">Create Subscription</button><span class="toast" id="subscription-toast"></span></div>
            </form>
            <form id="order-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Order</label><input name="name" value="portal-order" /></div>
              <div class="field"><label>Plan</label><select name="planRef" id="order-plan"></select></div>
              <div class="field"><label>Subscription</label><input name="subscriptionRef" value="portal-order-subscription" /></div>
              <div class="field"><label>Action</label><select name="action"><option>CreateSubscription</option><option>CancelSubscription</option><option>RenewSubscription</option><option>SuspendSubscription</option><option>ResumeSubscription</option></select></div>
              <div class="field"><label>State</label><select name="state"><option>Submitted</option><option>Approved</option><option>Cancelled</option><option>Rejected</option></select></div>
              <div class="field"><label>Idempotency Key</label><input name="idempotencyKey" value="portal-order-001" /></div>
              <div class="field"><label>Approval</label><select name="approvalRequired"><option value="false">Not required</option><option value="true">Required</option></select></div>
              <div class="field"><label>Not Before</label><input name="notBefore" placeholder="2026-06-22T23:00:00Z" /></div>
              <div class="field"><label>Expires At</label><input name="expiresAt" placeholder="2026-06-23T01:00:00Z" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create Order</button><span class="toast" id="order-toast"></span></div>
            </form>
            <form id="vm-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-vm" /></div>
              <div class="field"><label>Image</label><select name="image" id="vm-image"></select></div>
              <div class="field"><label>Class</label><select name="class"><option>tiny</option><option>small</option><option>medium</option></select></div>
              <div class="field"><label>CPU</label><input name="cpu" type="number" min="1" max="8" value="1" /></div>
              <div class="field"><label>Memory</label><input name="memory" value="256Mi" /></div>
              <div class="field"><label>Root Disk</label><input name="rootDisk" value="1Gi" /></div>
              <div class="field"><label>Zone</label><input name="zone" value="single-host" /></div>
              <div class="field"><label>Storage</label><input name="storage" value="longhorn-lab" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create VM</button><span class="toast" id="vm-toast"></span></div>
            </form>
            <form id="kcc-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-cluster" /></div>
              <div class="field"><label>Version</label><input name="version" value="v1.32.1" /></div>
              <div class="field"><label>Service Class</label><select name="serviceClass"><option>tiny-tenant-kubernetes</option></select></div>
              <div class="field"><label>Control Plane</label><select name="controlPlaneReplicas"><option>1</option></select></div>
              <div class="field"><label>Workers</label><input name="workerReplicas" type="number" min="0" max="10" value="0" /></div>
              <div class="field"><label>Pod CIDR</label><input name="podCIDR" value="10.245.0.0/16" /></div>
              <div class="field"><label>Zone</label><input name="zone" value="single-host" /></div>
              <div class="field"><label>Storage</label><input name="storage" value="longhorn-lab" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create K8s</button><span class="toast" id="kcc-toast"></span></div>
            </form>
            <form id="volume-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-volume" /></div>
              <div class="field"><label>Size</label><input name="size" value="1Gi" /></div>
              <div class="field"><label>Class</label><select name="class"><option>replicated</option><option>standard</option><option>fast</option><option>archive</option></select></div>
              <div class="field"><label>Access</label><select name="accessMode"><option>ReadWriteOnce</option><option>ReadWriteMany</option><option>ReadOnlyMany</option></select></div>
              <div class="form-actions"><button class="primary" type="submit">Create Volume</button><span class="toast" id="volume-toast"></span></div>
            </form>
            <form id="network-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-network" /></div>
              <div class="field"><label>Type</label><select name="type"><option>isolated</option></select></div>
              <div class="field"><label>CIDR</label><input name="cidr" value="10.247.0.0/24" /></div>
              <div class="field"><label>Gateway</label><input name="gateway" value="10.247.0.1" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create Network</button><span class="toast" id="network-toast"></span></div>
            </form>
            <form id="firewall-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-firewall" /></div>
              <div class="field"><label>Network</label><input name="networkRef" value="portal-network" /></div>
              <div class="field"><label>Direction</label><select name="direction"><option>Ingress</option><option>Egress</option></select></div>
              <div class="field"><label>Protocol</label><select name="protocol"><option>TCP</option><option>UDP</option><option>ICMP</option><option>Any</option></select></div>
              <div class="field"><label>Port</label><input name="port" type="number" min="1" max="65535" value="443" /></div>
              <div class="field"><label>CIDR</label><input name="cidr" value="172.28.10.0/24" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create Rule</button><span class="toast" id="firewall-toast"></span></div>
            </form>
            <form id="access-form" class="form-grid" data-action-scope="tenant">
              <div class="field"><label>Tenant</label><select name="namespace" class="project-select"></select></div>
              <div class="field"><label>Name</label><input name="name" value="portal-access" /></div>
              <div class="field"><label>Subject</label><input name="subjectName" value="platform:tenant-c:admins" /></div>
              <div class="field"><label>Role</label><select name="role"><option>viewer</option><option>operator</option><option>admin</option></select></div>
              <div class="field"><label>Target</label><select name="targetKind"><option>Project</option><option>Kubeconfig</option><option>Console</option><option>VirtualMachineClaim</option><option>KubernetesClusterClaim</option></select></div>
              <div class="field"><label>Duration</label><input name="duration" value="8h" /></div>
              <div class="form-actions"><button class="primary" type="submit">Create Access</button><span class="toast" id="access-toast"></span></div>
            </form>
          </div>
        </section>
        <div class="grid">
          <section class="panel">
            <div class="panel-head"><h2>Capacity Cells</h2><small>placement inventory</small></div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>Cell</th><th>Phase</th><th>Nodes</th><th>CPU</th><th>Memory</th><th>Reservations</th></tr></thead>
                <tbody id="cells"></tbody>
              </table>
            </div>
          </section>
          <section class="panel">
            <div class="panel-head"><h2>Operations Rail</h2><small id="updated">not loaded</small></div>
            <div class="events" id="events"></div>
            <div class="events" id="audit-events"></div>
            <div class="events" id="admission-journals"></div>
          </section>
        </div>
      </section>
    </main>
  </div>
  <div class="modal-backdrop" id="danger-modal" role="dialog" aria-modal="true" aria-labelledby="danger-title">
    <div class="modal">
      <h2 id="danger-title">Confirm dangerous operation</h2>
      <p id="danger-message">This action can change or remove tenant resources.</p>
      <div class="modal-actions">
        <button type="button" id="danger-cancel">Cancel</button>
        <button type="button" class="confirm-danger" id="danger-confirm">Yes</button>
      </div>
    </div>
  </div>
  <script>
    const $ = (id) => document.getElementById(id);
    const phaseClass = (phase) => phase === "Ready" || phase === "Active" || phase === "Admitted" ? "" : (phase === "Rejected" || phase === "Degraded" ? "bad" : "warn");
    const pct = (used, limit) => !limit ? 0 : Math.max(0, Math.min(100, Math.round(used / limit * 100)));
    function parseCpu(v){ if(!v) return 0; return String(v).endsWith("m") ? parseInt(v) : Math.round(parseFloat(v)*1000); }
    function parseMem(v){ if(!v) return 0; const s=String(v); if(s.endsWith("Gi")) return parseFloat(s)*1024; if(s.endsWith("Mi")) return parseFloat(s); return parseFloat(s)||0; }
    function esc(v){ return String(v ?? "").replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
    function pill(phase){ return `<span class="pill ${phaseClass(phase)}">${esc(phase || "Unknown")}</span>`; }
    function setToast(id, text, cls){
      const el = $(id);
      el.textContent = text;
      el.className = `toast ${cls || ""}`;
    }
    function setOptions(selector, values){
      document.querySelectorAll(selector).forEach((el) => {
        const current = el.value;
        el.innerHTML = values.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
        if (values.includes(current)) el.value = current;
      });
    }
    const tokenInput = $("write-token");
    tokenInput.value = localStorage.getItem("platformConsoleWriteToken") || "";
    tokenInput.addEventListener("input", () => {
      localStorage.setItem("platformConsoleWriteToken", tokenInput.value.trim());
      if (lastSummary) render(lastSummary);
    });
    let lastSummary = null;
    let activeKind = localStorage.getItem("platformConsoleActiveKind") || "all";
    let actionMode = localStorage.getItem("platformConsoleActionMode") || "tenant";
    const tenantFilter = $("tenant-filter");
    const searchInput = $("resource-search");
    function selectedTenant(){ return tenantFilter.value || ""; }
    function searchTerm(){ return searchInput.value.trim().toLowerCase(); }
    function emptyTableRow(message, span = 7){ return `<tr><td colspan="${span}" class="empty">${esc(message)}</td></tr>`; }
    function showList(items, itemRenderer, emptyMessage){
      if (!items.length) return `<div class="empty">${esc(emptyMessage)}</div>`;
      return items.map(itemRenderer).join("");
    }
    function setActionMode(mode){
      actionMode = mode === "admin" ? "admin" : "tenant";
      localStorage.setItem("platformConsoleActionMode", actionMode);
      $("actions").dataset.mode = actionMode;
      document.querySelectorAll("[data-action-mode]").forEach((button) => {
        button.classList.toggle("active", button.dataset.actionMode === actionMode);
      });
      $("action-mode-status").textContent = actionMode === "admin" ? "Admin setup" : "Tenant self-service";
    }
    function setTenantOptions(projects){
      const current = tenantFilter.value;
      const values = projects.map(p => p.metadata.name).filter(Boolean).sort();
      tenantFilter.innerHTML = `<option value="">All tenants</option>` + values.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
      if (values.includes(current)) tenantFilter.value = current;
    }
    function applyNavigationState(){
      const escapedKind = window.CSS && CSS.escape ? CSS.escape(activeKind) : String(activeKind).replace(/"/g, '\\"');
      const active = document.querySelector(`.nav-item[data-kind="${escapedKind}"]`) || document.querySelector('.nav-item[data-kind="all"]');
      document.querySelectorAll(".nav-item[data-kind]").forEach((button) => {
        button.classList.toggle("active", button === active);
      });
      $("page-title").textContent = `Provider ${active?.dataset.view || "Overview"}`;
    }
    function resourceMatches(row){
      const tenant = selectedTenant();
      const term = searchTerm();
      const kindMatch = activeKind === "all" || row.kind === activeKind || (activeKind === "Capacity" && row.kind === "Capacity") || (activeKind === "Audit" && row.kind === "Audit");
      const tenantMatch = !tenant || row.tenant === tenant;
      const termMatch = !term || [row.tenant, row.kind, row.name, row.phase, row.endpoint, row.footprint?.cpu, row.footprint?.memory].some(v => String(v || "").toLowerCase().includes(term));
      return kindMatch && tenantMatch && termMatch;
    }
    function renderOperations(data){
      const events = (data.events || []).slice(0, 6);
      $("events").innerHTML = showList(
        events,
        e => `<div class="event"><strong>${esc(e.reason || e.type || "Event")}</strong><span>${esc(e.namespace || "cluster")} / ${esc(e.object || "-")} - ${esc(e.message || "")}</span></div>`,
        "No cluster events reported."
      );
      const auditEvents = (data.auditEvents || []).slice(0, 6);
      $("audit-events").innerHTML = showList(
        auditEvents,
        e => `<div class="event"><strong>${esc(e.action || "audit")} ${esc(e.resource || "")}</strong><span>${esc(e.projectRef || e.namespace || "platform")} / ${esc(e.resourceName || "-")} - ${esc(e.outcome || "Recorded")}</span></div>`,
        "No self-service audit events reported."
      );
      const admissions = (data.admissionJournals || []).slice(0, 6);
      $("admission-journals").innerHTML = showList(
        admissions,
        e => `<div class="event"><strong>${esc(e.decision || "Admission")}</strong><span>${esc(e.projectRef || "platform")} / ${esc(e.claimRef?.name || "-")} - ${esc(e.reason || e.capacityCell || "")}</span></div>`,
        "No admission decisions reported."
      );
    }
    async function apiJson(path, method, payload){
      const headers = {"Content-Type": "application/json"};
      const token = tokenInput.value.trim();
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const response = await fetch(path, {
        method,
        headers,
        body: payload ? JSON.stringify(payload) : undefined,
      });
      const text = await response.text();
      const data = text ? JSON.parse(text) : {};
      if (!response.ok) throw new Error(data.error || `HTTP ${response.status}`);
      return data;
    }
    function render(data) {
      lastSummary = data;
      $("error").style.display = "none";
      applyNavigationState();
      setActionMode(actionMode);
      setTenantOptions(data.projects || []);
      const ready = data.health.ready;
      const baseWriteEnabled = data.health.writeEnabled !== false;
      const authRequired = data.health.writeAuthRequired !== false;
      const hasToken = tokenInput.value.trim().length > 0;
      const canWrite = baseWriteEnabled && (!authRequired || hasToken);
      $("overall-status").textContent = ready ? "Healthy" : "Degraded";
      $("overall-status").style.color = ready ? "var(--green)" : "var(--red)";
      if (!baseWriteEnabled) {
        $("write-status").textContent = "claim API disabled";
      } else if (authRequired && !hasToken) {
        $("write-status").textContent = `${data.health.writeAuthMode || "token"} token required`;
      } else {
        $("write-status").textContent = `claim API ${data.health.writeAuthMode || "ready"}`;
      }
      document.querySelectorAll("#project-form button,#plan-form button,#subscription-form button,#order-form button,#vm-form button,#kcc-form button,#volume-form button,#network-form button,#firewall-form button,#access-form button").forEach(b => b.disabled = !canWrite);
      $("m-projects").textContent = data.projects.length;
      $("m-vms").textContent = data.vmClaims.length;
      $("m-kcc").textContent = data.kubernetesClusterClaims.length;
      $("m-kcc-sub").textContent = `${data.kubernetesClusterClaims.filter(x => x.status.apiEndpoint).length} endpoints published`;
      const reserved = data.capacityCells.reduce((a, c) => a + parseCpu(c.status.reserved?.cpu), 0);
      $("m-capacity").textContent = `${reserved}m`;
      $("m-capacity-sub").textContent = `${data.capacityReservations.length} active reservations`;
      const rows = [];
      data.projects.forEach(x => rows.push({tenant:x.metadata.name, kind:"Project", deleteKind:"projects", deleteNamespace:x.metadata.name, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.tier || "-", footprint:x.spec.quotas || {}}));
      (data.productPlans || []).forEach(x => rows.push({tenant:"provider", kind:"Product Plan", deleteKind:"productplans", deleteNamespace:x.metadata.name, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.service?.kind || "-", footprint:{cpu:x.spec.quotaProfile?.cpu || "-", memory:x.spec.quotaProfile?.memory || "-"}}));
      (data.subscriptions || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Subscription", deleteKind:"subscriptions", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.planRef || "-", footprint:x.status.effectiveQuota || {}}));
      (data.orders || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Order", deleteKind:"orders", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.status.targetName || x.spec.subscriptionRef || "-", footprint:{cpu:x.spec.action || "-", memory:x.spec.planRef || "-"}}));
      data.vmClaims.forEach(x => rows.push({tenant:x.metadata.namespace, kind:"VM", deleteKind:"virtualmachineclaims", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.status.ip || "-", footprint:x.status.admission?.estimatedResources || {}}));
      data.kubernetesClusterClaims.forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Kubernetes", deleteKind:"kubernetesclusterclaims", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.status.apiEndpoint || x.status.lastKnownApiEndpoint || "-", footprint:x.status.admission?.estimatedResources || {}}));
      (data.volumes || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Volume", deleteKind:"volumes", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.status.pvcName || "-", footprint:{cpu:"-", memory:x.spec.size || "-"}}));
      (data.networks || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Network", deleteKind:"networks", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.cidr || "-", footprint:{cpu:"-", memory:x.spec.type || "-"}}));
      (data.firewallRules || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Firewall", deleteKind:"firewallrules", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.direction || "-", footprint:{cpu:"-", memory:x.spec.action || "-"}}));
      (data.accessGrants || []).forEach(x => rows.push({tenant:x.metadata.namespace, kind:"Access", deleteKind:"accessgrants", deleteNamespace:x.metadata.namespace, name:x.metadata.name, phase:x.status.phase, endpoint:x.spec.subject?.name || "-", footprint:{cpu:"-", memory:x.spec.role || "-"}}));
      data.capacityCells.forEach(x => rows.push({tenant:"provider", kind:"Capacity", deletable:false, name:x.metadata.name, phase:x.status.phase, endpoint:`${x.status.readyNodeCount || 0}/${x.status.nodeCount || 0} nodes`, footprint:{cpu:x.status.reserved?.cpu || "0", memory:x.status.reserved?.memory || "0"}}));
      (data.auditEvents || []).slice(0, 20).forEach(x => rows.push({tenant:x.projectRef || x.namespace || "platform", kind:"Audit", deletable:false, name:x.resourceName || x.name || "audit", phase:x.outcome || "Recorded", endpoint:x.resource || "-", footprint:{cpu:x.action || "-", memory:x.statusCode || "-"}}));
      const filteredRows = rows.filter(resourceMatches);
      $("resource-count").textContent = `${filteredRows.length} of ${rows.length} resources`;
      $("resources").innerHTML = filteredRows.length ? filteredRows.map(r => {
        const deleteCell = r.deletable === false || !canWrite ? "" : `<button class="danger" data-delete-kind="${esc(r.deleteKind)}" data-namespace="${esc(r.deleteNamespace || r.tenant)}" data-name="${esc(r.name)}">Delete</button>`;
        return `<tr><td>${esc(r.tenant)}</td><td>${esc(r.kind)}</td><td>${esc(r.name)}</td><td>${pill(r.phase)}</td><td>${esc(r.endpoint)}</td><td>${esc(r.footprint?.cpu || "-")} / ${esc(r.footprint?.memory || "-")}</td><td>${deleteCell}</td></tr>`;
      }).join("") : emptyTableRow("No resources match the current filters.");
      const tenantNames = data.projects.map(p => p.metadata.name).filter(Boolean);
      setOptions(".project-select", tenantNames);
      if (selectedTenant() && tenantNames.includes(selectedTenant())) {
        document.querySelectorAll(".project-select").forEach(el => { el.value = selectedTenant(); });
      }
      setOptions("#vm-image", data.images.map(i => i.metadata.name).filter(Boolean));
      setOptions("#subscription-plan", (data.productPlans || []).map(p => p.metadata.name).filter(Boolean));
      setOptions("#order-plan", (data.productPlans || []).map(p => p.metadata.name).filter(Boolean));
      const quotaProjects = selectedTenant() ? data.projects.filter(p => p.metadata.name === selectedTenant()) : data.projects;
      $("quotas").innerHTML = quotaProjects.length ? quotaProjects.map(p => {
        const q=p.spec.quotas||{}, u=p.status.quotaUsage||{};
        const cpuPct=pct(parseCpu(u.cpu), parseCpu(q.cpu));
        const memPct=pct(parseMem(u.memory), parseMem(q.memory));
        const vmPct=pct(u.vms||0, q.vms||0);
        const kPct=pct(u.tenantClusters||0, q.tenantClusters||0);
        return `<div><strong>${esc(p.metadata.name)}</strong></div>
          <div class="quota-row"><span>CPU</span><div class="bar"><i style="width:${cpuPct}%"></i></div><span>${esc(u.cpu||"0")} / ${esc(q.cpu||"-")}</span></div>
          <div class="quota-row"><span>Memory</span><div class="bar"><i style="width:${memPct}%"></i></div><span>${esc(u.memory||"0")} / ${esc(q.memory||"-")}</span></div>
          <div class="quota-row"><span>VMs</span><div class="bar"><i style="width:${vmPct}%"></i></div><span>${esc(u.vms||0)} / ${esc(q.vms||"-")}</span></div>
          <div class="quota-row"><span>K8s</span><div class="bar"><i style="width:${kPct}%"></i></div><span>${esc(u.tenantClusters||0)} / ${esc(q.tenantClusters||"-")}</span></div>`;
      }).join("") : `<div class="empty">No quota data for the selected tenant.</div>`;
      $("cells").innerHTML = data.capacityCells.length ? data.capacityCells.map(c => `<tr><td>${esc(c.metadata.name)}</td><td>${pill(c.status.phase)}</td><td>${esc(c.status.readyNodeCount || 0)}/${esc(c.status.nodeCount || 0)}</td><td>${esc(c.status.reserved?.cpu || "0")} / ${esc(c.status.allocatable?.cpu || "-")}</td><td>${esc(c.status.reserved?.memory || "0")} / ${esc(c.status.allocatable?.memory || "-")}</td><td>${esc(c.status.reserved?.claims || 0)}</td></tr>`).join("") : emptyTableRow("No capacity cells reported.", 6);
      renderOperations(data);
      $("updated").textContent = `updated ${new Date(data.generatedAt).toLocaleTimeString()}`;
    }
    async function load(fresh = false) {
      try {
        const response = await fetch(`/api/summary${fresh ? "?fresh=1" : ""}`, {cache: "no-cache"});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        render(await response.json());
      } catch (err) {
        $("overall-status").textContent = "Unavailable";
        $("error").textContent = `Unable to load provider summary: ${err.message}`;
        $("error").style.display = "block";
      }
    }
    function confirmDanger(message) {
      const modal = $("danger-modal");
      $("danger-message").textContent = message;
      modal.classList.add("open");
      return new Promise((resolve) => {
        const done = (answer) => {
          modal.classList.remove("open");
          $("danger-confirm").removeEventListener("click", yes);
          $("danger-cancel").removeEventListener("click", no);
          modal.removeEventListener("click", backdrop);
          resolve(answer);
        };
        const yes = () => done(true);
        const no = () => done(false);
        const backdrop = (event) => {
          if (event.target === modal) done(false);
        };
        $("danger-confirm").addEventListener("click", yes);
        $("danger-cancel").addEventListener("click", no);
        modal.addEventListener("click", backdrop);
      });
    }
    $("refresh").addEventListener("click", () => load(true));
    document.querySelectorAll(".nav-item[data-kind]").forEach((button) => {
      button.addEventListener("click", () => {
        activeKind = button.dataset.kind || "all";
        localStorage.setItem("platformConsoleActiveKind", activeKind);
        if (lastSummary) render(lastSummary);
      });
    });
    document.querySelectorAll("[data-action-mode]").forEach((button) => {
      button.addEventListener("click", () => setActionMode(button.dataset.actionMode));
    });
    tenantFilter.addEventListener("change", () => {
      if (lastSummary) render(lastSummary);
    });
    searchInput.addEventListener("input", () => {
      if (lastSummary) render(lastSummary);
    });
    $("clear-filters").addEventListener("click", () => {
      activeKind = "all";
      tenantFilter.value = "";
      searchInput.value = "";
      localStorage.setItem("platformConsoleActiveKind", activeKind);
      if (lastSummary) render(lastSummary);
    });
    $("resources").addEventListener("click", async (event) => {
      const button = event.target.closest("button[data-delete-kind]");
      if (!button) return;
      const confirmed = await confirmDanger(`Delete ${button.dataset.deleteKind}/${button.dataset.name} in ${button.dataset.namespace}?`);
      if (!confirmed) return;
      button.disabled = true;
      try {
        await apiJson(`/api/claims/${encodeURIComponent(button.dataset.deleteKind)}/${encodeURIComponent(button.dataset.namespace)}/${encodeURIComponent(button.dataset.name)}`, "DELETE");
        await load(true);
      } catch (err) {
        $("error").textContent = `Delete failed: ${err.message}`;
        $("error").style.display = "block";
      } finally {
        button.disabled = false;
      }
    });
    $("project-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("project-toast", "creating", "");
      try {
        await apiJson("/api/claims/projects", "POST", {
          name: form.name,
          tenantId: form.name,
          displayName: form.displayName,
          adminsGroup: form.adminsGroup,
          tier: form.tier,
          quotas: {
            cpu: form.cpu,
            memory: form.memory,
            vms: Number(form.vms),
            tenantClusters: Number(form.tenantClusters),
            volumes: Number(form.volumes)
          },
          network: {
            defaultDeny: true,
            allowInternetEgress: form.allowInternetEgress === "true",
            allowedLoadBalancers: 0
          }
        });
        setToast("project-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("project-toast", err.message, "bad");
      }
    });
    $("vm-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("vm-toast", "creating", "");
      try {
        await apiJson("/api/claims/virtualmachineclaims", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          class: form.class,
          image: form.image,
          cpu: Number(form.cpu),
          memory: form.memory,
          rootDisk: form.rootDisk,
          serviceClass: "tiny-vm",
          failureDomains: {zone: form.zone, storage: form.storage},
          runStrategy: "Always"
        });
        setToast("vm-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("vm-toast", err.message, "bad");
      }
    });
    $("plan-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("plan-toast", "creating", "");
      try {
        await apiJson("/api/claims/productplans", "POST", {
          name: form.name,
          displayName: form.displayName,
          category: form.category,
          lifecycle: {state: form.state},
          visibility: "public",
          service: {
            kind: form.serviceKind,
            serviceClass: form.serviceClass
          },
          quotaProfile: {
            cpu: form.cpu,
            memory: form.memory,
            vms: form.serviceKind === "VirtualMachineClaim" ? 1 : 0,
            tenantClusters: form.serviceKind === "KubernetesClusterClaim" ? 1 : 0,
            volumes: 1
          },
          commercial: {billingMode: form.billingMode}
        });
        setToast("plan-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("plan-toast", err.message, "bad");
      }
    });
    $("subscription-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("subscription-toast", "creating", "");
      try {
        await apiJson("/api/claims/subscriptions", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          planRef: form.planRef,
          state: form.state,
          autoRenew: form.autoRenew === "true"
        });
        setToast("subscription-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("subscription-toast", err.message, "bad");
      }
    });
    $("order-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("order-toast", "creating", "");
      try {
        const schedule = {};
        if (form.notBefore) schedule.notBefore = form.notBefore;
        if (form.expiresAt) schedule.expiresAt = form.expiresAt;
        if (["CancelSubscription", "SuspendSubscription", "ChangeSubscription"].includes(form.action)) {
          const confirmed = await confirmDanger(`${form.action} for subscription ${form.subscriptionRef} in ${form.namespace}?`);
          if (!confirmed) {
            setToast("order-toast", "cancelled", "");
            return;
          }
        }
        await apiJson("/api/claims/orders", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          action: form.action,
          state: form.state,
          planRef: form.planRef,
          subscriptionRef: form.subscriptionRef,
          idempotencyKey: form.idempotencyKey,
          approval: {required: form.approvalRequired === "true"},
          policy: {decision: "Allowed"},
          schedule
        });
        setToast("order-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("order-toast", err.message, "bad");
      }
    });
    $("kcc-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("kcc-toast", "creating", "");
      try {
        await apiJson("/api/claims/kubernetesclusterclaims", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          version: form.version,
          distribution: "kubeadm",
          controlPlaneReplicas: Number(form.controlPlaneReplicas),
          controlPlaneClass: "tiny",
          workerReplicas: Number(form.workerReplicas),
          workerClass: "tiny",
          serviceClass: form.serviceClass,
          failureDomains: {zone: form.zone, storage: form.storage},
          podCIDR: form.podCIDR,
          serviceCIDR: "10.97.0.0/12",
          cni: "cilium"
        });
        setToast("kcc-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("kcc-toast", err.message, "bad");
      }
    });
    $("volume-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("volume-toast", "creating", "");
      try {
        await apiJson("/api/claims/volumes", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          size: form.size,
          class: form.class,
          accessMode: form.accessMode,
          sourceType: "empty",
          encryptionEnabled: false,
          reclaimPolicy: "Snapshot"
        });
        setToast("volume-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("volume-toast", err.message, "bad");
      }
    });
    $("network-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("network-toast", "creating", "");
      try {
        await apiJson("/api/claims/networks", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          type: form.type,
          cidr: form.cidr,
          gateway: form.gateway,
          dns: ["10.96.0.10"],
          egress: {allowInternet: false, nat: false},
          loadBalancer: {allowed: false}
        });
        setToast("network-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("network-toast", err.message, "bad");
      }
    });
    $("firewall-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("firewall-toast", "creating", "");
      try {
        await apiJson("/api/claims/firewallrules", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          networkRef: form.networkRef,
          direction: form.direction,
          action: "Allow",
          priority: 100,
          rules: [{
            protocol: form.protocol,
            ports: form.port ? [Number(form.port)] : [],
            cidrs: form.cidr ? [form.cidr] : []
          }]
        });
        setToast("firewall-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("firewall-toast", err.message, "bad");
      }
    });
    $("access-form").addEventListener("submit", async (event) => {
      event.preventDefault();
      const form = Object.fromEntries(new FormData(event.target).entries());
      setToast("access-toast", "creating", "");
      try {
        await apiJson("/api/claims/accessgrants", "POST", {
          namespace: form.namespace,
          name: form.name,
          projectRef: form.namespace,
          subject: {kind: "Group", name: form.subjectName, provider: "oidc"},
          role: form.role,
          target: {kind: form.targetKind, name: form.namespace},
          duration: form.duration,
          approval: {required: false}
        });
        setToast("access-toast", "created", "good");
        await load(true);
      } catch (err) {
        setToast("access-toast", err.message, "bad");
      }
    });
    load(true);
    setInterval(load, 15000);
  </script>
</body>
</html>
"""


class KubernetesClient:
    def __init__(self):
        host = os.environ.get("KUBERNETES_SERVICE_HOST", "kubernetes.default.svc")
        port = os.environ.get("KUBERNETES_SERVICE_PORT", "443")
        self.base = f"https://{host}:{port}"
        with open(TOKEN_PATH, "r", encoding="utf-8") as handle:
            self.token = handle.read().strip()
        self.context = ssl.create_default_context(cafile=CA_PATH)

    def get(self, path):
        req = urllib.request.Request(
            f"{self.base}{path}",
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, context=self.context, timeout=8) as response:
            return json.loads(response.read().decode("utf-8"))

    def request(self, method, path, payload=None):
        body = None
        headers = {"Authorization": f"Bearer {self.token}", "Accept": "application/json"}
        if payload is not None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = urllib.request.Request(
            f"{self.base}{path}",
            data=body,
            headers=headers,
            method=method,
        )
        with urllib.request.urlopen(req, context=self.context, timeout=8) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def create_namespaced_custom_object(self, plural, namespace, payload):
        path = f"/apis/{GROUP}/{VERSION}/namespaces/{namespace}/{plural}"
        return self.request("POST", path, payload)

    def delete_namespaced_custom_object(self, plural, namespace, name):
        path = f"/apis/{GROUP}/{VERSION}/namespaces/{namespace}/{plural}/{name}"
        return self.request("DELETE", path)

    def create_cluster_custom_object(self, plural, payload):
        path = f"/apis/{GROUP}/{VERSION}/{plural}"
        return self.request("POST", path, payload)

    def delete_cluster_custom_object(self, plural, name):
        path = f"/apis/{GROUP}/{VERSION}/{plural}/{name}"
        return self.request("DELETE", path)

    def create_namespaced_lease(self, namespace, payload):
        path = f"/apis/coordination.k8s.io/v1/namespaces/{namespace}/leases"
        return self.request("POST", path, payload)

    def get_namespaced_lease(self, namespace, name):
        path = f"/apis/coordination.k8s.io/v1/namespaces/{namespace}/leases/{name}"
        return self.get(path)

    def replace_namespaced_lease(self, namespace, name, payload):
        path = f"/apis/coordination.k8s.io/v1/namespaces/{namespace}/leases/{name}"
        return self.request("PUT", path, payload)


def items(payload):
    return payload.get("items", []) if isinstance(payload, dict) else []


def limited_path(path, limit):
    if not limit or limit <= 0:
        return path
    separator = "&" if "?" in path else "?"
    return f"{path}{separator}limit={int(limit)}"


def limited_items(client, path, limit):
    return items(client.get(limited_path(path, limit)))


def optional_summary_items(name, loader):
    try:
        return loader()
    except Exception as exc:
        print(f"summary optional rail {name} unavailable: {exc}", flush=True)
        return []


def dns_label_name(raw, max_length=63):
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in raw.lower()).strip("-")
    if not cleaned:
        cleaned = "x"
    if len(cleaned) <= max_length:
        return cleaned
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8]
    return f"{cleaned[: max_length - 9].rstrip('-')}-{digest}"


def validate_name(value, field):
    if not isinstance(value, str) or not DNS_LABEL_RE.match(value):
        raise ValueError(f"{field} must be a DNS label")
    return value


def validate_quantity(value, field):
    if not isinstance(value, str) or not RESOURCE_RE.match(value):
        raise ValueError(f"{field} must use Mi or Gi units")
    return value


def validate_cpu_quantity(value, field):
    if not isinstance(value, str) or not CPU_RESOURCE_RE.match(value):
        raise ValueError(f"{field} must use whole cores or millicores")
    return value


def validate_int(value, field, minimum, maximum):
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum or value > maximum:
        raise ValueError(f"{field} must be an integer between {minimum} and {maximum}")
    return value


def validate_cidr(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a CIDR string")
    try:
        ipaddress.ip_network(value, strict=False)
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid CIDR") from exc
    return value


def validate_ip(value, field):
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an IP address")
    try:
        ipaddress.ip_address(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a valid IP address") from exc
    return value


def validate_bool(value, field):
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be boolean")
    return value


def validate_enum(value, field, allowed):
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"{field} is not supported")
    return value


def validate_optional_name(value, field):
    if value in (None, ""):
        return None
    return validate_name(value, field)


def validate_string(value, field, max_length=200):
    if not isinstance(value, str) or not value.strip() or len(value) > max_length:
        raise ValueError(f"{field} must be a non-empty string up to {max_length} characters")
    return value.strip()


def validate_optional_string(value, field, max_length=200):
    if value in (None, ""):
        return None
    return validate_string(value, field, max_length)


def validate_optional_rfc3339(value, field):
    raw = validate_optional_string(value, field, 64)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be RFC3339 time") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def validate_cidr_list(value, field, minimum=0, maximum=16):
    if value in (None, ""):
        return []
    if not isinstance(value, list) or len(value) < minimum or len(value) > maximum:
        raise ValueError(f"{field} must be a list with {minimum}-{maximum} CIDRs")
    return [validate_cidr(item, f"{field}[]") for item in value]


def validate_dns_list(value, field):
    if value in (None, ""):
        return []
    if not isinstance(value, list) or len(value) > 8:
        raise ValueError(f"{field} must be a list with up to 8 IP addresses")
    return [validate_ip(item, f"{field}[]") for item in value]


def validate_ports(value, field):
    if value in (None, ""):
        return []
    if not isinstance(value, list) or len(value) > 32:
        raise ValueError(f"{field} must be a list with up to 32 ports")
    return [validate_int(port, f"{field}[]", 1, 65535) for port in value]


def validate_project_namespace(payload):
    namespace = validate_name(payload.get("namespace"), "namespace")
    name = validate_name(payload.get("name"), "name")
    project_ref = validate_name(payload.get("projectRef", namespace), "projectRef")
    if project_ref != namespace:
        raise ValueError("projectRef must match namespace in the lab portal")
    return namespace, name, project_ref


def build_project(payload):
    name = validate_name(payload.get("name"), "name")
    tenant_id = validate_name(payload.get("tenantId", name), "tenantId")
    if tenant_id != name:
        raise ValueError("tenantId must match Project name in the portal onboarding flow")
    quotas = payload.get("quotas") or {}
    network = payload.get("network") or {}
    if not isinstance(quotas, dict):
        raise ValueError("quotas must be an object")
    if not isinstance(network, dict):
        raise ValueError("network must be an object")

    spec = {
        "tenantId": tenant_id,
        "tier": validate_enum(payload.get("tier", "shared"), "tier", PROJECT_TIERS),
        "adminsGroup": validate_string(
            payload.get(
                "adminsGroup",
                TENANT_ADMIN_GROUP_TEMPLATE.format(namespace=name, project=name),
            ),
            "adminsGroup",
            200,
        ),
        "quotas": {
            "cpu": validate_cpu_quantity(quotas.get("cpu", "2000m"), "quotas.cpu"),
            "memory": validate_quantity(quotas.get("memory", "2Gi"), "quotas.memory"),
            "vms": validate_int(quotas.get("vms", 5), "quotas.vms", 0, 10000),
            "tenantClusters": validate_int(quotas.get("tenantClusters", 2), "quotas.tenantClusters", 0, 10000),
            "volumes": validate_int(quotas.get("volumes", 8), "quotas.volumes", 0, 100000),
        },
        "network": {
            "defaultDeny": validate_bool(network.get("defaultDeny", True), "network.defaultDeny"),
            "allowInternetEgress": validate_bool(
                network.get("allowInternetEgress", False),
                "network.allowInternetEgress",
            ),
            "allowedLoadBalancers": validate_int(
                network.get("allowedLoadBalancers", 0),
                "network.allowedLoadBalancers",
                0,
                10000,
            ),
        },
    }
    display_name = validate_optional_string(payload.get("displayName"), "displayName", 120)
    if display_name:
        spec["displayName"] = display_name
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "Project",
        "metadata": {"name": name},
        "spec": spec,
    }


def build_product_plan(payload):
    name = validate_name(payload.get("name"), "name")
    lifecycle = payload.get("lifecycle") or {}
    service = payload.get("service") or {}
    quota = payload.get("quotaProfile") or {}
    commercial = payload.get("commercial") or {}
    if not isinstance(lifecycle, dict):
        raise ValueError("lifecycle must be an object")
    if not isinstance(service, dict):
        raise ValueError("service must be an object")
    if not isinstance(quota, dict):
        raise ValueError("quotaProfile must be an object")
    if not isinstance(commercial, dict):
        raise ValueError("commercial must be an object")
    spec = {
        "displayName": validate_string(payload.get("displayName", name), "displayName", 120),
        "category": validate_enum(payload.get("category", "compute"), "category", PRODUCT_CATEGORIES),
        "visibility": validate_enum(payload.get("visibility", "public"), "visibility", PRODUCT_VISIBILITY),
        "lifecycle": {
            "state": validate_enum(lifecycle.get("state", "Draft"), "lifecycle.state", PRODUCT_LIFECYCLE_STATES),
        },
        "service": {
            "kind": validate_enum(service.get("kind", "VirtualMachineClaim"), "service.kind", PRODUCT_SERVICE_KINDS),
            "serviceClass": validate_string(service.get("serviceClass", "tiny-vm"), "service.serviceClass", 80),
        },
        "quotaProfile": {},
        "commercial": {
            "billingMode": validate_enum(commercial.get("billingMode", "free"), "commercial.billingMode", PRODUCT_BILLING_MODES),
        },
    }
    description = validate_optional_string(payload.get("description"), "description", 500)
    if description:
        spec["description"] = description
    for field in ("publishAt", "retireAt", "supportEndAt"):
        value = validate_optional_string(lifecycle.get(field), f"lifecycle.{field}", 80)
        if value:
            spec["lifecycle"][field] = value
    default_image = validate_optional_name(service.get("defaultImage"), "service.defaultImage")
    default_version = validate_optional_string(service.get("defaultVersion"), "service.defaultVersion", 40)
    if default_image:
        spec["service"]["defaultImage"] = default_image
    if default_version:
        spec["service"]["defaultVersion"] = default_version
    if isinstance(service.get("capacityCellSelector"), dict):
        selector = {}
        for key in ("provider", "region", "site", "zone", "storage", "network"):
            value = validate_optional_string(service["capacityCellSelector"].get(key), f"service.capacityCellSelector.{key}", 80)
            if value:
                selector[key] = value
        if selector:
            spec["service"]["capacityCellSelector"] = selector
    cpu = quota.get("cpu")
    memory = quota.get("memory")
    storage = quota.get("storage")
    if cpu not in (None, ""):
        spec["quotaProfile"]["cpu"] = validate_cpu_quantity(cpu, "quotaProfile.cpu")
    if memory not in (None, ""):
        spec["quotaProfile"]["memory"] = validate_quantity(memory, "quotaProfile.memory")
    if storage not in (None, ""):
        spec["quotaProfile"]["storage"] = validate_quantity(storage, "quotaProfile.storage")
    for field in ("vms", "tenantClusters", "volumes"):
        if field in quota:
            spec["quotaProfile"][field] = validate_int(quota.get(field), f"quotaProfile.{field}", 0, 100000)
    for field in ("currency", "monthlyPrice"):
        value = validate_optional_string(commercial.get(field), f"commercial.{field}", 32)
        if value:
            spec["commercial"][field] = value
    if isinstance(commercial.get("meteringKeys"), list):
        spec["commercial"]["meteringKeys"] = [
            validate_string(item, "commercial.meteringKeys[]", 80)
            for item in commercial["meteringKeys"][:16]
        ]
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "ProductPlan",
        "metadata": {"name": name},
        "spec": spec,
    }


def build_subscription(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "Subscription",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "projectRef": project_ref,
            "planRef": validate_name(payload.get("planRef"), "planRef"),
            "displayName": validate_optional_string(payload.get("displayName"), "displayName", 120) or name,
            "state": validate_enum(payload.get("state", "Active"), "state", SUBSCRIPTION_STATES),
            "autoRenew": validate_bool(payload.get("autoRenew", True), "autoRenew"),
            "requestedBy": validate_optional_string(payload.get("requestedBy"), "requestedBy", 200) or "portal",
        },
    }


def build_order(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    action = validate_enum(payload.get("action", "CreateSubscription"), "action", ORDER_ACTIONS)
    state = validate_enum(payload.get("state", "Submitted"), "state", ORDER_STATES)
    plan_ref = validate_name(payload.get("planRef"), "planRef")
    subscription_ref = validate_optional_name(payload.get("subscriptionRef"), "subscriptionRef")
    idempotency_key = validate_optional_string(payload.get("idempotencyKey"), "idempotencyKey", 160)
    requested_by = validate_optional_string(payload.get("requestedBy"), "requestedBy", 200)
    billing_account_ref = validate_optional_string(payload.get("billingAccountRef"), "billingAccountRef", 120)
    approval = payload.get("approval") or {}
    policy = payload.get("policy") or {}
    budget = payload.get("budget") or {}
    schedule = payload.get("schedule") or {}
    if not isinstance(approval, dict):
        raise ValueError("approval must be an object")
    if not isinstance(policy, dict):
        raise ValueError("policy must be an object")
    if not isinstance(budget, dict):
        raise ValueError("budget must be an object")
    if not isinstance(schedule, dict):
        raise ValueError("schedule must be an object")
    spec = {
        "projectRef": project_ref,
        "action": action,
        "state": state,
        "planRef": plan_ref,
        "idempotencyKey": idempotency_key or f"{namespace}:{name}:{action}:{plan_ref}",
        "requestedBy": requested_by or "portal",
        "policy": {
            "decision": validate_enum(policy.get("decision", "Allowed"), "policy.decision", ORDER_POLICY_DECISIONS)
        },
        "approval": {"required": validate_bool(approval.get("required", False), "approval.required")},
        "parameters": {},
    }
    if subscription_ref:
        spec["subscriptionRef"] = subscription_ref
    if billing_account_ref:
        spec["billingAccountRef"] = billing_account_ref
    for field in ("approvedBy", "ticketRef"):
        value = validate_optional_string(approval.get(field), f"approval.{field}", 200)
        if value:
            spec["approval"][field] = value
    reason = validate_optional_string(policy.get("reason"), "policy.reason", 300)
    if reason:
        spec["policy"]["reason"] = reason
    for field in ("currency", "estimatedMonthly"):
        value = validate_optional_string(budget.get(field), f"budget.{field}", 32)
        if value:
            spec.setdefault("budget", {})[field] = value
    schedule_spec = {}
    not_before = validate_optional_rfc3339(schedule.get("notBefore"), "schedule.notBefore")
    expires_at = validate_optional_rfc3339(schedule.get("expiresAt"), "schedule.expiresAt")
    reason_text = validate_optional_string(schedule.get("reason"), "schedule.reason", 200)
    if not_before:
        schedule_spec["notBefore"] = not_before
    if expires_at:
        schedule_spec["expiresAt"] = expires_at
    if reason_text:
        schedule_spec["reason"] = reason_text
    if schedule_spec:
        spec["schedule"] = schedule_spec
    parameters = payload.get("parameters")
    if parameters not in (None, ""):
        if not isinstance(parameters, dict):
            raise ValueError("parameters must be an object")
        spec["parameters"] = parameters
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "Order",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }


def validate_failure_domains(value):
    if value in (None, "", {}):
        return {}
    if not isinstance(value, dict):
        raise ValueError("failureDomains must be an object")
    result = {}
    for key, raw_value in value.items():
        if key not in FAILURE_DOMAIN_KEYS:
            raise ValueError(f"failureDomains.{key} is not supported")
        domain = validate_optional_string(raw_value, f"failureDomains.{key}", 80)
        if domain:
            result[key] = domain
    return result


def build_placement(payload, service_class):
    placement = {"serviceClass": service_class}
    failure_domains = validate_failure_domains(payload.get("failureDomains"))
    if failure_domains:
        placement["failureDomains"] = failure_domains
    return placement


def build_vm_claim(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    vm_class = payload.get("class", "tiny")
    if vm_class not in VM_CLASS_NAMES:
        raise ValueError("class is not supported")
    service_class = payload.get("serviceClass", "tiny-vm")
    if not isinstance(service_class, str) or service_class not in {"tiny-vm"}:
        raise ValueError("serviceClass is not supported")
    run_strategy = payload.get("runStrategy", "Always")
    if run_strategy not in RUN_STRATEGIES:
        raise ValueError("runStrategy is not supported")
    image = validate_name(payload.get("image"), "image")
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "VirtualMachineClaim",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "projectRef": project_ref,
            "class": vm_class,
            "image": {"name": image, "source": "catalog"},
            "resources": {
                "cpu": validate_int(payload.get("cpu", 1), "cpu", 1, 8),
                "memory": validate_quantity(payload.get("memory", "256Mi"), "memory"),
                "rootDisk": validate_quantity(payload.get("rootDisk", "1Gi"), "rootDisk"),
            },
            "placement": build_placement(payload, service_class),
            "availability": {"runStrategy": run_strategy, "liveMigratable": True},
        },
    }


def build_kcc_claim(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    distribution = payload.get("distribution", "kubeadm")
    if distribution != "kubeadm":
        raise ValueError("only kubeadm tenant clusters are supported in the lab portal")
    service_class = payload.get("serviceClass", "tiny-tenant-kubernetes")
    if service_class not in {"tiny-tenant-kubernetes", "ha-tenant-kubernetes"}:
        raise ValueError("serviceClass is not supported")
    cp_replicas = validate_int(payload.get("controlPlaneReplicas", 1), "controlPlaneReplicas", 1, 5)
    if cp_replicas not in CONTROL_PLANE_REPLICAS:
        raise ValueError("controlPlaneReplicas must be 1, 3, or 5")
    worker_replicas = validate_int(payload.get("workerReplicas", 0), "workerReplicas", 0, 10)
    control_plane_class = payload.get("controlPlaneClass", "tiny")
    worker_class = payload.get("workerClass", "tiny")
    if control_plane_class not in KCC_CONTROL_PLANE_CLASS_NAMES:
        raise ValueError("controlPlaneClass is not supported")
    if worker_class not in KCC_WORKER_CLASS_NAMES:
        raise ValueError("workerClass is not supported")
    cni = payload.get("cni", "cilium")
    if cni != "cilium":
        raise ValueError("only cilium CNI is supported in the lab portal")
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "KubernetesClusterClaim",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "projectRef": project_ref,
            "version": payload.get("version", "v1.32.1"),
            "distribution": distribution,
            "controlPlane": {
                "replicas": cp_replicas,
                "class": control_plane_class,
            },
            "workers": [
                {
                    "name": "default",
                    "replicas": worker_replicas,
                    "class": worker_class,
                }
            ],
            "placement": build_placement(payload, service_class),
            "network": {
                "podCIDR": validate_cidr(payload.get("podCIDR", "10.245.0.0/16"), "podCIDR"),
                "serviceCIDR": validate_cidr(payload.get("serviceCIDR", "10.97.0.0/12"), "serviceCIDR"),
                "cni": cni,
            },
            "lifecycle": {"autoUpgrade": False},
        },
    }


def build_volume(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    source_type = validate_enum(payload.get("sourceType", "empty"), "sourceType", VOLUME_SOURCES)
    source = {"type": source_type}
    source_ref = validate_optional_string(payload.get("sourceRef"), "sourceRef", 128)
    if source_ref:
        source["ref"] = source_ref
    encryption_enabled = validate_bool(payload.get("encryptionEnabled", False), "encryptionEnabled")
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "Volume",
        "metadata": {"name": name, "namespace": namespace},
        "spec": {
            "projectRef": project_ref,
            "size": validate_quantity(payload.get("size", "1Gi"), "size"),
            "class": validate_enum(payload.get("class", "replicated"), "class", VOLUME_CLASSES),
            "accessMode": validate_enum(payload.get("accessMode", "ReadWriteOnce"), "accessMode", VOLUME_ACCESS_MODES),
            "source": source,
            "encryption": {"enabled": encryption_enabled},
            "reclaimPolicy": validate_enum(payload.get("reclaimPolicy", "Snapshot"), "reclaimPolicy", VOLUME_RECLAIM_POLICIES),
        },
    }


def build_network(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    egress = payload.get("egress") or {}
    load_balancer = payload.get("loadBalancer") or {}
    if not isinstance(egress, dict) or not isinstance(load_balancer, dict):
        raise ValueError("egress and loadBalancer must be objects")
    spec = {
        "projectRef": project_ref,
        "type": validate_enum(payload.get("type", "isolated"), "type", NETWORK_TYPES),
        "cidr": validate_cidr(payload.get("cidr"), "cidr"),
        "egress": {
            "allowInternet": validate_bool(egress.get("allowInternet", False), "egress.allowInternet"),
            "nat": validate_bool(egress.get("nat", False), "egress.nat"),
        },
        "loadBalancer": {
            "allowed": validate_bool(load_balancer.get("allowed", False), "loadBalancer.allowed"),
        },
    }
    gateway = payload.get("gateway")
    if gateway not in (None, ""):
        spec["gateway"] = validate_ip(gateway, "gateway")
    dns = validate_dns_list(payload.get("dns", []), "dns")
    if dns:
        spec["dns"] = dns
    pool_ref = validate_optional_string(load_balancer.get("poolRef"), "loadBalancer.poolRef", 128)
    if pool_ref:
        spec["loadBalancer"]["poolRef"] = pool_ref
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "Network",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }


def build_firewall_rule(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    rules = payload.get("rules")
    if not isinstance(rules, list) or not rules or len(rules) > 16:
        raise ValueError("rules must be a list with 1-16 items")
    rendered_rules = []
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError("rules[] must be objects")
        rendered_rule = {
            "protocol": validate_enum(rule.get("protocol", "TCP"), f"rules[{index}].protocol", FIREWALL_PROTOCOLS),
        }
        ports = validate_ports(rule.get("ports", []), f"rules[{index}].ports")
        cidrs = validate_cidr_list(rule.get("cidrs", []), f"rules[{index}].cidrs")
        if ports:
            rendered_rule["ports"] = ports
        if cidrs:
            rendered_rule["cidrs"] = cidrs
        rendered_rules.append(rendered_rule)
    spec = {
        "projectRef": project_ref,
        "direction": validate_enum(payload.get("direction", "Ingress"), "direction", FIREWALL_DIRECTIONS),
        "action": validate_enum(payload.get("action", "Allow"), "action", FIREWALL_ACTIONS),
        "priority": validate_int(payload.get("priority", 100), "priority", 1, 10000),
        "rules": rendered_rules,
    }
    network_ref = validate_optional_name(payload.get("networkRef"), "networkRef")
    if network_ref:
        spec["networkRef"] = network_ref
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "FirewallRule",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }


def build_access_grant(payload):
    namespace, name, project_ref = validate_project_namespace(payload)
    subject = payload.get("subject") or {}
    target = payload.get("target") or {}
    approval = payload.get("approval") or {}
    if not isinstance(subject, dict) or not isinstance(target, dict) or not isinstance(approval, dict):
        raise ValueError("subject, target, and approval must be objects")
    spec = {
        "projectRef": project_ref,
        "subject": {
            "kind": validate_enum(subject.get("kind", "Group"), "subject.kind", ACCESS_SUBJECT_KINDS),
            "name": validate_string(subject.get("name"), "subject.name", 200),
            "provider": validate_enum(subject.get("provider", "oidc"), "subject.provider", ACCESS_PROVIDERS),
        },
        "role": validate_enum(payload.get("role", "viewer"), "role", ACCESS_ROLES),
        "target": {
            "kind": validate_enum(target.get("kind", "Project"), "target.kind", ACCESS_TARGET_KINDS),
            "name": validate_string(target.get("name", namespace), "target.name", 128),
        },
        "approval": {
            "required": validate_bool(approval.get("required", False), "approval.required"),
        },
    }
    duration = validate_optional_string(payload.get("duration"), "duration", 64)
    if duration:
        spec["duration"] = duration
    approver_group = validate_optional_string(approval.get("approverGroup"), "approval.approverGroup", 200)
    ticket_ref = validate_optional_string(approval.get("ticketRef"), "approval.ticketRef", 200)
    if approver_group:
        spec["approval"]["approverGroup"] = approver_group
    if ticket_ref:
        spec["approval"]["ticketRef"] = ticket_ref
    return {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "AccessGrant",
        "metadata": {"name": name, "namespace": namespace},
        "spec": spec,
    }


WRITE_BUILDERS = {
    "/api/claims/projects": ("projects", build_project, "cluster"),
    "/api/claims/productplans": ("productplans", build_product_plan, "cluster"),
    "/api/claims/subscriptions": ("subscriptions", build_subscription, "namespaced"),
    "/api/claims/orders": ("orders", build_order, "namespaced"),
    "/api/claims/virtualmachineclaims": ("virtualmachineclaims", build_vm_claim, "namespaced"),
    "/api/claims/kubernetesclusterclaims": ("kubernetesclusterclaims", build_kcc_claim, "namespaced"),
    "/api/claims/volumes": ("volumes", build_volume, "namespaced"),
    "/api/claims/networks": ("networks", build_network, "namespaced"),
    "/api/claims/firewallrules": ("firewallrules", build_firewall_rule, "namespaced"),
    "/api/claims/accessgrants": ("accessgrants", build_access_grant, "namespaced"),
}
DELETE_PLURALS = {plural: scope for plural, _, scope in WRITE_BUILDERS.values()}


def compact_meta(obj):
    meta = obj.get("metadata", {})
    return {
        "name": meta.get("name"),
        "namespace": meta.get("namespace"),
        "creationTimestamp": meta.get("creationTimestamp"),
        "labels": meta.get("labels", {}),
    }


def compact(obj):
    return {
        "metadata": compact_meta(obj),
        "spec": obj.get("spec", {}),
        "status": obj.get("status", {}),
    }


def compact_node(obj):
    status = obj.get("status", {})
    ready = "Unknown"
    for condition in status.get("conditions", []):
        if condition.get("type") == "Ready":
            ready = condition.get("status", "Unknown")
            break
    return {
        "metadata": {
            "name": obj.get("metadata", {}).get("name"),
            "creationTimestamp": obj.get("metadata", {}).get("creationTimestamp"),
        },
        "status": {
            "ready": ready,
            "allocatable": status.get("allocatable", {}),
            "capacity": status.get("capacity", {}),
            "nodeInfo": {
                "kubeletVersion": status.get("nodeInfo", {}).get("kubeletVersion"),
                "osImage": status.get("nodeInfo", {}).get("osImage"),
                "architecture": status.get("nodeInfo", {}).get("architecture"),
            },
        },
    }


def event_summary(event):
    involved = event.get("involvedObject", {})
    return {
        "namespace": event.get("metadata", {}).get("namespace"),
        "object": f"{involved.get('kind', '')}/{involved.get('name', '')}".strip("/"),
        "type": event.get("type"),
        "reason": event.get("reason"),
        "message": event.get("message", "")[:220],
        "lastTimestamp": event.get("lastTimestamp") or event.get("eventTime"),
    }


def audit_event_summary(event):
    spec = event.get("spec", {})
    return {
        "namespace": event.get("metadata", {}).get("namespace"),
        "name": event.get("metadata", {}).get("name"),
        "projectRef": spec.get("projectRef"),
        "subject": spec.get("subject"),
        "action": spec.get("action"),
        "resource": spec.get("resource"),
        "resourceName": spec.get("resourceName"),
        "outcome": spec.get("outcome"),
        "statusCode": spec.get("statusCode"),
        "message": spec.get("message", "")[:220],
        "timestamp": spec.get("timestamp"),
    }


def list_audit_events(client):
    try:
        return [
            audit_event_summary(x)
            for x in limited_items(client, f"/apis/{GROUP}/{VERSION}/{AUDIT_PLURAL}", SUMMARY_AUDIT_LIST_LIMIT)
        ]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise


def admission_journal_summary(journal):
    spec = journal.get("spec", {})
    return {
        "metadata": compact_meta(journal),
        "claimRef": spec.get("claimRef", {}),
        "projectRef": spec.get("projectRef"),
        "decision": spec.get("decision"),
        "reason": spec.get("reason"),
        "message": spec.get("message", "")[:220],
        "capacityCell": spec.get("capacityCell"),
        "serviceClass": spec.get("serviceClass"),
        "resources": spec.get("resources", {}),
        "quotaSnapshot": spec.get("quotaSnapshot", {}),
        "locks": spec.get("locks", {}),
        "controller": spec.get("controller", {}),
        "observedAt": spec.get("observedAt"),
    }


def list_admission_journals(client):
    try:
        return [
            admission_journal_summary(x)
            for x in limited_items(
                client,
                f"/apis/{GROUP}/{VERSION}/admissionjournals",
                SUMMARY_ADMISSION_LIST_LIMIT,
            )
        ]
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return []
        raise


def build_summary(client):
    projects = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/projects"))]
    cells = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/capacitycells"))]
    reservations = [
        compact(x)
        for x in items(client.get(f"/apis/{GROUP}/{VERSION}/capacityreservations"))
        if x.get("status", {}).get("phase") == "Active"
    ]
    vm_claims = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/virtualmachineclaims"))]
    kccs = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/kubernetesclusterclaims"))]
    product_plans = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/productplans"))]
    subscriptions = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/subscriptions"))]
    orders = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/orders"))]
    volumes = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/volumes"))]
    networks = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/networks"))]
    firewall_rules = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/firewallrules"))]
    backup_plans = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/backupplans"))]
    access_grants = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/accessgrants"))]
    images = [compact(x) for x in items(client.get(f"/apis/{GROUP}/{VERSION}/images"))]
    nodes = [compact_node(x) for x in items(client.get("/api/v1/nodes"))]
    pods = limited_items(client, "/api/v1/pods", SUMMARY_POD_LIST_LIMIT)
    events = optional_summary_items(
        "events",
        lambda: [event_summary(x) for x in limited_items(client, "/api/v1/events", SUMMARY_EVENT_LIST_LIMIT)],
    )
    audit_events = optional_summary_items("audit-events", lambda: list_audit_events(client))
    admission_journals = optional_summary_items("admission-journals", lambda: list_admission_journals(client))
    non_running = [
        {
            "namespace": x.get("metadata", {}).get("namespace"),
            "name": x.get("metadata", {}).get("name"),
            "phase": x.get("status", {}).get("phase"),
        }
        for x in pods
        if x.get("status", {}).get("phase") not in ("Running", "Succeeded")
    ]
    health = {
        "ready": all(p.get("status", {}).get("phase") == "Ready" for p in projects)
        and all(c.get("status", {}).get("phase") == "Ready" for c in cells)
        and not non_running,
        "nonRunningPods": len(non_running),
        "writeEnabled": WRITE_ENABLED,
        "writeAuthMode": WRITE_AUTH_MODE,
        "writeAuthRequired": WRITE_AUTH_MODE not in ("disabled", "none", "off"),
        "writeAuthIssuer": JWT_ISSUER if WRITE_AUTH_MODE in JWT_AUTH_MODES else "",
        "writeAuthAudience": JWT_AUDIENCE if WRITE_AUTH_MODE in JWT_AUTH_MODES else "",
        "writeAuthGroupsClaim": JWT_GROUPS_CLAIM if WRITE_AUTH_MODE in JWT_AUTH_MODES else "",
        "writeAuthNamespacesClaim": JWT_NAMESPACES_CLAIM if WRITE_AUTH_MODE in JWT_AUTH_MODES else "",
        "writeAuthJwksUri": JWT_JWKS_URI if WRITE_AUTH_MODE == "oidc-jwks" else "",
        "writeAuthAllowedAlgorithms": sorted(JWT_ALLOWED_ALGORITHMS) if WRITE_AUTH_MODE in JWT_AUTH_MODES else [],
        "writeAuthHs256Configured": bool(JWT_HS256_SECRET) if WRITE_AUTH_MODE in JWT_AUTH_MODES else False,
        "writeRateLimit": WRITE_RATE_LIMITER.health(),
    }
    return {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "health": health,
        "projects": projects,
        "capacityCells": cells,
        "capacityReservations": reservations,
        "productPlans": product_plans,
        "subscriptions": subscriptions,
        "orders": orders,
        "vmClaims": vm_claims,
        "kubernetesClusterClaims": kccs,
        "volumes": volumes,
        "networks": networks,
        "firewallRules": firewall_rules,
        "backupPlans": backup_plans,
        "accessGrants": access_grants,
        "images": images,
        "nodes": nodes,
        "nonRunningPods": non_running,
        "events": sorted(events, key=lambda x: x.get("lastTimestamp") or "", reverse=True)[:SUMMARY_MAX_EVENTS],
        "auditEvents": sorted(
            audit_events,
            key=lambda x: (x.get("timestamp") or "", x.get("name") or ""),
            reverse=True,
        )[:SUMMARY_MAX_AUDIT_EVENTS],
        "admissionJournals": sorted(
            admission_journals,
            key=lambda x: x.get("observedAt") or "",
            reverse=True,
        )[:SUMMARY_MAX_ADMISSION_JOURNALS],
    }


def metric_inc(bucket, key, value=1):
    with METRICS_LOCK:
        bucket_obj = METRICS[bucket]
        bucket_obj[key] = bucket_obj.get(key, 0) + value


def metric_observe_refresh(seconds):
    with METRICS_LOCK:
        METRICS["summary_refresh_seconds_sum"] += seconds
        METRICS["summary_refresh_seconds_count"] += 1


def cached_payload(payload, age_seconds, mode, stale, error=None):
    data = copy.deepcopy(payload)
    data["cache"] = {
        "mode": mode,
        "stale": stale,
        "ageSeconds": round(age_seconds, 3),
        "ttlSeconds": SUMMARY_CACHE_TTL_SECONDS,
        "staleSeconds": SUMMARY_CACHE_STALE_SECONDS,
    }
    if error:
        data["cache"]["lastError"] = str(error)[:240]
        data.setdefault("health", {})["ready"] = False
        data["health"]["cacheStale"] = True
    return data


ETAG_IGNORED_KEYS = {
    "cache",
    "events",
    "generatedAt",
    "lastHeartbeatTime",
    "expiresAt",
    "lastTransitionTime",
}


def normalize_for_etag(value):
    if isinstance(value, dict):
        return {
            key: normalize_for_etag(item)
            for key, item in sorted(value.items())
            if key not in ETAG_IGNORED_KEYS
        }
    if isinstance(value, list):
        return [normalize_for_etag(item) for item in value]
    return value


def summary_etag(payload):
    body = json.dumps(normalize_for_etag(payload), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return 'W/"sha256:%s"' % hashlib.sha256(body).hexdigest()


def json_body_size(payload):
    return len(json.dumps(payload, separators=(",", ":")).encode("utf-8"))


def etag_matches(header, etag):
    if not header:
        return False
    current = etag[2:] if etag.startswith("W/") else etag
    for item in header.split(","):
        candidate = item.strip()
        if candidate == "*":
            return True
        if candidate.startswith("W/"):
            candidate = candidate[2:]
        if candidate == current:
            return True
    return False


def summary_cache_control():
    ttl = max(0, int(SUMMARY_CACHE_TTL_SECONDS))
    stale = max(0, int(SUMMARY_CACHE_STALE_SECONDS))
    return f"private, max-age={ttl}, stale-if-error={stale}"


def summary_response_headers(etag):
    return {
        "Cache-Control": summary_cache_control(),
        "ETag": etag,
        "Vary": "Authorization",
        "X-Content-Type-Options": "nosniff",
    }


class SummaryCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.refresh_lock = threading.Lock()
        self.payload = None
        self.refreshed_at = 0.0
        self.last_error = None

    def invalidate(self):
        with self.lock:
            if self.payload is None:
                self.refreshed_at = 0.0
            else:
                self.refreshed_at = time.monotonic() - SUMMARY_CACHE_TTL_SECONDS - 0.001

    def get(self, client, force=False):
        now = time.monotonic()
        with self.lock:
            payload = self.payload
            refreshed_at = self.refreshed_at
            last_error = self.last_error
        if payload is not None:
            age = now - refreshed_at
            if (not force and age <= SUMMARY_CACHE_TTL_SECONDS) or (
                force and age <= SUMMARY_FORCE_FRESH_GRACE_SECONDS
            ):
                metric_inc("summary_cache", "hit")
                return cached_payload(payload, age, "hit", False)
            acquired = self.refresh_lock.acquire(blocking=False)
            if acquired:
                if force:
                    try:
                        start = time.monotonic()
                        refreshed = build_summary(client)
                        elapsed = time.monotonic() - start
                        metric_observe_refresh(elapsed)
                        with self.lock:
                            self.payload = refreshed
                            self.refreshed_at = time.monotonic()
                            self.last_error = None
                        metric_inc("summary_cache", "miss")
                        return cached_payload(refreshed, 0.0, "miss", False)
                    except Exception as exc:
                        with self.lock:
                            self.last_error = exc
                        with METRICS_LOCK:
                            METRICS["summary_refresh_errors"] += 1
                        if age <= SUMMARY_CACHE_STALE_SECONDS:
                            metric_inc("summary_cache", "stale")
                            return cached_payload(payload, age, "stale", True, exc)
                        raise
                    finally:
                        self.refresh_lock.release()

                def refresh_background():
                    try:
                        start = time.monotonic()
                        refreshed = build_summary(client)
                        elapsed = time.monotonic() - start
                        metric_observe_refresh(elapsed)
                        with self.lock:
                            self.payload = refreshed
                            self.refreshed_at = time.monotonic()
                            self.last_error = None
                    except Exception as exc:
                        with self.lock:
                            self.last_error = exc
                        with METRICS_LOCK:
                            METRICS["summary_refresh_errors"] += 1
                    finally:
                        self.refresh_lock.release()

                threading.Thread(target=refresh_background, daemon=True).start()
            metric_inc("summary_cache", "stale")
            age = time.monotonic() - refreshed_at
            return cached_payload(payload, age, "stale", True, last_error or "summary refresh scheduled")

        acquired = self.refresh_lock.acquire(blocking=False)
        if not acquired:
            if payload is not None:
                age = time.monotonic() - refreshed_at
                metric_inc("summary_cache", "stale")
                return cached_payload(payload, age, "stale", True, last_error or "summary refresh in progress")
            raise TimeoutError("summary refresh is already in progress and no cached payload is available")
        try:
            try:
                start = time.monotonic()
                payload = build_summary(client)
                elapsed = time.monotonic() - start
                metric_observe_refresh(elapsed)
                with self.lock:
                    self.payload = payload
                    self.refreshed_at = time.monotonic()
                    self.last_error = None
                metric_inc("summary_cache", "miss")
                return cached_payload(payload, 0.0, "miss", False)
            except Exception as exc:
                with self.lock:
                    self.last_error = exc
                    payload = self.payload
                    refreshed_at = self.refreshed_at
                with METRICS_LOCK:
                    METRICS["summary_refresh_errors"] += 1
                if payload is not None:
                    age = time.monotonic() - refreshed_at
                    if age <= SUMMARY_CACHE_STALE_SECONDS:
                        metric_inc("summary_cache", "stale")
                        return cached_payload(payload, age, "stale", True, exc)
                raise
        finally:
            if acquired:
                self.refresh_lock.release()


SUMMARY_CACHE = SummaryCache()


class AuthError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


class RateLimitError(Exception):
    def __init__(self, retry_after_seconds):
        super().__init__("write rate limit exceeded")
        self.retry_after_seconds = max(1, int(retry_after_seconds))


class RateLimitBackendError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class LocalWriteRateLimiter:
    def __init__(self, window_seconds, max_requests):
        self.window_seconds = max(0.0, float(window_seconds))
        self.max_requests = max(0, int(max_requests))
        self.scope = "local"
        self.lock = threading.Lock()
        self.requests = {}

    def enabled(self):
        return self.window_seconds > 0 and self.max_requests > 0

    def health(self):
        return {
            "enabled": self.enabled(),
            "windowSeconds": self.window_seconds,
            "maxRequests": self.max_requests,
            "scope": self.scope,
        }

    def check(self, client, principal, namespace):
        if not self.enabled():
            return
        subject = principal.get("subject") or "unknown"
        key = f"{namespace}|{subject}"
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self.lock:
            timestamps = [item for item in self.requests.get(key, []) if item > cutoff]
            if len(timestamps) >= self.max_requests:
                retry_after = self.window_seconds - (now - min(timestamps))
                self.requests[key] = timestamps
                raise RateLimitError(retry_after)
            timestamps.append(now)
            self.requests[key] = timestamps


class SharedLeaseWriteRateLimiter:
    def __init__(self, window_seconds, max_requests, namespace, name_prefix):
        self.window_seconds = max(0.0, float(window_seconds))
        self.max_requests = max(0, int(max_requests))
        self.namespace = namespace
        self.name_prefix = name_prefix
        self.scope = "shared"
        self.max_retries = 8

    def enabled(self):
        return self.window_seconds > 0 and self.max_requests > 0

    def health(self):
        return {
            "enabled": self.enabled(),
            "windowSeconds": self.window_seconds,
            "maxRequests": self.max_requests,
            "scope": self.scope,
            "backend": "kubernetes-lease",
            "namespace": self.namespace,
        }

    def lease_name(self, namespace, subject):
        key = f"{namespace}|{subject}"
        digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]
        return dns_label_name(f"{self.name_prefix}-{namespace}-{digest}")

    def lease_timestamp(self, now):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(now)) + ".000000Z"

    def lease_annotations(self, namespace, subject, window_start, count):
        key = f"{namespace}|{subject}"
        return {
            "platform.privatecloud.local/rate-limit-key-hash": hashlib.sha1(key.encode("utf-8")).hexdigest(),
            "platform.privatecloud.local/rate-limit-tenant-namespace": namespace,
            "platform.privatecloud.local/rate-limit-subject": subject[:200],
            "platform.privatecloud.local/rate-limit-window-start": f"{window_start:.6f}",
            "platform.privatecloud.local/rate-limit-count": str(int(count)),
        }

    def lease_spec(self, now):
        return {
            "holderIdentity": "provider-portal-shared-write-rate-limit",
            "leaseDurationSeconds": max(1, int(self.window_seconds * 2) or 1),
            "renewTime": self.lease_timestamp(now),
        }

    def lease_body(self, name, namespace, subject, window_start, count, now):
        return {
            "apiVersion": "coordination.k8s.io/v1",
            "kind": "Lease",
            "metadata": {
                "name": name,
                "namespace": self.namespace,
                "labels": {
                    "app": "provider-portal",
                    "platform.privatecloud.local/write-rate-limit": "true",
                    "platform.privatecloud.local/tenant-namespace": namespace,
                },
                "annotations": self.lease_annotations(namespace, subject, window_start, count),
            },
            "spec": self.lease_spec(now),
        }

    def rate_decision(self, annotations, now):
        try:
            window_start = float(annotations.get("platform.privatecloud.local/rate-limit-window-start", "0") or "0")
        except ValueError:
            window_start = 0.0
        try:
            count = int(annotations.get("platform.privatecloud.local/rate-limit-count", "0") or "0")
        except ValueError:
            count = 0
        if window_start <= 0 or window_start > now + self.window_seconds or now - window_start >= self.window_seconds:
            return now, 1, None
        if count >= self.max_requests:
            return window_start, count, self.window_seconds - (now - window_start)
        return window_start, count + 1, None

    def check(self, client, principal, namespace):
        if not self.enabled():
            return
        subject = principal.get("subject") or "unknown"
        name = self.lease_name(namespace, subject)
        for attempt in range(self.max_retries):
            now = time.time()
            try:
                lease = client.get_namespaced_lease(self.namespace, name)
            except urllib.error.HTTPError as exc:
                if exc.code != 404:
                    raise RateLimitBackendError(f"shared write rate limit lease read failed with HTTP {exc.code}")
                body = self.lease_body(name, namespace, subject, now, 1, now)
                try:
                    client.create_namespaced_lease(self.namespace, body)
                    return
                except urllib.error.HTTPError as create_exc:
                    if create_exc.code == 409:
                        time.sleep(0.02 * (attempt + 1))
                        continue
                    raise RateLimitBackendError(
                        f"shared write rate limit lease create failed with HTTP {create_exc.code}"
                    )

            metadata = lease.setdefault("metadata", {})
            annotations = metadata.setdefault("annotations", {})
            window_start, count, retry_after = self.rate_decision(annotations, now)
            if retry_after is not None:
                raise RateLimitError(retry_after)
            annotations.update(self.lease_annotations(namespace, subject, window_start, count))
            labels = metadata.setdefault("labels", {})
            labels.update(
                {
                    "app": "provider-portal",
                    "platform.privatecloud.local/write-rate-limit": "true",
                    "platform.privatecloud.local/tenant-namespace": namespace,
                }
            )
            lease["spec"] = self.lease_spec(now)
            try:
                client.replace_namespaced_lease(self.namespace, name, lease)
                return
            except urllib.error.HTTPError as update_exc:
                if update_exc.code == 409:
                    time.sleep(0.02 * (attempt + 1))
                    continue
                raise RateLimitBackendError(
                    f"shared write rate limit lease update failed with HTTP {update_exc.code}"
                )
        raise RateLimitBackendError("shared write rate limit lease update conflicted too many times")


def build_write_rate_limiter():
    if WRITE_RATE_LIMIT_SCOPE in ("shared", "global", "lease", "leases"):
        return SharedLeaseWriteRateLimiter(
            WRITE_RATE_LIMIT_WINDOW_SECONDS,
            WRITE_RATE_LIMIT_MAX_REQUESTS,
            WRITE_RATE_LIMIT_NAMESPACE,
            WRITE_RATE_LIMIT_LEASE_PREFIX,
        )
    return LocalWriteRateLimiter(WRITE_RATE_LIMIT_WINDOW_SECONDS, WRITE_RATE_LIMIT_MAX_REQUESTS)


WRITE_RATE_LIMITER = build_write_rate_limiter()


def static_principal_from_token(token):
    if not token:
        raise AuthError(401, "missing bearer token")
    record = STATIC_WRITE_TOKENS.get(token)
    if not isinstance(record, dict):
        raise AuthError(401, "invalid bearer token")
    groups = record.get("groups", [])
    namespaces = record.get("namespaces", [])
    if not isinstance(groups, list) or not isinstance(namespaces, list):
        raise AuthError(401, "invalid token principal")
    return {
        "subject": str(record.get("subject") or "static-token"),
        "groups": {str(group) for group in groups},
        "namespaces": {str(namespace) for namespace in namespaces},
    }


def jwt_b64decode(segment):
    try:
        padding = "=" * (-len(segment) % 4)
        return base64.urlsafe_b64decode((segment + padding).encode("ascii"))
    except Exception as exc:
        raise AuthError(401, "invalid bearer token") from exc


def jwt_json_segment(segment):
    try:
        value = json.loads(jwt_b64decode(segment).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuthError(401, "invalid bearer token") from exc
    if not isinstance(value, dict):
        raise AuthError(401, "invalid bearer token")
    return value


def jwt_claim_strings(value, claim_name):
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        result = set()
        for item in value:
            if not isinstance(item, str) or not item:
                raise AuthError(401, f"invalid jwt {claim_name} claim")
            result.add(item)
        return result
    raise AuthError(401, f"invalid jwt {claim_name} claim")


def jwt_number_claim(payload, name):
    value = payload.get(name)
    if value is None:
        return None
    if isinstance(value, bool):
        raise AuthError(401, f"invalid jwt {name} claim")
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise AuthError(401, f"invalid jwt {name} claim") from exc


def jwt_audience_matches(audience):
    if not JWT_AUDIENCE:
        return True
    if isinstance(audience, str):
        return audience == JWT_AUDIENCE
    if isinstance(audience, list):
        return JWT_AUDIENCE in audience
    return False


RSA_SHA256_DIGESTINFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


def jwt_b64decode_text(segment):
    try:
        return jwt_b64decode(segment).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuthError(401, "invalid bearer token") from exc


def jwt_jwk_int(value, name):
    if not isinstance(value, str) or not value:
        raise AuthError(503, f"invalid jwks {name}")
    number = int.from_bytes(jwt_b64decode(value), "big")
    if number <= 0:
        raise AuthError(503, f"invalid jwks {name}")
    return number


def load_inline_jwks():
    try:
        payload = json.loads(JWT_JWKS_JSON or "{}")
    except json.JSONDecodeError as exc:
        raise AuthError(503, "invalid inline jwks") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list) or not payload["keys"]:
        raise AuthError(503, "inline jwks is not configured")
    return payload


def public_jwks_payload():
    payload = load_inline_jwks()
    public_keys = []
    for key in payload.get("keys", []):
        if not isinstance(key, dict):
            continue
        public_key = {
            field: key[field]
            for field in ("kty", "use", "kid", "alg", "n", "e", "crv", "x", "y", "x5c", "x5t", "x5t#S256")
            if field in key
        }
        if public_key:
            public_keys.append(public_key)
    if not public_keys:
        raise AuthError(503, "inline jwks has no public keys")
    return {"keys": public_keys}


class JwksCache:
    def __init__(self):
        self.lock = threading.Lock()
        self.expires_at = 0.0
        self.payload = None

    def get(self):
        now = time.time()
        with self.lock:
            if self.payload is not None and now < self.expires_at:
                return self.payload
        payload = self.fetch()
        with self.lock:
            self.payload = payload
            self.expires_at = now + max(1.0, JWT_JWKS_CACHE_TTL_SECONDS)
        return payload

    def fetch(self):
        if JWT_JWKS_URI:
            request = urllib.request.Request(JWT_JWKS_URI, headers={"Accept": "application/json"})
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except (urllib.error.URLError, OSError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise AuthError(503, "jwks fetch failed") from exc
        else:
            payload = load_inline_jwks()
        if not isinstance(payload, dict) or not isinstance(payload.get("keys"), list) or not payload["keys"]:
            raise AuthError(503, "jwks is not configured")
        return payload

    def select_key(self, header):
        alg = header.get("alg")
        kid = header.get("kid")
        keys = self.get().get("keys", [])
        matches = []
        for key in keys:
            if not isinstance(key, dict):
                continue
            if key.get("kty") != "RSA":
                continue
            if key.get("use") not in (None, "sig"):
                continue
            if key.get("alg") not in (None, alg):
                continue
            if kid and key.get("kid") != kid:
                continue
            if "n" not in key or "e" not in key:
                continue
            matches.append(key)
        if not matches:
            raise AuthError(401, "jwt signing key not found")
        return matches[0]


JWKS_CACHE = JwksCache()


def verify_hs256_signature(signing_input, signature):
    if not JWT_HS256_SECRET:
        raise AuthError(503, "HS256 write authentication is not configured")
    expected = hmac.new(JWT_HS256_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise AuthError(401, "invalid bearer token")


def verify_rs256_signature(header, signing_input, signature):
    key = JWKS_CACHE.select_key(header)
    n = jwt_jwk_int(key.get("n"), "n")
    e = jwt_jwk_int(key.get("e"), "e")
    key_bytes = (n.bit_length() + 7) // 8
    if len(signature) != key_bytes:
        raise AuthError(401, "invalid bearer token")
    digest = hashlib.sha256(signing_input).digest()
    padding_len = key_bytes - len(RSA_SHA256_DIGESTINFO_PREFIX) - len(digest) - 3
    if padding_len < 8:
        raise AuthError(503, "jwks rsa key is too small")
    encoded = pow(int.from_bytes(signature, "big"), e, n).to_bytes(key_bytes, "big")
    expected = (
        b"\x00\x01"
        + (b"\xff" * padding_len)
        + b"\x00"
        + RSA_SHA256_DIGESTINFO_PREFIX
        + digest
    )
    if not hmac.compare_digest(encoded, expected):
        raise AuthError(401, "invalid bearer token")


def jwt_principal_from_token(token):
    if not token:
        raise AuthError(401, "missing bearer token")
    parts = token.split(".")
    if len(parts) != 3 or not all(parts):
        raise AuthError(401, "invalid bearer token")
    header = jwt_json_segment(parts[0])
    payload = jwt_json_segment(parts[1])
    alg = header.get("alg")
    if alg not in JWT_ALLOWED_ALGORITHMS:
        raise AuthError(401, "unsupported jwt signing algorithm")
    signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")
    signature = jwt_b64decode(parts[2])
    if alg == "HS256":
        verify_hs256_signature(signing_input, signature)
    elif alg == "RS256":
        verify_rs256_signature(header, signing_input, signature)
    else:
        raise AuthError(401, "unsupported jwt signing algorithm")

    if JWT_ISSUER and payload.get("iss") != JWT_ISSUER:
        raise AuthError(401, "invalid jwt issuer")
    if not jwt_audience_matches(payload.get("aud")):
        raise AuthError(401, "invalid jwt audience")
    now = time.time()
    skew = max(0, JWT_CLOCK_SKEW_SECONDS)
    exp = jwt_number_claim(payload, "exp")
    if exp is None:
        raise AuthError(401, "missing jwt exp claim")
    if exp + skew < now:
        raise AuthError(401, "expired bearer token")
    nbf = jwt_number_claim(payload, "nbf")
    if nbf is not None and nbf - skew > now:
        raise AuthError(401, "jwt not valid yet")
    iat = jwt_number_claim(payload, "iat")
    if iat is not None and iat - skew > now:
        raise AuthError(401, "jwt issued in the future")

    subject = payload.get(JWT_SUBJECT_CLAIM) or payload.get("preferred_username") or payload.get("email")
    if not isinstance(subject, str) or not subject:
        raise AuthError(401, "missing jwt subject")
    groups = jwt_claim_strings(payload.get(JWT_GROUPS_CLAIM), JWT_GROUPS_CLAIM)
    namespaces = jwt_claim_strings(payload.get(JWT_NAMESPACES_CLAIM), JWT_NAMESPACES_CLAIM)
    return {
        "subject": subject,
        "groups": groups,
        "namespaces": namespaces,
        "issuer": payload.get("iss", ""),
        "authMode": WRITE_AUTH_MODE,
    }


def project_admin_group(client, namespace):
    try:
        project = client.get(f"/apis/{GROUP}/{VERSION}/projects/{namespace}")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise AuthError(403, f"namespace {namespace} is not a project") from exc
        raise
    spec = project.get("spec", {})
    project_name = project.get("metadata", {}).get("name") or namespace
    tenant_namespace = spec.get("tenantId") or project_name
    if tenant_namespace != namespace:
        raise AuthError(403, f"project {project_name} is bound to namespace {tenant_namespace}")
    return spec.get("adminsGroup") or TENANT_ADMIN_GROUP_TEMPLATE.format(
        namespace=namespace,
        project=project_name,
    )


def principal_can_write_namespace(client, principal, namespace):
    groups = principal.get("groups", set())
    namespaces = principal.get("namespaces", set())
    if PLATFORM_ADMIN_GROUP in groups:
        return True
    if "*" not in namespaces and namespace not in namespaces:
        return False
    admins_group = project_admin_group(client, namespace)
    fallback_group = TENANT_ADMIN_GROUP_TEMPLATE.format(namespace=namespace, project=namespace)
    return admins_group in groups or fallback_group in groups


def principal_is_platform_admin(principal):
    return PLATFORM_ADMIN_GROUP in principal.get("groups", set())


def audit_timestamp():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def principal_subject(principal):
    if not principal:
        return "anonymous"
    return str(principal.get("subject") or "unknown")


def principal_groups(principal):
    if not principal:
        return []
    return sorted(str(group) for group in principal.get("groups", set()))


def record_self_service_audit(
    client,
    namespace,
    principal,
    action,
    resource,
    resource_name,
    outcome,
    status_code,
    message,
    path,
    project_ref=None,
    audit_namespace=None,
):
    audit_namespace = audit_namespace or namespace
    project_ref = project_ref or namespace
    if not audit_namespace or not DNS_LABEL_RE.match(audit_namespace):
        return
    label_project = project_ref if project_ref and DNS_LABEL_RE.match(project_ref) else audit_namespace
    subject = principal_subject(principal)
    subject_hash = hashlib.sha1(subject.encode("utf-8")).hexdigest()
    labels = {
        "app": "provider-portal",
        "platform.privatecloud.local/audit": "true",
        "platform.privatecloud.local/project": label_project,
        "platform.privatecloud.local/resource": resource,
        "platform.privatecloud.local/action": action,
        "platform.privatecloud.local/outcome": outcome.lower(),
        "platform.privatecloud.local/subject-hash": subject_hash[:12],
    }
    body = {
        "apiVersion": f"{GROUP}/{VERSION}",
        "kind": "SelfServiceAuditEvent",
        "metadata": {
            "generateName": "portal-audit-",
            "namespace": audit_namespace,
            "labels": labels,
        },
        "spec": {
            "projectRef": project_ref,
            "subject": subject,
            "subjectHash": subject_hash,
            "groups": principal_groups(principal),
            "action": action,
            "resource": resource,
            "resourceName": resource_name or "",
            "outcome": outcome,
            "statusCode": int(status_code),
            "message": str(message or "")[:500],
            "source": "provider-portal",
            "requestPath": path,
            "timestamp": audit_timestamp(),
        },
    }
    try:
        client.create_namespaced_custom_object(AUDIT_PLURAL, audit_namespace, body)
    except Exception as exc:
        print(f"failed to record self-service audit event: {exc}", flush=True)


def prometheus_metrics():
    with METRICS_LOCK:
        metrics = copy.deepcopy(METRICS)
    lines = [
        "# HELP provider_portal_summary_requests_total Summary API requests by status and cache mode.",
        "# TYPE provider_portal_summary_requests_total counter",
    ]
    for key, value in sorted(metrics["summary_requests"].items()):
        status, cache_mode = key.split("|", 1)
        lines.append(
            f'provider_portal_summary_requests_total{{status="{status}",cache="{cache_mode}"}} {value}'
        )
    lines.extend(
        [
            "# HELP provider_portal_summary_cache_total Summary cache outcomes.",
            "# TYPE provider_portal_summary_cache_total counter",
        ]
    )
    for mode, value in sorted(metrics["summary_cache"].items()):
        lines.append(f'provider_portal_summary_cache_total{{result="{mode}"}} {value}')
    lines.extend(
        [
            "# HELP provider_portal_summary_response_bytes_total Summary API response body bytes by status and cache mode.",
            "# TYPE provider_portal_summary_response_bytes_total counter",
        ]
    )
    for key, value in sorted(metrics["summary_response_bytes"].items()):
        status, cache_mode = key.split("|", 1)
        lines.append(
            f'provider_portal_summary_response_bytes_total{{status="{status}",cache="{cache_mode}"}} {value}'
        )
    lines.extend(
        [
            "# HELP provider_portal_summary_refresh_errors_total Summary cache refresh errors.",
            "# TYPE provider_portal_summary_refresh_errors_total counter",
            f'provider_portal_summary_refresh_errors_total {metrics["summary_refresh_errors"]}',
            "# HELP provider_portal_summary_refresh_seconds Time spent refreshing provider summary from Kubernetes.",
            "# TYPE provider_portal_summary_refresh_seconds summary",
            f'provider_portal_summary_refresh_seconds_sum {metrics["summary_refresh_seconds_sum"]:.6f}',
            f'provider_portal_summary_refresh_seconds_count {metrics["summary_refresh_seconds_count"]}',
            "# HELP provider_portal_write_requests_total Write API requests by verb, resource, and status.",
            "# TYPE provider_portal_write_requests_total counter",
        ]
    )
    for key, value in sorted(metrics["write_requests"].items()):
        method, resource, status = key.split("|", 2)
        lines.append(
            f'provider_portal_write_requests_total{{method="{method}",resource="{resource}",status="{status}"}} {value}'
        )
    return "\n".join(lines) + "\n"


class Handler(BaseHTTPRequestHandler):
    client = None

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)

    def send_json(self, status, payload, extra_headers=None):
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers = extra_headers or {}
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        if not any(key.lower() == "cache-control" for key in headers):
            self.send_header("Cache-Control", "no-store")
        for key, value in headers.items():
            self.send_header(key, str(value))
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_not_modified(self, etag, extra_headers=None):
        headers = extra_headers or {}
        self.send_response(304)
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", headers.get("Cache-Control", "no-cache"))
        self.send_header("Vary", headers.get("Vary", "Authorization"))
        self.send_header("X-Content-Type-Options", headers.get("X-Content-Type-Options", "nosniff"))
        self.end_headers()

    def send_text(self, status, payload, content_type="text/plain; charset=utf-8"):
        body = payload.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = self.headers.get("Content-Length")
        if length is None:
            raise ValueError("missing request body")
        try:
            size = int(length)
        except ValueError as exc:
            raise ValueError("invalid Content-Length") from exc
        if size < 1 or size > 16384:
            raise ValueError("request body must be between 1 and 16384 bytes")
        raw = self.rfile.read(size)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("request body must be JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def send_kubernetes_error(self, exc):
        try:
            body = json.loads(exc.read().decode("utf-8"))
            message = body.get("message") or body.get("reason") or exc.reason
        except Exception:
            message = exc.reason
        self.send_json(exc.code, {"error": message})

    def bearer_token(self):
        header = self.headers.get("Authorization", "")
        scheme, _, value = header.partition(" ")
        if scheme.lower() != "bearer" or not value.strip():
            return ""
        return value.strip()

    def authenticate_write(self):
        if WRITE_AUTH_MODE in ("disabled", "none", "off"):
            return {"subject": "auth-disabled", "groups": {PLATFORM_ADMIN_GROUP}, "namespaces": {"*"}}
        if WRITE_AUTH_MODE == "static":
            return static_principal_from_token(self.bearer_token())
        elif WRITE_AUTH_MODE in JWT_AUTH_MODES:
            return jwt_principal_from_token(self.bearer_token())
        else:
            raise AuthError(503, f"unsupported write auth mode {WRITE_AUTH_MODE}")

    def authorize_write(self, namespace):
        principal = self.authenticate_write()
        if not principal_can_write_namespace(self.client, principal, namespace):
            subject = principal.get("subject", "caller")
            raise AuthError(403, f"{subject} is not allowed to write namespace {namespace}")
        return principal

    def authorize_platform_admin(self):
        principal = self.authenticate_write()
        if not principal_is_platform_admin(principal):
            subject = principal.get("subject", "caller")
            raise AuthError(403, f"{subject} is not allowed to manage Projects")
        return principal

    def check_write_rate_limit(self, principal, namespace):
        WRITE_RATE_LIMITER.check(self.client, principal, namespace)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        if parsed.path == "/healthz":
            self.send_json(200, {"ok": True})
            return
        if parsed.path == "/metrics":
            self.send_text(200, prometheus_metrics())
            return
        if parsed.path in ("/oidc/jwks.json", "/.well-known/jwks.json"):
            try:
                self.send_json(
                    200,
                    public_jwks_payload(),
                    {"Cache-Control": f"public, max-age={int(max(1.0, JWT_JWKS_CACHE_TTL_SECONDS))}"},
                )
            except AuthError as exc:
                self.send_json(exc.status, {"error": exc.message})
            return
        if parsed.path == "/.well-known/openid-configuration":
            issuer = JWT_ISSUER.rstrip("/")
            jwks_uri = JWT_JWKS_URI or "/oidc/jwks.json"
            self.send_json(
                200,
                {
                    "issuer": JWT_ISSUER,
                    "jwks_uri": jwks_uri if urllib.parse.urlparse(jwks_uri).scheme else f"{issuer}{jwks_uri}",
                    "id_token_signing_alg_values_supported": sorted(JWT_ALLOWED_ALGORITHMS),
                    "response_types_supported": ["token"],
                    "subject_types_supported": ["public"],
                },
                {"Cache-Control": "no-store"},
            )
            return
        if parsed.path == "/api/summary":
            query = urllib.parse.parse_qs(parsed.query)
            force = query.get("fresh", ["0"])[0].lower() in ("1", "true", "yes")
            try:
                payload = SUMMARY_CACHE.get(self.client, force=force)
                cache_mode = payload.get("cache", {}).get("mode", "unknown")
                etag = summary_etag(payload)
                headers = summary_response_headers(etag)
                if etag_matches(self.headers.get("If-None-Match", ""), etag):
                    metric_inc("summary_requests", f"304|{cache_mode}")
                    metric_inc("summary_response_bytes", f"304|{cache_mode}", 0)
                    self.send_not_modified(etag, headers)
                    return
                metric_inc("summary_requests", f"200|{cache_mode}")
                metric_inc("summary_response_bytes", f"200|{cache_mode}", json_body_size(payload))
                self.send_json(200, payload, headers)
            except urllib.error.HTTPError as exc:
                metric_inc("summary_requests", f"{exc.code}|error")
                self.send_json(exc.code, {"error": exc.reason})
            except TimeoutError as exc:
                metric_inc("summary_requests", "503|error")
                self.send_json(503, {"error": str(exc), "retryAfterSeconds": 1}, {"Retry-After": "1"})
            except Exception as exc:
                metric_inc("summary_requests", "500|error")
                self.send_json(500, {"error": str(exc)})
            return
        self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if not WRITE_ENABLED:
            self.send_json(403, {"error": "write API is disabled"})
            return
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path not in WRITE_BUILDERS:
            self.send_json(404, {"error": "not found"})
            return
        plural, builder, scope = WRITE_BUILDERS[parsed.path]
        namespace = ""
        resource_name = ""
        audit_namespace = ""
        audit_project_ref = ""
        principal = None
        try:
            raw_payload = self.read_json()
            resource_name = str(raw_payload.get("name") or "")[:63]
            if scope == "cluster":
                namespace = resource_name
                audit_namespace = PROJECT_AUDIT_NAMESPACE
                audit_project_ref = resource_name
                principal = self.authorize_platform_admin()
                self.check_write_rate_limit(principal, PROJECT_AUDIT_NAMESPACE)
                payload = builder(raw_payload)
                resource_name = payload["metadata"]["name"]
                namespace = resource_name
                audit_project_ref = resource_name
                created = self.client.create_cluster_custom_object(plural, payload)
            else:
                namespace = validate_name(raw_payload.get("namespace"), "namespace")
                audit_namespace = namespace
                audit_project_ref = namespace
                principal = self.authorize_write(namespace)
                self.check_write_rate_limit(principal, namespace)
                payload = builder(raw_payload)
                namespace = payload["metadata"]["namespace"]
                resource_name = payload["metadata"]["name"]
                audit_namespace = namespace
                audit_project_ref = namespace
                created = self.client.create_namespaced_custom_object(plural, namespace, payload)
            SUMMARY_CACHE.invalidate()
            metric_inc("write_requests", f"POST|{plural}|201")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Allowed",
                201,
                "created through provider portal",
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(201, compact(created))
        except ValueError as exc:
            metric_inc("write_requests", f"POST|{plural}|400")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Rejected",
                400,
                str(exc),
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(400, {"error": str(exc)})
        except AuthError as exc:
            metric_inc("write_requests", f"POST|{plural}|{exc.status}")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Rejected",
                exc.status,
                exc.message,
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(exc.status, {"error": exc.message})
        except RateLimitError as exc:
            metric_inc("write_requests", f"POST|{plural}|429")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "RateLimited",
                429,
                "write rate limit exceeded",
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(
                429,
                {
                    "error": "write rate limit exceeded",
                    "retryAfterSeconds": exc.retry_after_seconds,
                },
                {"Retry-After": exc.retry_after_seconds},
            )
        except RateLimitBackendError as exc:
            metric_inc("write_requests", f"POST|{plural}|503")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Error",
                503,
                exc.message,
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(503, {"error": exc.message})
        except urllib.error.HTTPError as exc:
            metric_inc("write_requests", f"POST|{plural}|{exc.code}")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Error",
                exc.code,
                exc.reason,
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_kubernetes_error(exc)
        except Exception as exc:
            metric_inc("write_requests", f"POST|{plural}|500")
            record_self_service_audit(
                self.client,
                audit_namespace or namespace,
                principal,
                "create",
                plural,
                resource_name,
                "Error",
                500,
                str(exc),
                parsed.path,
                project_ref=audit_project_ref or namespace,
                audit_namespace=audit_namespace or namespace,
            )
            self.send_json(500, {"error": str(exc)})

    def do_DELETE(self):
        if not WRITE_ENABLED:
            self.send_json(403, {"error": "write API is disabled"})
            return
        parsed = urllib.parse.urlparse(self.path)
        parts = [urllib.parse.unquote(x) for x in parsed.path.strip("/").split("/")]
        if len(parts) == 4 and parts[0:2] == ["api", "claims"]:
            plural, namespace, name = parts[2], parts[3], parts[3]
        elif len(parts) == 5 and parts[0:2] == ["api", "claims"]:
            plural, namespace, name = parts[2], parts[3], parts[4]
        else:
            self.send_json(404, {"error": "not found"})
            return
        if plural not in DELETE_PLURALS:
            self.send_json(404, {"error": "not found"})
            return
        scope = DELETE_PLURALS[plural]
        audit_namespace = PROJECT_AUDIT_NAMESPACE if scope == "cluster" else namespace
        audit_project_ref = name if scope == "cluster" else namespace
        principal = None
        try:
            namespace = validate_name(namespace, "namespace")
            name = validate_name(name, "name")
            if scope == "cluster":
                if namespace != name:
                    raise ValueError("cluster-scoped delete path must use matching namespace placeholder and name")
                audit_project_ref = name
                principal = self.authorize_platform_admin()
                self.check_write_rate_limit(principal, PROJECT_AUDIT_NAMESPACE)
                deleted = self.client.delete_cluster_custom_object(plural, name)
            else:
                audit_namespace = namespace
                audit_project_ref = namespace
                principal = self.authorize_write(namespace)
                self.check_write_rate_limit(principal, namespace)
                deleted = self.client.delete_namespaced_custom_object(plural, namespace, name)
            SUMMARY_CACHE.invalidate()
            metric_inc("write_requests", f"DELETE|{plural}|200")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Allowed",
                200,
                "deleted through provider portal",
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(200, deleted or {"deleted": True})
        except ValueError as exc:
            metric_inc("write_requests", f"DELETE|{plural}|400")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Rejected",
                400,
                str(exc),
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(400, {"error": str(exc)})
        except AuthError as exc:
            metric_inc("write_requests", f"DELETE|{plural}|{exc.status}")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Rejected",
                exc.status,
                exc.message,
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(exc.status, {"error": exc.message})
        except RateLimitError as exc:
            metric_inc("write_requests", f"DELETE|{plural}|429")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "RateLimited",
                429,
                "write rate limit exceeded",
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(
                429,
                {
                    "error": "write rate limit exceeded",
                    "retryAfterSeconds": exc.retry_after_seconds,
                },
                {"Retry-After": exc.retry_after_seconds},
            )
        except RateLimitBackendError as exc:
            metric_inc("write_requests", f"DELETE|{plural}|503")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Error",
                503,
                exc.message,
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(503, {"error": exc.message})
        except urllib.error.HTTPError as exc:
            metric_inc("write_requests", f"DELETE|{plural}|{exc.code}")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Error",
                exc.code,
                exc.reason,
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_kubernetes_error(exc)
        except Exception as exc:
            metric_inc("write_requests", f"DELETE|{plural}|500")
            record_self_service_audit(
                self.client,
                audit_namespace,
                principal,
                "delete",
                plural,
                name,
                "Error",
                500,
                str(exc),
                parsed.path,
                project_ref=audit_project_ref,
                audit_namespace=audit_namespace,
            )
            self.send_json(500, {"error": str(exc)})


def main():
    Handler.client = KubernetesClient()
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"provider portal listening on :{port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
