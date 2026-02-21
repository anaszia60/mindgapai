#!/bin/bash

# Kill background processes on exit
trap "kill 0" EXIT

echo "Starting MindGap AI Backend..."
cd backend
source venv/bin/activate
python app.py &

echo "Starting MindGap AI Frontend..."
cd ../frontend
npm run dev &

wait
