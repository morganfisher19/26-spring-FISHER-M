@echo off

:: Run pipeline first
@REM echo Running pipeline...
@REM python code/pipeline/run_pipeline.py
@REM if %errorlevel% neq 0 (
@REM     echo Pipeline failed. Exiting.
@REM     exit /b 1
@REM )
@REM echo Pipeline complete.

:: Start backend in a new window
start /b python code/backend/app.py

:: Start frontend
cd code/frontend
npm run dev