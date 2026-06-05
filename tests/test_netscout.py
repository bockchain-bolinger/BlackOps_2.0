import sys
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.netscout import NetScoutRunner

@pytest.mark.asyncio
async def test_scan_port_open():
    runner = NetScoutRunner("localhost")
    # Mocking open_connection to simulate an open port
    with patch("asyncio.open_connection", new_callable=AsyncMock) as mock_open:
        # Mocking writer and reader
        mock_writer = AsyncMock()
        mock_open.return_value = (AsyncMock(), mock_writer)
        
        port = await runner._scan_port("127.0.0.1", 80, "HTTP")
        
        assert port == 80
        mock_writer.close.assert_called_once()

@pytest.mark.asyncio
async def test_scan_port_closed():
    runner = NetScoutRunner("localhost")
    # Mocking open_connection to simulate a closed/refused port
    with patch("asyncio.open_connection", side_effect=ConnectionRefusedError):
        port = await runner._scan_port("127.0.0.1", 80, "HTTP")
        
        assert port is None
