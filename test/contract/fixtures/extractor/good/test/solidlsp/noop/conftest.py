"""Ordinary fixtures that must not be classified as bootstrap."""

import pytest


@pytest.fixture
def ordinary_fixture() -> str:
    return "ready"
