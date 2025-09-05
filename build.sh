#!/bin/bash

# Render.com build script for FinBuddy

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p instance static/audio uploads data

# Set up database (if needed)
python -c "
try:
    from app import app, db
    with app.app_context():
        db.create_all()
        print('Database tables created successfully!')
except Exception as e:
    print(f'Database setup: {e}')
"

echo "Build completed successfully!"
