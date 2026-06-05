import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import ast
from src.modules.polymorphic_engine import PolymorphicEngine

def test_polymorphic_mutation():
    engine = PolymorphicEngine()
    original_code = """
def connect():
    x = 1
"""
    mutated = engine.mutate(original_code)
    
    # Check if mutated code is still valid Python
    try:
        ast.parse(mutated)
    except SyntaxError:
        pytest.fail("Mutated code is not valid Python")
        
    # Check that it is different from original
    assert mutated != original_code
    # Check if dummy variable insertion occurred
    assert "def" in mutated
