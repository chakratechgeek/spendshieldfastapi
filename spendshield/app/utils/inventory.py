import pkgutil
import importlib
from typing import Iterator, Dict, Any

REGION = "ap-southeast-2"

def fetch_all_resources() -> Iterator[Dict[str, Any]]:
    seen = set()
    # Dynamically discover every module in app.utils.fetchers
    import app.utils.fetchers as fetchers_pkg

    for finder, name, _ in pkgutil.iter_modules(fetchers_pkg.__path__):
        module = importlib.import_module(f"app.utils.fetchers.{name}")
        for item in module.fetch(REGION):
            key = (item["resource_type"], item["resource_id"])
            if key not in seen:
                seen.add(key)
                yield item
