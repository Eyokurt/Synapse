import pytest
from synapse.tools.builtin.web_search import search_web

def test_search_web():
    results = search_web("Python programming", max_results=2)
    assert isinstance(results, str)
    assert "http" in results.lower()
    assert "Title: " in results
