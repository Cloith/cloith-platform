import pytest
import IOError
from unittest.mock import patch, MagicMock, mock_open
import sys

# Import your actual class here
from services.system.instance_manager import InstanceLock

def test_acquire_happy_path():
    """1. Test that we can successfully get a lock if it's free."""
    lock = InstanceLock("/tmp/test_manager.lock")
    
    # Fake the file opening, the fcntl locking, and our process ID
    with patch("builtins.open", mock_open()) as mocked_file, \
         patch("fcntl.flock") as mocked_flock, \
         patch("os.getpid", return_value=9999), \
         patch("os.fsync"):
        
        result = lock.acquire()
        
        # Verify the class returned itself (successful context manager)
        assert result == lock
        # Verify it wrote our fake PID (9999) to the file
        mocked_file().write.assert_called_with("9999")


def test_acquire_active_collision():
    """2. Test that the app safely exits if another process holds the lock."""
    lock = InstanceLock("/tmp/test_manager.lock")
    
    # Mocking open to simulate reading an old PID of '5555'
    # Simulating flock throwing an IOError (meaning file is locked)
    # Simulating os.kill returning None (meaning PID 5555 is alive and healthy)
    with patch("builtins.open", mock_open(read_data="5555")), \
         patch("fcntl.flock", side_effect=IOError("Locked")), \
         patch("os.kill", return_value=None), \
         patch("sys.exit") as mocked_exit:
        
        lock.acquire()
        
        # Assert that the program attempted to exit with status code 1
        mocked_exit.assert_called_once_with(1)


def test_acquire_stale_lock_cleanup():
    """3. Test that a stale lock from a dead process is automatically purged."""
    lock = InstanceLock("/tmp/test_manager.lock")
    
    # First time flock is called, it fails (simulating existing file).
    # Second time flock is called (during recursion), it succeeds!
    mock_flock = MagicMock()
    mock_flock.side_effect = [IOError("Locked"), None]
    
    with patch("builtins.open", mock_open(read_data="8888")), \
         patch("fcntl.flock", mock_flock), \
         patch("os.kill", side_effect=OSError(3, "No such process")), \
         patch("os.path.exists", return_value=True), \
         patch("os.remove") as mocked_remove, \
         patch("os.getpid", return_value=9999), \
         patch("os.fsync"):
        
        result = lock.acquire()
        
        # Verify that the old stale lock file was deleted
        mocked_remove.assert_called_once_with("/tmp/test_manager.lock")
        # Verify we ultimately got the lock instance back
        assert result == lock