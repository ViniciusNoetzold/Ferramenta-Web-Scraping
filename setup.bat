@echo off
echo ===================================================
echo   Instalador WebArchiver Pro (Windows)
echo ===================================================
echo.

echo [1/4] Configurando Backend (Python)...
cd backend
if not exist venv (
    echo Criando ambiente virtual Python...
    python -m venv venv
)
call venv\Scripts\activate
echo Instalando dependencias do Python...
pip install -r requirements.txt

echo.
echo [2/4] Instalando navegador base do Playwright...
playwright install chromium

echo.
echo [3/4] Verificando arquivo .env...
if not exist .env (
    echo Criando arquivo .env padrao...
    copy .env.example .env
    echo [AVISO] Lembre-se de colocar suas chaves da Groq e NVIDIA no arquivo backend/.env!
) else (
    echo Arquivo .env ja existe.
)

echo.
echo [4/4] Configurando Frontend (Node.js)...
cd ..\frontend
echo Instalando dependencias do Node...
call npm install

echo.
echo ===================================================
echo   Instalacao Concluida!
echo ===================================================
echo Para rodar o projeto no futuro, abra dois terminais:
echo.
echo Terminal 1 (Backend):
echo cd backend ^& venv\Scripts\activate ^& python run.py
echo.
echo Terminal 2 (Frontend):
echo cd frontend ^& npm run dev
echo ===================================================
pause
