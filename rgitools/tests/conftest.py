import pytest
from oggm.utils import _downloads
from oggm.tests.conftest import secure_url_retrieve


@pytest.fixture(autouse=True)
def patch_url_retrieve(monkeypatch):
    monkeypatch.setattr(_downloads, 'oggm_urlretrieve', secure_url_retrieve)
