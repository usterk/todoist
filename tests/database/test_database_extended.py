"""
Extended tests for database configuration and connections.
"""

import pytest
import os
import tempfile
from unittest import mock
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.database import get_db, DATABASE_URL, engine, SessionLocal

def test_database_url_format():
    """Test that the database URL is correctly formatted"""
    assert DATABASE_URL.startswith("sqlite:///")

def test_get_db_generator():
    """Test that get_db returns a generator with database session"""
    db_generator = get_db()
    db_session = next(db_generator)
    
    # Verify that we got a database session
    assert isinstance(db_session, Session)
    
    # Close the session
    try:
        next(db_generator)
    except StopIteration:
        pass  # Expected behavior for generator exhaustion

def test_db_session_error_handling():
    """Test error handling in get_db function"""
    # Mock the SessionLocal to raise an exception when called
    with mock.patch('app.database.database.SessionLocal', side_effect=OperationalError("statement", {}, "error")):
        db_generator = get_db()
        
        # The generator should still be created without error
        assert db_generator is not None
        
        # But trying to get a session should raise an error
        with pytest.raises(OperationalError):
            next(db_generator)

def test_engine_connection():
    """Test that the database engine can connect"""
    # Create a temporary database file
    with tempfile.NamedTemporaryFile(suffix='.db') as tmp:
        # Create a test database URL
        test_db_url = f"sqlite:///{tmp.name}"
        
        # Create an engine with the test URL
        with mock.patch('app.database.database.DATABASE_URL', test_db_url):
            from app.database.database import create_engine
            test_engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
            
            # Test connection
            conn = test_engine.connect()
            assert conn is not None
            conn.close()

def test_session_local_creation():
    """Test that SessionLocal can create a session"""
    # Create a new session
    session = SessionLocal()
    
    # Verify that a session was created
    assert session is not None
    
    # Close the session
    session.close()

def test_session_execute():
    """Test that a session can execute SQL statements"""
    # Create a session
    session = SessionLocal()
    
    try:
        # Execute a simple query - używamy text() zamiast bezpośredniego ciągu znaków
        result = session.execute(text("SELECT 1"))
        row = result.fetchone()
        
        # Verify the result
        assert row[0] == 1
    finally:
        # Ensure session is closed
        session.close()

def test_session_commit_and_rollback():
    """Test session commit and rollback operations"""
    # Create a session
    session = SessionLocal()
    
    try:
        # Start a transaction and insert data
        session.execute(text("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)"))
        session.execute(text("INSERT INTO test_table (id) VALUES (1)"))
        
        # Verify the data is in the session before committing
        result = session.execute(text("SELECT COUNT(*) FROM test_table"))
        assert result.scalar() == 1
        
        # Rollback the transaction
        session.rollback()
        
        # Verify the data was rolled back (insertion was undone)
        result = session.execute(text("SELECT COUNT(*) FROM test_table"))
        assert result.scalar() == 0
        
        # Insert again and commit
        session.execute(text("INSERT INTO test_table (id) VALUES (1)"))
        session.commit()
        
        # Verify data persists after commit
        result = session.execute(text("SELECT COUNT(*) FROM test_table"))
        assert result.scalar() == 1
        
        # Clean up
        session.execute(text("DROP TABLE test_table"))
        session.commit()
    finally:
        # Ensure session is closed
        session.close()