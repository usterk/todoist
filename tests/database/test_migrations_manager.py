"""
Tests for database migration management.
"""

import os
import pytest
import logging
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path
from alembic.config import Config

from app.database.migrations_manager import (
    get_alembic_config,
    run_migrations
)

def test_get_alembic_config():
    """Test that get_alembic_config returns a valid Alembic Config object"""
    # Get the config
    config = get_alembic_config()
    
    # Check it's the right type
    assert isinstance(config, Config)
    
    # Check it points to a real file
    config_path = config.config_file_name
    assert os.path.exists(config_path)
    assert os.path.basename(config_path) == "alembic.ini"


@patch('app.database.migrations_manager.command')
def test_run_migrations_success(mock_command):
    """Test that run_migrations calls the command.upgrade function with correct parameters"""
    # Set up mock
    mock_command.upgrade = MagicMock()
    
    # Call the function
    run_migrations()
    
    # Check that upgrade was called with right parameters
    mock_command.upgrade.assert_called_once()
    args, kwargs = mock_command.upgrade.call_args
    assert args[1] == "head"  # Second argument should be "head"
    assert isinstance(args[0], Config)  # First argument should be a Config object


@patch('app.database.migrations_manager.command')
def test_run_migrations_creates_data_directory(mock_command):
    """Test that run_migrations creates the data directory if it doesn't exist"""
    # Use a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_data_dir = os.path.join(temp_dir, "test_data")
        
        # Set environment variable to temp directory
        old_data_dir = os.environ.get('DATA_DIRECTORY')
        os.environ['DATA_DIRECTORY'] = test_data_dir
        
        try:
            # Call the function
            run_migrations()
            
            # Check that directory was created
            assert os.path.exists(test_data_dir)
        finally:
            # Restore original environment variable
            if old_data_dir:
                os.environ['DATA_DIRECTORY'] = old_data_dir
            else:
                del os.environ['DATA_DIRECTORY']


@patch('app.database.migrations_manager.command')
@patch('app.database.migrations_manager.logger')
def test_run_migrations_logs_info(mock_logger, mock_command):
    """Test that run_migrations logs appropriate info messages"""
    # Call function
    run_migrations()
    
    # Check start and completion logs
    assert mock_logger.info.call_count >= 2
    mock_logger.info.assert_any_call("Running database migrations...")
    mock_logger.info.assert_any_call("Database migrations completed successfully.")


@patch('app.database.migrations_manager.command')
@patch('app.database.migrations_manager.logger')
def test_run_migrations_error_handling(mock_logger, mock_command):
    """Test that run_migrations handles errors properly"""
    # Make command.upgrade raise an exception
    mock_command.upgrade.side_effect = Exception("Test migration error")
    
    # Call function and assert it raises
    with pytest.raises(Exception, match="Test migration error"):
        run_migrations()
    
    # Check error was logged
    mock_logger.error.assert_called_once()
    assert "Error running database migrations" in mock_logger.error.call_args[0][0]