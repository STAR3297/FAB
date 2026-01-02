#!/bin/bash
# Cleanup script for Linux/Mac
# Removes unnecessary files and cache directories

echo "Cleaning up project files..."

# Remove Python cache
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete

# Remove virtual environment (optional - uncomment if you want to remove)
# echo "Removing virtual environments..."
# find . -type d -name ".venv" -o -name "venv" -o -name "ENV" -o -name "env" | xargs rm -r 2>/dev/null

# Remove Node modules (optional - uncomment if you want to remove)
# echo "Removing node_modules..."
# find . -type d -name "node_modules" | xargs rm -r 2>/dev/null

# Remove build directories
echo "Removing build directories..."
find . -type d -name "build" -o -name "dist" | xargs rm -r 2>/dev/null

# Remove IDE files
echo "Removing IDE files..."
find . -type d -name ".vscode" -o -name ".idea" | xargs rm -r 2>/dev/null
find . -type f -name "*.swp" -o -name "*.swo" -delete

# Remove OS files
echo "Removing OS files..."
find . -type f -name ".DS_Store" -delete
find . -type f -name "Thumbs.db" -delete
find . -type f -name "desktop.ini" -delete

# Remove log files
echo "Removing log files..."
find . -type f -name "*.log" -delete

# Remove temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -o -name "*.temp" -delete

echo "Cleanup complete!"

