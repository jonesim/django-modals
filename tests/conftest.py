import os

import pytest


BASE_URL = "http://localhost:8007"


def _server_is_up():
    import urllib.request
    try:
        urllib.request.urlopen(BASE_URL, timeout=2)
        return True
    except Exception:
        return False


@pytest.fixture(scope="session")
def base_url():
    """Provide the base URL for the running Django dev server."""
    if not _server_is_up():
        pytest.skip("Django dev server is not running on localhost:8007")
    return BASE_URL


@pytest.fixture(scope="session")
def browser_context_args():
    return {"ignore_https_errors": True}
