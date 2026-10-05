"""Python client for the CDEK API."""

from gocream_pycdek.client import PRODUCTION_API_URL
from gocream_pycdek.client import TEST_API_URL
from gocream_pycdek.client import CdekClient
from gocream_pycdek.client import ContractType


__all__ = [
    "PRODUCTION_API_URL",
    "TEST_API_URL",
    "CdekClient",
    "ContractType",
    "__version__",
]


__version__ = "2.0.0-b.10"
