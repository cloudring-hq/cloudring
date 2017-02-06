from pathlib import Path
import sys
try:
    import yaml
except Exception as exc:
    print(f"missing yaml module: {exc}", file=sys.stderr)
    sys.exit(2)
path = Path("iac/kubernetes/provider-controller/rendered-controller.yaml")
out = Path("tmp/rendered-controller-embedded.py")
for doc in yaml.safe_load_all(path.read_text(encoding="utf-8-sig")):
    if isinstance(doc, dict) and doc.get("kind") == "ConfigMap" and doc.get("data", {}).get("controller.py"):
        out.parent.mkdir(exist_ok=True)
        out.write_text(doc["data"]["controller.py"], encoding="utf-8")
        print(out)
        sys.exit(0)
print("controller.py ConfigMap entry not found", file=sys.stderr)
sys.exit(1)