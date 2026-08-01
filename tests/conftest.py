from pathlib import Path

import pytest


@pytest.fixture
def python_complex_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "python_complex"


@pytest.fixture
def python_complex_cyclic_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "python_complex_cyclic"


@pytest.fixture
def js_complex_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "js_complex"


@pytest.fixture
def js_complex_cyclic_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "js_complex_cyclic"


@pytest.fixture
def cpp_complex_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "cpp_complex"


@pytest.fixture
def cpp_complex_cyclic_dir() -> Path:
    return Path(__file__).parent / "fixtures" / "cpp_complex_cyclic"
