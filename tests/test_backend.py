"""Basic tests for backend"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_imports():
    """Test that backend imports work"""
    try:
        from BackEnd.backend import app, Task, CreateTask
        assert app is not None
        assert Task is not None
        assert CreateTask is not None
    except ImportError as e:
        assert False, f"Import failed: {e}"


def test_task_model():
    """Test Task model structure"""
    from BackEnd.backend import CreateTask

    task = CreateTask(original_text="Test task")
    assert task.original_text == "Test task"


def test_fallback_parsing():
    """Test fallback parsing function"""
    from BackEnd.backend import fallback_parsing

    result = fallback_parsing("Buy milk tomorrow, urgent")

    assert "title" in result
    assert "priority" in result
    assert "category" in result
    assert "deadline" in result
    assert result["priority"] == "High"  # Should detect "urgent"


if __name__ == "__main__":
    test_imports()
    test_task_model()
    test_fallback_parsing()
    print("✅ All tests passed!")