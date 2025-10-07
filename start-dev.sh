#!/bin/bash

# Starta backend
echo "Starting backend server..."
cd backend
python -m src.app &
BACKEND_PID=$!

# Starta frontend
echo "Starting frontend development server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Funktion för att avsluta båda processerna vid stängning
function cleanup {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  exit
}

# Fånga SIGINT (Ctrl+C) och SIGTERM
trap cleanup SIGINT SIGTERM

echo "Both servers are running. Press Ctrl+C to stop."
wait
