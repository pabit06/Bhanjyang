import pytest
import sys
from unittest.mock import MagicMock

# Create a mock for pyclamd
mock_pyclamd = MagicMock()
mock_pyclamd.ClamdUnixSocket.return_value.scan_file.return_value = None  # None means no virus
mock_pyclamd.ClamdUnixSocket.return_value.scan_stream.return_value = None
mock_pyclamd.ClamdNetworkSocket.return_value.scan_file.return_value = None
mock_pyclamd.ClamdNetworkSocket.return_value.scan_stream.return_value = None

# Register it in sys.modules
sys.modules['pyclamd'] = mock_pyclamd
