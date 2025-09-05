#!/bin/bash

# Render.com start script for FinBuddy

# Create necessary directories if they don't exist
mkdir -p instance static/audio uploads data

# Start the application with Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --max-requests 1000 app:app
