#!/usr/bin/env python
"""Main entry point for TalentBeacon™."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from backend.app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from backend.extensions import db
        db.create_all()
        print("[*] Database tables created.")
    print("[*] TalentBeacon starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
