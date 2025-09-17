# Tests Directory

This directory contains test files for the Python Auth Face App.

## Test Files

- **`test_simple.py`** - Basic UI test without database
- **`test_compound_names.py`** - Test compound name matching for face recognition
- **`test_db_connection.py`** - Database connection and service tests

## Usage

Run tests from the project root directory:

```bash
# Basic UI test
python tests/test_simple.py

# Compound name matching test
python tests/test_compound_names.py

# Database connection test
python tests/test_db_connection.py
```

## Test Categories

### Unit Tests

- `test_simple.py` - Tests basic UI functionality
- `test_compound_names.py` - Tests face recognition name matching

### Integration Tests

- `test_db_connection.py` - Tests database connectivity and services

## Notes

- All tests automatically add the project root to the Python path
- Tests are designed to be run from the project root directory
- Database tests require a running MySQL instance
- Some tests may require camera access for face recognition testing
