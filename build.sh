#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> [Mezzold Studio] Starting build for WebArchiver Pro..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright chromium browser
echo "==> Installing Playwright Chromium browser..."
playwright install chromium || true

# If static assets need to be refreshed from frontend
if [ -d "frontend" ] && [ ! -d "backend/static/_next" ]; then
  echo "==> Building frontend..."
  cd frontend
  npm install
  npm run build
  cd ..
  mkdir -p backend/static
  cp -r frontend/out/* backend/static/
fi

echo "==> [Mezzold Studio] Build finished successfully!"
