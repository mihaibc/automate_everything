import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def load_script():
    def _load_script(relative_path: str):
        path = REPO_ROOT / relative_path
        module_name = relative_path.replace("/", "_").replace(".", "_").replace("+", "plus")
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(module)
        return module

    return _load_script


def load_module(relative_path: str):
    path = REPO_ROOT / relative_path
    module_name = relative_path.replace("/", "_").replace(".", "_").replace("+", "plus")
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module
