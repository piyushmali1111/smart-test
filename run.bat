@echo off
echo ========================================================
echo Starting Smart Test Selection (Sem-5 DAA Project)
echo ========================================================

echo Starting FastAPI Backend on port 8001...
start "SmartTest Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python -m uvicorn smarttest.api.main:app --host 127.0.0.1 --port 8001"

timeout /t 2 /nobreak >nul

echo Starting Vite React Frontend on port 5173...
start "SmartTest Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo Opening browser at http://localhost:5173...
start http://localhost:5173

echo.
echo Both servers are running!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8001/docs
echo ========================================================
pause
