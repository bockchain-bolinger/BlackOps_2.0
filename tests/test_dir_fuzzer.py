import sys
import os
import pytest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.dir_fuzzer import DirFuzzer

@pytest.mark.asyncio
async def test_fuzzer_found_path():
    fuzzer = DirFuzzer()
    
    mock_response = AsyncMock()
    mock_response.status = 200
    
    mock_session = AsyncMock()
    # Correct mock for async context manager session.get()
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.__aenter__.return_value = mock_response
    mock_session.get.return_value = mock_response
    
    with patch("src.modules.dir_fuzzer.print") as mock_print:
        await fuzzer._check_path(mock_session, "http://test.com", "admin")
        
        # DEBUG: Print what was actually called
        print(f"DEBUG: mock_print.call_args_list: {mock_print.call_args_list}")
        
        # Verify the print for found path was called
        # Check if any call contains the expected string
        found = False
        for call in mock_print.call_args_list:
            if "[+] Found: http://test.com/admin (200)" in call[0][0]:
                found = True
                break
        assert found

@pytest.mark.asyncio
async def test_fuzzer_not_found_path():
    fuzzer = DirFuzzer()
    
    mock_response = AsyncMock()
    mock_response.status = 404
    
    mock_session = AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response
    
    with patch("src.modules.dir_fuzzer.print") as mock_print:
        await fuzzer._check_path(mock_session, "http://test.com", "admin")
        
        # Verify the print for found path was NOT called
        for call in mock_print.call_args_list:
            assert "[+] Found: http://test.com/admin" not in call[0][0]
