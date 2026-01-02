# Cleanup script for Windows PowerShell
# Removes unnecessary files and cache directories

Write-Host "Cleaning up project files..." -ForegroundColor Green

# Remove Python cache
Write-Host "Removing Python cache files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include *.pyc -Recurse -Force | Remove-Item -Force
Get-ChildItem -Path . -Include *.pyo -Recurse -Force | Remove-Item -Force

# Remove virtual environment (optional - uncomment if you want to remove)
# Write-Host "Removing virtual environments..." -ForegroundColor Yellow
# Get-ChildItem -Path . -Include .venv,venv,ENV,env -Recurse -Force -Directory | Remove-Item -Recurse -Force

# Remove Node modules (optional - uncomment if you want to remove)
# Write-Host "Removing node_modules..." -ForegroundColor Yellow
# Get-ChildItem -Path . -Include node_modules -Recurse -Force -Directory | Remove-Item -Recurse -Force

# Remove build directories
Write-Host "Removing build directories..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include build,dist -Recurse -Force -Directory | Remove-Item -Recurse -Force

# Remove IDE files
Write-Host "Removing IDE files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include .vscode,.idea -Recurse -Force -Directory | Remove-Item -Recurse -Force
Get-ChildItem -Path . -Include *.swp,*.swo -Recurse -Force | Remove-Item -Force

# Remove OS files
Write-Host "Removing OS files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include .DS_Store,Thumbs.db,desktop.ini -Recurse -Force | Remove-Item -Force

# Remove log files
Write-Host "Removing log files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include *.log -Recurse -Force | Remove-Item -Force

# Remove temporary files
Write-Host "Removing temporary files..." -ForegroundColor Yellow
Get-ChildItem -Path . -Include *.tmp,*.temp -Recurse -Force | Remove-Item -Force

Write-Host "Cleanup complete!" -ForegroundColor Green

