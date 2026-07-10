#!/bin/bash

echo "Starting EuclidCam 3D Viewer..."
echo "This viewer automatically bypasses all caches!"

# Start python server in the background
python3 -m http.server 8000 > /dev/null 2>&1 &
SERVER_PID=$!

sleep 1

# Open the viewer in the default browser
open http://localhost:8000/viewer.html

echo "Server running at http://localhost:8000/viewer.html"
echo "Viewer opened in your browser!"
echo "Press Ctrl+C to shut down the server when you are done."

# Wait for Ctrl+C to kill the server
trap "kill $SERVER_PID" INT
wait $SERVER_PID
