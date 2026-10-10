"""
SURF — Root Launcher for Local Execution and Testing
"""
import sys
import os
from pathlib import Path
import importlib.util

# Add SURF and SURF/backend to sys.path
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "backend"
backend_api_file = backend_dir / "api.py"

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Explicit spec loader ensures 100% reliability across virtual filesystems
spec = importlib.util.spec_from_file_location("api", str(backend_api_file))
api_module = importlib.util.module_from_spec(spec)
sys.modules["api"] = api_module
sys.modules["backend.api"] = api_module
spec.loader.exec_module(api_module)
app = api_module.app

if __name__ == "__main__":
    import uvicorn
    print("Launching SURF Satellite Urban Climate Intelligence Platform on http://localhost:8000 ...")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
