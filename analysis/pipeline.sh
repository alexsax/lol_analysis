#!/usr/bin/env bash
# Download
python ../data/download.py
# Processing
python process_match.py

# Generating analysis data
python generate_kill_data.py
python generate_team_data.py
python gen_location_data.py
python generate_match_data.py
python generate_lane_data.py
python first_data.py