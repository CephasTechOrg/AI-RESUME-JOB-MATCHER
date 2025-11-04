#!/usr/bin/env bash
set -e

echo "Starting setup for Render Free Plan (simple mode)..."

# 1. Install compatible Python version via pyenv
PYTHON_VERSION="3.11.8"
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION\$"; then
    pyenv install $PYTHON_VERSION
fi
pyenv global $PYTHON_VERSION

# 2. Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# 3. Install all dependencies globally
pip install fastapi==0.104.1 uvicorn==0.23.2 python-multipart==0.0.6 \
            PyPDF2==3.0.1 python-docx==0.8.11 requests==2.31.0 \
            pydantic==2.5.3 python-dotenv==1.0.0

echo "Setup complete. Python version: $(python --version)"
echo "uvicorn location: $(which uvicorn)"

# 4. Start the app directly (Render will run this)
uvicorn main:app --host 0.0.0.0 --port 10000
