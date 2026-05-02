@echo off

:: Run pipeline first
echo Running pipeline...
python code/pipeline/run_pipeline.py
if %errorlevel% neq 0 (
    echo Pipeline failed. Exiting.
    exit /b 1
)
echo Pipeline complete.

@REM :: Start backend in a new window
@REM start /b python code/backend/app.py

@REM :: Start frontend
@REM cd code/frontend
@REM npm run dev