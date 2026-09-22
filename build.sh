#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> [Mezzold Studio] Starting build for WebArchiver Pro..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright chromium browser
echo "==> Installing Playwright Chromium browser..."
playwright install chromium || true

# If frontend directory and npm are available, compile frontend
if [ -d "frontend" ] && command -v npm &> /dev/null; then
  echo "==> Building frontend..."
  cd frontend
  npm install
  npm run build
  cd ..
  mkdir -p backend/static
  cp -r frontend/out/* backend/static/
fi

echo "==> [Mezzold Studio] Build finished successfully!"
