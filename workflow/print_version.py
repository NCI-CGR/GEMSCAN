import sys
from pathlib import Path

path = Path("../pyproject.toml")
if not path.exists():
    print("pyproject.toml not found", file=sys.stderr)
    sys.exit(1)

data = None
try:
    # Python 3.11+
    import tomllib as toml_loader
except Exception:
    try:
        import tomli as toml_loader  # pip install tomli for Py<=3.10
    except Exception:
        print("tomli/tomllib required", file=sys.stderr)
        sys.exit(1)

with path.open("rb") as f:
    data = toml_loader.load(f)

# Try common locations for version
version = None
if "project" in data and isinstance(data["project"], dict):
    version = data["project"].get("version")
if not version and "tool" in data and "poetry" in data["tool"]:
    version = data["tool"]["poetry"].get("version")

if version:
    print("###################")
    print(f"PACKAGE_VERSION={version}")
    print("###################")
else:
    print("###################")
    print("version not found in pyproject.toml", file=sys.stderr)
    print("###################")
    sys.exit(2)

