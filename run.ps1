Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Smart Test Selection (Sem-5 DAA Project)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

Write-Host "Starting FastAPI Backend on port 8001..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .\.venv\Scripts\python -m uvicorn smarttest.api.main:app --host 127.0.0.1 --port 8001"

Start-Sleep -Seconds 2

Write-Host "Starting Vite React Frontend on port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Start-Sleep -Seconds 2

Write-Host "Opening browser at http://localhost:5173..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"

Write-Host "`nBoth servers are running!" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Backend:  http://localhost:8001/docs" -ForegroundColor White
