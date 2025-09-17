# Scripts Directory

This directory contains development and utility scripts for the Python Auth Face App.

## Scripts

- **`dev.py`** - Development server with auto-reload functionality
- **`migrate.py`** - Database migration CLI (Laravel style)
- **`performance_tuner.py`** - Performance tuning script for face recognition system
- **`improve_face_recognition.py`** - Script to improve face recognition accuracy

## Usage

Run scripts from the project root directory:

```bash
# Development server
python scripts/dev.py

# Database migration
python scripts/migrate.py migrate
python scripts/migrate.py seed
python scripts/migrate.py fresh

# Performance tuning
python scripts/performance_tuner.py benchmark
python scripts/performance_tuner.py compare
python scripts/performance_tuner.py optimize

# Face recognition improvement
python scripts/improve_face_recognition.py
```

## Notes

- All scripts automatically add the project root to the Python path
- Scripts are designed to be run from the project root directory
- Make sure all dependencies are installed before running scripts
