@echo off

:: Run pipeline first
echo Running pipeline...
python code/pipeline/run_pipeline.py
if %errorlevel% neq 0 (
    echo Pipeline failed. Exiting.
    exit /b 1
)
echo Pipeline complete.

:: Start backend in a new window
start /b python code/backend/app.py

:: Start frontend
cd code/frontend
npm run dev