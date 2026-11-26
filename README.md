# Job Application Tracker

A lightweight command-line application built with Python and SQLite to track, search, update, and summarize job and internship applications.

## Features
- **Add Applications**: Store company name, role, status, application date, and notes.
- **Search & Filter**: Search by keyword (company, role, or notes) or filter by application status.
- **Update & Delete**: Modify application status and notes or remove entries by ID.
- **Summary Dashboard**: View total applications grouped by status using SQL aggregation.
- **Unit Tested**: Core database operations verified with Python's `unittest` framework.

## Tech Stack
- **Language**: Python 3
- **Database**: SQLite (`sqlite3`)
- **Testing**: `unittest`

## Getting Started

### Run the Application
```bash
python tracker.py
