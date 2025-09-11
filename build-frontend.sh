#!/bin/bash
# Build script for frontend deployment to Render

echo "Installing frontend dependencies..."
cd frontend
npm install

echo "Building React app..."
npm run build

echo "Frontend build complete!"
echo "Build files are in frontend/build/"
