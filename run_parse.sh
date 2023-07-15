#!/bin/bash

# Activate the virtual environment
source /app/.venv/bin/activate

# Run your functions
python /app/belinda_app/services/parse_spotify_playlists.py
python /app/belinda_app/services/parse_spotify_tracks.py
