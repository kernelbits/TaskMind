"""Basic tests for backend"""
import sys
import os

sys.path.insert(0, os.path.abspath(os. path.join(os. path.dirname(__file__), '..')))

def test_imports():
    """Test that backend imports work"""
    try:
        from BackEnd.backend import app, Task, CreateTask
        assert app is not None
        print("✅ Backend imports successful")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        raise

def test_fallback_parsing():
    """Test fallback parsing function"""
    from BackEnd.backend import fallback_parsing

    result = fallback_parsing("Buy milk tomorrow, urgent")

    assert "title" in result
    assert "priority" in result
    assert result["priority"] == "High"
    print("✅ Fallback parsing works")

if __name__ == "__main__":
    test_imports()
    test_fallback_parsing()
    print("✅ All tests passed!")