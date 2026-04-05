@echo off

:: Start backend in a new window
start "Backend" python code/backend/app.py

:: Start frontend (Vite will print the localhost link)
cd code/frontend
npm run dev