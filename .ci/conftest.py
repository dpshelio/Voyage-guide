from testfixtures import TempDirectory
import pytest

@pytest.fixture()
def dir():
    with TempDirectory() as dir:
        yield dir
