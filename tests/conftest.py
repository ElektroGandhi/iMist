"""Load the pure modules of the integration without Home Assistant installed.

protocol.py and schedule.py only depend on const.py; device.py needs two Bluetooth
libraries, which are replaced by stubs here. Everything else needs a running HA
and is covered by the hassfest/HACS checks in CI.
"""
import importlib.util
import sys
import types
from pathlib import Path

PKG = Path(__file__).resolve().parents[1] / "custom_components" / "imist"

for name in ("bleak", "bleak.backends", "bleak.backends.device"):
    sys.modules.setdefault(name, types.ModuleType(name))
sys.modules["bleak.backends.device"].BLEDevice = object
_brc = sys.modules.setdefault("bleak_retry_connector", types.ModuleType("bleak_retry_connector"))
_brc.BleakClientWithServiceCache = object
_brc.establish_connection = None

_pkg = types.ModuleType("imist")
_pkg.__path__ = [str(PKG)]
sys.modules["imist"] = _pkg
for _name in ("const", "protocol", "schedule", "device"):
    _spec = importlib.util.spec_from_file_location(f"imist.{_name}", PKG / f"{_name}.py")
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[f"imist.{_name}"] = _mod
    _spec.loader.exec_module(_mod)
