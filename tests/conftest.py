import os
import pytest

# Automatically apply test ENV for all tests
@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["ENV"] = "dev"